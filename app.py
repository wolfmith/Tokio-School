from tkinter import ttk, LabelFrame, Label, Entry, Toplevel, StringVar, W, E, CENTER, END, Tk
import sqlite3

# Style
button_font = ('Calibri', 14, 'bold')
table_font = ('Calibri', 11)
label_font = ('Calibri', 13)
title_font = ('Calibri', 16, 'bold')


def isfloat(str):
    try:
        float(str)
    except ValueError:
        return False
    return True


def create_label_entry(frame, label_text, row, column, entry_textvar=None, readonly=False):
    label = Label(frame, text=label_text, font=label_font)
    label.grid(row=row, column=column, padx=(10, 5), pady=5, sticky='e')

    if readonly:
        entry = Entry(frame, textvariable=entry_textvar, font=label_font, state='readonly')
    else:
        entry = Entry(frame, textvariable=entry_textvar, font=label_font)

    entry.grid(row=row, column=column + 1, padx=(5, 10), pady=5, sticky='w')

    # Configure column and row to expand equally
    frame.grid_columnconfigure(column, weight=1)
    frame.grid_columnconfigure(column + 1, weight=1)
    frame.grid_rowconfigure(row, weight=0)

    return entry


# Configure SQLAlchemy to work with SQLite
engine = create_engine('sqlite:///database/produtos.db', echo=True)
Base = declarative_base()


class Product(Base):
    __tablename__ = 'produto'
    id = Column(Integer, primary_key=True)
    nome = Column(String)
    preço = Column(Float)


class Produto:
    """
    Classe que representa a aplicação de gestão de produtos.
    """
    db = 'database/produtos.db' # Path to the SQLite database file.

    def __init__(self, root):
        """
        Initialize the product management application.

        Args:
            root: The Tkinter root window.
        """
        self.janela = root
        self.janela.title("App Gestor de Produtos")  # Set the window title.
        self.janela.resizable(1, 1)  # Allow window resizing.
        self.janela.grid_rowconfigure(0, weight=1)  # Make the row expand with resizing
        self.janela.grid_columnconfigure(0, weight=1)  # Make the column expand with resizing
        self.janela.grid_columnconfigure(1, weight=1)
        self.janela.wm_iconbitmap('recursos/icon.ico')  # Set the window icon.

        # Create the main LabelFrame container.
        frame = LabelFrame(self.janela, text="Registar um novo Produto", font=title_font, labelanchor='n')
        frame.grid(row=0, column=0, columnspan=3, pady=5, padx = 50, sticky="nsew")
        frame.grid_rowconfigure(0, weight=0)  # Make the row expand with resizing

        # Label and Entry for Nome
        self.nome = create_label_entry(frame, "Nome: ", 1, 0)
        self.nome.focus()  # Para que o foco do rato vá a esta Entry no início

        # Label and Entry for Preço
        self.preço = create_label_entry(frame, "Preço: ", 2, 0)

        # Botão Adicionar Produto
        s = ttk.Style()
        s.configure('my.TButton', font=button_font)
        self.botao_adicionar = ttk.Button(frame, text="Guardar Produto", command=self.add_produto, style='my.TButton')
        self.botao_adicionar.grid(row=3, columnspan=2, sticky="nsew")
        # Mensagem informativa para o utilizador
        self.mensagem = Label(text='', fg='red')
        self.mensagem.grid(row=3, column=0, columnspan=2, sticky="nsew")
        # Tabela de Produtos
        # Estilo personalizado para a tabela
        style = ttk.Style()
        # Modifica-se a fonte da tabela
        style.configure("mystyle.Treeview", highlightthickness=0, bd=0, font=table_font)
        # Modifica-se a fonte das cabeceiras
        style.configure("mystyle.Treeview.Heading", font=title_font)
        # Eliminar as bordas
        style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])
        # Estrutura da tabela
        self.tabela = ttk.Treeview(height=20, columns=2, style="mystyle.Treeview")
        self.tabela.grid(row=4, column=0, columnspan=2, sticky="nsew")
        self.tabela.grid_columnconfigure(0, weight=1)  # Make the column expand with resizing
        self.tabela.grid_columnconfigure(1, weight=1)  # Make the column expand with resizing
        self.tabela.grid_rowconfigure(0, weight=1)  # Make the row expand with resizing
        self.janela.bind("<Configure>", lambda event: self.tabela.configure(height=(self.janela.winfo_height()-200) // 22))
        self.tabela.heading('#0', text='Nome', anchor=CENTER)  # Cabeçalho 0
        self.tabela.heading('#1', text='Preço', anchor=CENTER)  # Cabeçalho 1
        # Create a vertical scrollbar
        y_scrollbar = ttk.Scrollbar(self.janela, orient="vertical", command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=y_scrollbar.set)
        y_scrollbar.grid(row=4, column=3, sticky="ns")
        self.get_produtos()  # Chamada ao método get_produtos() para obter a listagem de produtos ao início da app

        # Botões de Eliminar e Editar
        botão_eliminar = ttk.Button(text='ELIMINAR', command=self.del_produto, style='my.TButton')
        botão_eliminar.grid(row=5, column=0, padx=5, pady=5, sticky=W + E)  # Stick to the left side

        botão_editar = ttk.Button(text='EDITAR', command=self.edit_produto, style='my.TButton')
        botão_editar.grid(row=5, column=1, padx=5, pady=5, sticky=W + E)  # Stick to the right side

    def db_consulta(self, consulta, parametros=()):
        """
        Execute a database query and return the result.

        Args:
            consulta (str): The SQL query to execute.
            parametros (tuple): The parameters to be used in the query, if any.

        Returns:
            sqlite3.Cursor: The result of the executed query.

        This function executes the provided SQL query with the given parameters on the connected database.

        """
        with sqlite3.connect(self.db) as con:  # Iniciamos uma conexão com a base de dados (alias con)
            cursor = con.cursor()  # Criamos um cursor da conexão para poder operar na base de dados
            resultado = cursor.execute(consulta, parametros)  # Preparar a consulta SQL (com parâmetros se os há)
            con.commit()  # Executar a consulta SQL preparada anteriormente
        return resultado  # Restituir o resultado da consulta SQL

    def get_produtos(self):
        """
        Retrieve and display a list of products in a tkinter Treeview.

        This function retrieves a list of products from a database and displays them in a tkinter Treeview widget.
        If a product is already present in the Treeview, it updates the existing record; otherwise, it inserts a new record.

        The function performs the following tasks:
        1. Retrieves the current records displayed in the Treeview.
        2. Retrieves product information from the database.
        3. Compares each retrieved product with the existing records in the Treeview.
        4. Updates existing records or inserts new records accordingly.

        Returns:
            None

        """
        registos_tabela = self.tabela.get_children()  # Obter todos os dados da tabela
        query = 'SELECT * FROM produto ORDER BY nome DESC'  # Consulta SQL
        registos_db = self.db_consulta(query)  # Faz-se a chamada ao método db_consultas

        # Escrever os dados no ecrã
        for linha in registos_db:
            # Check if the record already exists in the table
            record_exists = False
            for child in registos_tabela:
                if self.tabela.item(child)['tags'][0] == linha[0]:
                    self.tabela.item(child, text=linha[1], values=linha[2], tags=(linha[0],))
                    record_exists = True
                    break

            if not record_exists:
                self.tabela.insert('', 0, text=linha[1], values=linha[2], tags=(linha[0],))

    def validacao_nome(self):
        nome_introduzido = self.nome.get()
        return len(nome_introduzido) != 0

    def validacao_preço(self):
        preço_introduzido = self.preço.get()
        return len(preço_introduzido) != 0 and isfloat(preço_introduzido)

    def add_produto(self):
        """
        Adds a new product to the database.

        This function adds a new product to the database, provided that both the name and the price fields pass their
        respective validation checks.
        It first constructs the SQL query and the corresponding parameters, then executes the query.
        If either the name or the price fails validation, it displays an appropriate error message.

        The function performs the following tasks:
        1. Validates the product name and price.
        2. Constructs and executes the SQL query for inserting a new product into the database.
        3. Displays a success message if the product is added successfully.
        4. Displays an error message if the name, price, or both are not valid.
        5. Calls the 'get_produtos' method to update the view with the latest changes.

        Returns:
            None

        """
        if self.validacao_nome() and self.validacao_preço():
            query = 'INSERT INTO produto VALUES(NULL, ?, ?)'  # Consulta SQL (sem os dados)
            parametros = (
            self.nome.get(), format(float(self.preço.get()), '.2f'))  # Parâmetros da consulta SQL (preço arredondado)
            self.db_consulta(query, parametros)
            self.mensagem['text'] = 'Produto {} adicionado com êxito'.format(
                self.nome.get())  # Label localizada entre o botão e a tabela
            self.nome.delete(0, END)  # Apagar o campo nome do formulário
            self.preço.delete(0, END)  # Apagar o campo preço do formulário
        elif self.validacao_nome() and self.validacao_preço() == False:
            self.mensagem['text'] = 'Um preço válido é obrigatório'
        elif self.validacao_nome() == False and self.validacao_preço():
            self.mensagem['text'] = 'Um nome é obrigatório'
        else:
            self.mensagem['text'] = 'O nome e o preço são obrigatórios'
        # Após inserir os dados, atualize o método para ver as alterações
        self.get_produtos()

    def del_produto(self):
        """
        Deletes a selected product from the database.

        This function deletes a product from the database based on the user's selection from the view. If no product is selected, it displays an appropriate error message.

        The function performs the following tasks:
        1. Validates the selection of a product for deletion.
        2. Retrieves the ID and name of the selected item.
        3. Constructs and executes the SQL query for deleting the selected product from the database.
        4. Displays a success message if the product is deleted successfully.
        5. Calls the 'get_produtos' method to update the view with the latest changes.

        Returns:
            None

        """
        self.mensagem['text'] = ''
        selected_item = self.tabela.selection()
        if selected_item:
            nome = self.tabela.item(selected_item)['text']
            id_produto = self.tabela.item(selected_item)['tags'][0]
        else:
            self.mensagem['text'] = 'Por favor, selecione um produto'
            return
        # Delete the item based on its ID
        query = 'DELETE FROM produto WHERE id = ?'
        self.db_consulta(query, (id_produto,))
        self.mensagem['text'] = 'Produto {} eliminado com êxito'.format(nome)
        self.get_produtos()  # Update the table

    def edit_produto(self):
        """
        Opens a new window to edit the selected product.

        This function enables the user to edit a selected product by opening a new window. If no product is selected,
        it displays an appropriate error message.

        The function performs the following tasks:
        1. Validates the selection of a product for editing.
        2. Retrieves the ID, name, and price of the selected item.
        3. Creates a new window for editing the selected product and positions it relative to the main window.
        4. Creates a frame within the new window to contain the editing elements.
        5. Provides fields for entering the old and new product names and prices.
        6. Includes a button for updating the product information.

        Returns:
            None

        """
        self.mensagem['text'] = ''  # Mensagem inicialmente vazia
        # Comprovação de que se selecione um produto para poder eliminá-lo
        selected_item = self.tabela.selection()
        # Get the ID and name of the selected item
        if selected_item:
            nome = self.tabela.item(selected_item)['text']
            id_produto = self.tabela.item(selected_item)['tags'][0]
        else:
            self.mensagem['text'] = 'Por favor, selecione um produto'
            return
        old_preço = self.tabela.item(self.tabela.selection())['values'][0]  # O preço encontra-se dentro de uma lista

        self.janela_editar = Toplevel()  # Criar uma janela à frente da principal
        self.janela_editar.title = "Editar Produto"  # Titulo da janela
        self.janela_editar.resizable(0, 0)  # Ativar a redimensão da janela. Para desativá-la: (0,0)
        self.janela_editar.wm_iconbitmap('recursos/icon.ico')  # Ícone da janela
        # Get the size and position of the main window
        x, y = self.janela.winfo_x(), self.janela.winfo_y()
        width, height = self.janela.winfo_width(), self.janela.winfo_height()
        # Position the new window relative to the main window
        self.janela_editar.geometry("+{}+{}".format(x + round(width/4), y + round(height/2)))

        # Criação do recipiente Frame da janela de Editar Produto
        frame_ep = LabelFrame(self.janela_editar, text="Editar o seguinte Produto", font=title_font)  # frame_ep: Frame Editar Produto
        frame_ep.grid(row=1, column=0, columnspan=20, pady=20)
        # Label and Entry for Nome antigo
        self.input_nome_antigo = create_label_entry(frame_ep, "Nome antigo: ", 2, 0,
                                                    StringVar(self.janela_editar, value=nome), readonly=True)

        # Label and Entry for Nome novo
        self.input_nome_novo = create_label_entry(frame_ep, "Nome novo: ", 3, 0)
        self.input_nome_novo.focus()

        # Label and Entry for Preço antigo
        self.input_preço_antigo = create_label_entry(frame_ep, "Preço antigo: ", 4, 0,
                                                     StringVar(self.janela_editar, value=old_preço), readonly=True)

        # Label and Entry for Preço novo
        self.input_preço_novo = create_label_entry(frame_ep, "Preço novo: ", 5, 0)

        # Botão Atualizar Produto
        self.botão_atualizar = ttk.Button(frame_ep, text="Atualizar Produto", style='my.TButton', command=lambda:
                                          self.atualizar_produtos(self.input_nome_novo.get(),
                                                                  self.input_nome_antigo.get(),
                                                                  self.input_preço_novo.get(),
                                                                  self.input_preço_antigo.get(), id_produto))
        self.botão_atualizar.grid(row=6, columnspan=2, sticky=W + E)

    def atualizar_produtos(self, novo_nome, antigo_nome, novo_preço, antigo_preço, id_produto):
        """
        Update the product information based on the user's input.

        This function allows the user to update product information based on the provided input.
        It checks whether the new name or price is provided or not and executes the corresponding database update query.

        Args:
            novo_nome (str): The new name of the product.
            antigo_nome (str): The old name of the product.
            novo_preço (str): The new price of the product.
            antigo_preço (str): The old price of the product.
            id_produto (int): The ID of the product.

        Returns:
            None

        """
        produto_modificado = False
        query = 'UPDATE produto SET nome = ?, preço = ? WHERE id = ?'
        if novo_nome != '' and (novo_preço != '' and isfloat(novo_preço)) :
            # Se o utilizador escreve novo nome e novo preço, mudam-se ambos
            parametros = (novo_nome, format(float(novo_preço), '.2f'), id_produto)
            produto_modificado = True
        elif novo_nome != '' and (novo_preço == '' or isfloat(novo_preço)):
            # Se o utilizador deixa vazio o novo preço, mantém-se o preço anterior
            parametros = (novo_nome, antigo_preço, id_produto)
            produto_modificado = True
        elif novo_nome == '' and (novo_preço != '' and isfloat(novo_preço)):
            # Se o utilizador deixa vazio o novo nome, mantém-se o nome anterior
            parametros = (antigo_nome, format(float(novo_preço), '.2f'), id_produto)
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
