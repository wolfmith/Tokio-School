from tkinter import ttk, LabelFrame, Label, Entry, Toplevel, StringVar, W, E, CENTER, END, Tk
import sqlite3


class Produto:
    """
    Classe que representa a aplicação de gestão de produtos.
    """

    db = 'database/produtos.db'

    def __init__(self, root):
        """
        Inicializa a janela principal e cria a interface da aplicação.

        Args:
            root: A janela principal da aplicação.
        """
        self.janela = root
        self.janela.title("App Gestor de Produtos")  # Título da janela
        self.janela.resizable(0, 0)  # Desativar o redimensionamento da janela
        self.janela.wm_iconbitmap('recursos/icon.ico')

        # Criação do recipiente Frame principal
        frame = LabelFrame(self.janela, text="Registar um novo Produto")
        frame.grid(row=0, column=0, columnspan=3, pady=20)

        # Label Nome
        self.etiqueta_nome = Label(frame, text="Nome: ")
        self.etiqueta_nome.grid(row=1, column=0)

        # Entry Nome
        self.nome = Entry(frame)
        self.nome.focus()
        self.nome.grid(row=1, column=1)

        # Label Preço
        self.etiqueta_preço = Label(frame, text="Preço: ")
        self.etiqueta_preço.grid(row=2, column=0)

        # Entry Preço
        self.preço = Entry(frame)
        self.preço.grid(row=2, column=1)

        # Botão Adicionar Produto
        self.botao_adicionar = ttk.Button(frame, text="Guardar Produto", command=self.add_produto)
        self.botao_adicionar.grid(row=3, columnspan=2, sticky=W + E)

        # Mensagem informativa para o utilizador
        self.mensagem = Label(text='', fg='red')
        self.mensagem.grid(row=3, column=0, columnspan=2, sticky=W + E)

        # Tabela de Produtos
        # Estilo personalizado para a tabela
        style = ttk.Style()
        style.configure("mystyle.Treeview", highlightthickness=0, bd=0, font=('Calibri', 11))
        style.configure("mystyle.Treeview.Heading", font=('Calibri', 13, 'bold'))
        style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])

        # Estrutura da tabela
        self.tabela = ttk.Treeview(height=20, columns=2, style="mystyle.Treeview")
        self.tabela.grid(row=4, column=0, columnspan=2)
        self.tabela.heading('#0', text='Nome', anchor=CENTER)
        self.tabela.heading('#1', text='Preço', anchor=CENTER)
        self.get_produtos()

        # Botões de Eliminar e Editar
        botão_eliminar = ttk.Button(text='ELIMINAR', command=self.del_produto)
        botão_eliminar.grid(row=5, column=0, sticky=W + E)
        botão_editar = ttk.Button(text='EDITAR', command=self.edit_produto)
        botão_editar.grid(row=5, column=1, sticky=W + E)

    def db_consulta(self, consulta, parametros=()):
        """
        Executa uma consulta à base de dados.

        Args:
            consulta: A consulta SQL a ser executada.
            parametros: Parâmetros opcionais para a consulta.

        Returns:
            O resultado da consulta.
        """
        with sqlite3.connect(self.db) as con:
            cursor = con.cursor()
            resultado = cursor.execute(consulta, parametros)
            con.commit()
        return resultado

    def get_produtos(self):
        """
        Obtém e exibe os produtos na tabela.
        """
        # Limpa a tabela se houver dados antigos
        registos_tabela = self.tabela.get_children()
        for linha in registos_tabela:
            self.tabela.delete(linha)

        # Consulta SQL
        query = 'SELECT * FROM produto ORDER BY nome DESC'
        registos_db = self.db_consulta(query)

        # Preenche a tabela com os dados
        for linha in registos_db:
            self.tabela.insert('', 0, text=linha[1], values=linha[2])

    def validacao_nome(self):
        """
        Validação do campo Nome.

        Returns:
            True se o campo Nome é válido, False caso contrário.
        """
        nome_introduzido_por_utilizador = self.nome.get()
        return len(nome_introduzido_por_utilizador) != 0

    def validacao_preço(self):
        """
        Validação do campo Preço.

        Returns:
            True se o campo Preço é válido, False caso contrário.
        """
        preço_introduzido_por_utilizador = self.preço.get()
        return len(preço_introduzido_por_utilizador) != 0

    def add_produto(self):
        """
        Adiciona um novo produto à base de dados.
        """
        if self.validacao_nome() and self.validacao_preço():
            query = 'INSERT INTO produto VALUES(NULL, ?, ?)'
            parametros = (self.nome.get(), self.preço.get())
            self.db_consulta(query, parametros)
            self.mensagem['text'] = 'Produto {} adicionado com êxito'.format(self.nome.get())
            self.nome.delete(0, END)
            self.preço.delete(0, END)
            self.get_produtos()
        elif self.validacao_nome() and self.validacao_preço() == False:
            self.mensagem['text'] = 'O preço é obrigatório'
        elif self.validacao_nome() == False and self.validacao_preço():
            self.mensagem['text'] = 'O nome é obrigatório'
        else:
            self.mensagem['text'] = 'O nome e o preço são obrigatórios'
        self.get_produtos()

    def del_produto(self):
        """
        Elimina um produto da base de dados.
        """
        self.mensagem['text'] = ''
        try:
            self.tabela.item(self.tabela.selection())['text'][0]
        except IndexError as e:
            self.mensagem['text'] = 'Por favor, selecione um produto'
            return

        self.mensagem['text'] = ''
        nome = self.tabela.item(self.tabela.selection())['text']
        query = 'DELETE FROM produto WHERE nome = ?'
        self.db_consulta(query, (nome,))
        self.mensagem['text'] = 'Produto {} eliminado com êxito'.format(nome)
        self.get_produtos()

    def edit_produto(self):
        """
        Abre uma janela de edição de produto.
        """
        self.mensagem['text'] = ''
        try:
            self.tabela.item(self.tabela.selection())['text'][0]
        except IndexError as e:
            self.mensagem['text'] = 'Por favor, selecione um produto'
            return

        nome = self.tabela.item(self.tabela.selection())['text']
        old_preço = self.tabela.item(self.tabela.selection())['values'][0]

        self.janela_editar = Toplevel()
        self.janela_editar.title = "Editar Produto"
        self.janela_editar.resizable(1, 1)
        self.janela_editar.wm_iconbitmap('recursos/icon.ico')

        título = Label(self.janela_editar, text='Edição de Produtos', font=('Calibri', 50, 'bold'))
        título.grid(column=0, row=0)

        frame_ep = LabelFrame(self.janela_editar, text="Editar o seguinte Produto")
        frame_ep.grid(row=1, column=0, columnspan=20, pady=20)

        self.etiqueta_nome_antigo = Label(frame_ep, text="Nome antigo: ")
        self.etiqueta_nome_antigo.grid(row=2, column=0)

        self.input_nome_antigo = Entry(frame_ep, textvariable=StringVar(self.janela_editar, value=nome),
                                       state='readonly')
        self.input_nome_antigo.grid(row=2, column=1)

        self.etiqueta_nome_novo = Label(frame_ep, text="Nome novo: ")
        self.etiqueta_nome_novo.grid(row=3, column=0)

        self.input_nome_novo = Entry(frame_ep)
        self.input_nome_novo.grid(row=3, column=1)
        self.input_nome_novo.focus()

        self.etiqueta_preço_antigo = Label(frame_ep, text="Preço antigo: ")
        self.etiqueta_preço_antigo.grid(row=4, column=0)

        self.input_preço_antigo = Entry(frame_ep, textvariable=StringVar(self.janela_editar, value=old_preço),
                                        state='readonly')
        self.input_preço_antigo.grid(row=4, column=1)

        self.etiqueta_preço_novo = Label(frame_ep, text="Preço novo: ")
        self.etiqueta_preço_novo.grid(row=5, column=0)

        self.input_preço_novo = Entry(frame_ep)
        self.input_preço_novo.grid(row=5, column=1)

        self.botão_atualizar = ttk.Button(frame_ep, text="Atualizar Produto", command=lambda:
        self.atualizar_produtos(self.input_nome_novo.get(), self.input_nome_antigo.get(),
                                self.input_preço_novo.get(), self.input_preço_antigo.get()))
        self.botão_atualizar.grid(row=6, columnspan=2, sticky=W + E)

    def atualizar_produtos(self, novo_nome, antigo_nome, novo_preço, antigo_preço):
        """
        Atualiza um produto na base de dados.

        Args:
            novo_nome: O novo nome do produto.
            antigo_nome: O nome antigo do produto.
            novo_preço: O novo preço do produto.
            antigo_preço: O preço antigo do produto.
        """
        produto_modificado = False
        query = 'UPDATE produto SET nome = ?, preço = ? WHERE nome = ? AND preço = ?'
        if novo_nome != '' and novo_preço != '':
            parametros = (novo_nome, novo_preço, antigo_nome, antigo_preço)
            produto_modificado = True
        elif novo_nome != '' and novo_preço == '':
            parametros = (novo_nome, antigo_preço, antigo_nome, antigo_preço)
            produto_modificado = True
        elif novo_nome == '' and novo_preço != '':
            parametros = (antigo_nome, novo_preço, antigo_nome, antigo_preço)
            produto_modificado = True

        if (produto_modificado):
            self.db_consulta(query, parametros)
            self.janela_editar.destroy()
            self.mensagem['text'] = 'O produto {} foi atualizado com êxito'.format(antigo_nome)
            self.get_produtos()
        else:
            self.janela_editar.destroy()
            self.mensagem['text'] = 'O produto {} NÃO foi atualizado'.format(antigo_nome)


if __name__ == '__main__':
    root = Tk()
    app = Produto(root)
    root.mainloop()
