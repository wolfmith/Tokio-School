from tkinter import ttk
from tkinter import *
import sqlite3


class Produto:
    db = 'database/produtos.db'

    def __init__(self, root):
        self.janela = root
        self.janela.title("App Gestor de Produtos")  # Título da janela
        self.janela.resizable(1, 1)  # Ativar a redimensionamento da janela. Para desativá-la: (0,0)
        # root.geometry("500x300")  # Width x Height
        self.janela.wm_iconbitmap('recursos/icon.ico')
        # Criação do recipiente Frame principal
        frame = LabelFrame(self.janela, text="Registar um novo Produto")
        frame.grid(row=0, column=0, columnspan=3, pady=20)
        # Label Nome
        self.etiqueta_nome = Label(frame, text="Nome: ")  # Etiqueta de texto localizada no frame
        self.etiqueta_nome.grid(row=1, column=0)  # Posicionamento através de grid
        # Entry Nome (caixa de texto que irá receber o nome)
        self.nome = Entry(frame)  # Caixa de texto (input de texto) localizada no frame
        self.nome.focus()  # Para que o foco do rato vá a esta Entry no início
        self.nome.grid(row=1, column=1)
        # Label Preço
        self.etiqueta_preço = Label(frame, text="Preço: ")  # Etiqueta de texto localizada no frame
        self.etiqueta_preço.grid(row=2, column=0)  # Entry Preço (caixa de texto que irá receber o preço)
        self.preço = Entry(frame)  # Caixa de texto (input de texto) localizada no frame
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
        # Modifica-se a fonte da tabela
        style.configure("mystyle.Treeview", highlightthickness=0, bd=0, font=('Calibri', 11))
        # Modifica-se a fonte das cabeceiras
        style.configure("mystyle.Treeview.Heading", font=('Calibri', 13, 'bold'))
        # Eliminar as bordas
        style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])
        # Estrutura da tabela
        self.tabela = ttk.Treeview(height=20, columns=2, style="mystyle.Treeview")
        self.tabela.grid(row=4, column=0, columnspan=2)
        self.tabela.heading('#0', text='Nome', anchor=CENTER)  # Cabeçalho 0
        self.tabela.heading('#1', text='Preço', anchor=CENTER)  # Cabeçalho 1
        self.get_produtos()  # Chamada ao método get_produtos() para obter a listagem de produtos ao início da app
        # Botões de Eliminar e Editar
        botão_eliminar = ttk.Button(text='ELIMINAR', command=self.del_produto)
        botão_eliminar.grid(row=5, column=0, sticky=W + E)
        botão_editar = ttk.Button(text='EDITAR', command=self.edit_produto)
        botão_editar.grid(row=5, column=1, sticky=W + E)

    def db_consulta(self, consulta, parametros=()):
        with sqlite3.connect(self.db) as con:  # Iniciamos uma conexão com a base de dados (alias con)
            cursor = con.cursor()  # Criamos um cursor da conexão para poder operar na base de dados
            resultado = cursor.execute(consulta, parametros)  # Preparar a consulta SQL (com parâmetros se os há)
            con.commit()  # Executar a consulta SQL preparada anteriormente
        return resultado  # Restituir o resultado da consulta SQL

    def get_produtos(self):
        # O primeiro, ao iniciar a app, vamos limpar a tabela se tiver dados residuais ou antigos
        registos_tabela = self.tabela.get_children()  # Obter todos os dados da tabela
        for linha in registos_tabela:
            self.tabela.delete(linha)

        # Consulta SQL
        query = 'SELECT * FROM produto ORDER BY nome DESC'
        registos_db = self.db_consulta(query)  # Faz-se a chamada ao método db_consultas

        # Escrever os dados no ecrã
        for linha in registos_db:
            print(linha)  # print para verificar por consola os dados
            self.tabela.insert('', 0, text=linha[1], values=linha[2])

    def validacao_nome(self):
        nome_introduzido_por_utilizador = self.nome.get()
        return len(nome_introduzido_por_utilizador) != 0

    def validacao_preço(self):
        preço_introduzido_por_utilizador = self.preço.get()
        return len(preço_introduzido_por_utilizador) != 0

    def add_produto(self):
        if self.validacao_nome() and self.validacao_preço():
            query = 'INSERT INTO produto VALUES(NULL, ?, ?)'  # Consulta SQL (sem os dados)
            parametros = (self.nome.get(), self.preço.get())  # Parâmetros da consulta SQL
            self.db_consulta(query, parametros)
            self.mensagem['text'] = 'Produto {} adicionado com êxito'.format(
                self.nome.get())  # Label localizada entre o botão e a tabela
            self.nome.delete(0, END)  # Apagar o campo nome do formulário
            self.preço.delete(0, END)  # Apagar o campo preço do formulário

            # Para debug
            # print(self.nome.get())
            # print(self.preço.get())
        elif self.validacao_nome() and self.validacao_preço() == False:
            print("O preço é obrigatório")
            self.mensagem['text'] = 'O preço é obrigatório'
        elif self.validacao_nome() == False and self.validacao_preço():
            print("O nome é obrigatório")
            self.mensagem['text'] = 'O nome é obrigatório'
        else:
            print("O nome e o preço são obrigatórios")
            self.mensagem['text'] = 'O nome e o preço são obrigatórios'
        # Após inserir os dados, atualize o método para ver as alterações
        self.get_produtos()

    def del_produto(self):
        # Debug
        # print(self.tabela.item(self.tabela.selection()))
        # print(self.tabela.item(self.tabela.selection())['text'])
        # print(self.tabela.item(self.tabela.selection())['values'])
        # print(self.tabela.item(self.tabela.selection())['values'][0])

        self.mensagem['text'] = ''  # Mensagem inicialmente vazio
        # Comprovação de que se selecione um produto para poder eliminá-lo
        try:
            self.tabela.item(self.tabela.selection())['text'][0]
        except IndexError as e:
            self.mensagem['text'] = 'Por favor, selecione um produto'
            return

        self.mensagem['text'] = ''
        nome = self.tabela.item(self.tabela.selection())['text']
        query = 'DELETE FROM produto WHERE nome = ?'  # Consulta SQL
        self.db_consulta(query, (nome,))  # Executar a consulta
        self.mensagem['text'] = 'Produto {} eliminado com êxito'.format(nome)
        self.get_produtos()  # Atualizar a tabela de produtos

    def edit_produto(self):
        self.mensagem['text'] = ''  # Mensagem inicialmente vazia
        try:
            self.tabela.item(self.tabela.selection())['text'][0]
        except IndexError as e:
            self.mensagem['text'] = 'Por favor, selecione um produto'
            return
        nome = self.tabela.item(self.tabela.selection())['text']
        old_preço = self.tabela.item(self.tabela.selection())['values'][0]  # O preço encontra-se dentro de uma lista

        self.janela_editar = Toplevel()  # Criar uma janela à frente da principal
        self.janela_editar.title = "Editar Produto"  # Titulo da janela
        self.janela_editar.resizable(1, 1)  # Ativar a redimensão da janela. Para desativá-la: (0,0)
        self.janela_editar.wm_iconbitmap('recursos/icon.ico')  # Ícone da janela
        título = Label(self.janela_editar, text='Edição de Produtos', font=('Calibri', 50, 'bold'))
        título.grid(column=0, row=0)
        # Criação do recipiente Frame da janela de Editar Produto
        frame_ep = LabelFrame(self.janela_editar, text="Editar o seguinte Produto")  # frame_ep: Frame Editar Produto
        frame_ep.grid(row=1, column=0, columnspan=20, pady=20)
        # Label Nome antigo
        self.etiqueta_nome_antigo = Label(frame_ep, text="Nome antigo: ")  # Etiqueta de texto localizada no frame
        self.etiqueta_nome_antigo.grid(row=2, column=0)  # Posicionamento através de grid
        # Entry Nome antigo (texto que não se poderá modificar)
        self.input_nome_antigo = Entry(frame_ep, textvariable=StringVar(self.janela_editar, value=nome),
                                       state='readonly')
        self.input_nome_antigo.grid(row=2, column=1)
        # Label Nome novo
        self.etiqueta_nome_novo = Label(frame_ep, text="Nome novo: ")
        self.etiqueta_nome_novo.grid(row=3, column=0)
        # Entry Nome novo (texto que se poderá modificar)
        self.input_nome_novo = Entry(frame_ep)
        self.input_nome_novo.grid(row=3, column=1)
        self.input_nome_novo.focus()  # Para que a seta do rato vá a esta Entry ao início
        # Label Preço antigo
        self.etiqueta_preço_antigo = Label(frame_ep, text="Preço antigo: ")  # Etiqueta de texto localizada no frame
        self.etiqueta_preço_antigo.grid(row=4, column=0)  # Posicionamento através de grid
        # Entry Preço antigo (texto que não se poderá modificar)
        self.input_preço_antigo = Entry(frame_ep, textvariable=StringVar(self.janela_editar, value=old_preço),
                                        state='readonly')
        self.input_preço_antigo.grid(row=4, column=1)
        # Label Preço novo
        self.etiqueta_preço_novo = Label(frame_ep, text="Preço novo: ")
        self.etiqueta_preço_novo.grid(row=5, column=0)
        # Entry Preço novo (texto que se poderá modificar)
        self.input_preço_novo = Entry(frame_ep)
        self.input_preço_novo.grid(row=5, column=1)
        # Botão Atualizar Produto
        self.botão_atualizar = ttk.Button(frame_ep, text="Atualizar Produto", command=lambda:
        self.atualizar_produtos(self.input_nome_novo.get(), self.input_nome_antigo.get(), self.input_preço_novo.get(),
                                self.input_preço_antigo.get()))
        self.botão_atualizar.grid(row=6, columnspan=2, sticky=W + E)

    def atualizar_produtos(self, novo_nome, antigo_nome, novo_preço, antigo_preço):
        produto_modificado = False
        query = 'UPDATE produto SET nome = ?, preço = ? WHERE nome = ? AND preço = ?'
        if novo_nome != '' and novo_preço != '':
            # Se o utilizador escreve novo nome e novo preço, mudam-se ambos
            parametros = (novo_nome, novo_preço, antigo_nome, antigo_preço)
            produto_modificado = True
        elif novo_nome != '' and novo_preço == '':
            # Se o utilizador deixa vazio o novo preço, mantém-se o preço anterior
            parametros = (novo_nome, antigo_preço, antigo_nome, antigo_preço)
            produto_modificado = True
        elif novo_nome == '' and novo_preço != '':
            # Se o utilizador deixa vazio o novo nome, mantém-se o nome anterior
            parametros = (antigo_nome, novo_preço, antigo_nome, antigo_preço)
            produto_modificado = True

        if (produto_modificado):
            self.db_consulta(query, parametros)  # Executar a consulta
            self.janela_editar.destroy()  # Fechar a janela de edição de produtos
            self.mensagem['text'] = 'O produto {} foi atualizado com êxito'.format(
                antigo_nome)  # Mostrar mensagem para o utilizador
            self.get_produtos()  # Atualizar a tabela de produtos
        else:
            self.janela_editar.destroy()  # Fechar a janela de edição de produtos
            self.mensagem['text'] = 'O produto {} NÃO foi atualizado'.format(
                antigo_nome)  # Mostrar mensagem para o utilizador


if __name__ == '__main__':
    root = Tk()  # Instância da janela principal
    app = Produto(root)
    root.mainloop()  # Começamos o ciclo de aplicação, é como um while True
