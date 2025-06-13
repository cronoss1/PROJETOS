# Versão com interface gráfica e histórico de equipamentos.

import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import os
import csv
import json
from tkinter import font as tkfont

class SistemaGerenciamentoEquipamentos:
    def __init__(self, root):
        # Configuração do caminho do banco de dados (mantido igual)
        self.DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'gerenciamento_equipamentos.db')
        os.makedirs(os.path.dirname(self.DB_PATH), exist_ok=True)
        
        self.root = root
        self.root.title("Sistema de Gerenciamento de Equipamentos")
        self.root.geometry("800x650")
        
        # Configuração de estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Tema mais moderno
        
         # Configurações de cores CORRIGIDAS (linhas 27-37)
        self.style.configure('.', background='#f0f0f0', font=('Segoe UI', 10))
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Segoe UI', 10))
        self.style.configure('TButton', font=('Segoe UI', 10), padding=5)
        self.style.configure('TEntry', padding=5)
        self.style.configure('TNotebook.Tab', padding=[10, 5], font=('Segoe UI', 10))
        
        # Cores personalizadas CORRIGIDAS
        self.style.configure('Card.TFrame', background='white', borderwidth=1, relief='solid')
        self.style.configure('Title.TLabel', font=('Segoe UI', 12, 'bold'))
        self.style.configure('Primary.TButton', background='#4a6baf', foreground='white')

        self.criar_banco_dados()
        self.criar_interface()
    
    def criar_banco_dados(self):
        conn = sqlite3.connect(self.DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS funcionarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            matricula TEXT NOT NULL UNIQUE
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS equipamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT NOT NULL UNIQUE,
            modelo TEXT NOT NULL,
            serial TEXT NOT NULL UNIQUE,
            status TEXT DEFAULT 'Disponível'
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS vinculos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            funcionario_id INTEGER NOT NULL,
            equipamento_id INTEGER NOT NULL,
            data_entrega TEXT NOT NULL,
            data_devolucao TEXT,
            FOREIGN KEY (funcionario_id) REFERENCES funcionarios(id),
            FOREIGN KEY (equipamento_id) REFERENCES equipamentos(id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def criar_interface(self):
        # Adicionar cabeçalho
        header = ttk.Frame(self.root, style='Card.TFrame', padding=10)
        header.pack(fill='x', padx=10, pady=10)
        
        title = ttk.Label(header, text="Sistema de Gerenciamento de Equipamentos", 
                        font=('Segoe UI', 14, 'bold'))
        title.pack()
        
        # Notebook (abas)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        # Abas
        self.criar_aba_cadastro()
        self.criar_aba_operacoes()
        self.criar_aba_consulta()
        self.criar_aba_relatorios()
        self.criar_aba_edicao()
        self.criar_aba_historico()
        self.criar_aba_import_export()  # Nova aba para importação/exportação
    
    def criar_aba_import_export(self):
        """Nova aba para importação e exportação de dados"""
        aba = ttk.Frame(self.notebook)
        self.notebook.add(aba, text="Importar/Exportar")
        
        # Frame para exportação
        frame_export = ttk.LabelFrame(aba, text="Exportar Dados", padding=10)
        frame_export.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(frame_export, text="Formato:").grid(row=0, column=0, sticky='w')
        self.export_format = tk.StringVar(value="CSV")
        ttk.Radiobutton(frame_export, text="CSV", variable=self.export_format, value="CSV").grid(row=0, column=1, sticky='w')
        ttk.Radiobutton(frame_export, text="JSON", variable=self.export_format, value="JSON").grid(row=0, column=2, sticky='w')
        
        ttk.Label(frame_export, text="Dados a exportar:").grid(row=1, column=0, sticky='w')
        self.export_data_type = tk.StringVar(value="equipamentos")
        ttk.Combobox(frame_export, textvariable=self.export_data_type, 
                    values=["equipamentos", "funcionarios", "vinculos", "todos"]).grid(row=1, column=1, columnspan=2, sticky='ew')
        
        ttk.Button(frame_export, text="Exportar", command=self.exportar_dados).grid(row=2, column=1, pady=10, sticky='e')
        
        # Frame para importação
        frame_import = ttk.LabelFrame(aba, text="Importar Dados", padding=10)
        frame_import.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(frame_import, text="Formato:").grid(row=0, column=0, sticky='w')
        self.import_format = tk.StringVar(value="CSV")
        ttk.Radiobutton(frame_import, text="CSV", variable=self.import_format, value="CSV").grid(row=0, column=1, sticky='w')
        ttk.Radiobutton(frame_import, text="JSON", variable=self.import_format, value="JSON").grid(row=0, column=2, sticky='w')
        
        ttk.Label(frame_import, text="Arquivo:").grid(row=1, column=0, sticky='w')
        self.import_file_path = tk.StringVar()
        ttk.Entry(frame_import, textvariable=self.import_file_path, width=40).grid(row=1, column=1, sticky='ew')
        ttk.Button(frame_import, text="Selecionar", command=self.selecionar_arquivo_importacao).grid(row=1, column=2, padx=5)
        
        ttk.Button(frame_import, text="Importar", command=self.importar_dados).grid(row=2, column=1, pady=10, sticky='e')
    
    def selecionar_arquivo_importacao(self):
        """Abre a caixa de diálogo para selecionar arquivo de importação"""
        filetypes = []
        if self.import_format.get() == "CSV":
            filetypes = [("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")]
        else:
            filetypes = [("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")]
        
        filename = filedialog.askopenfilename(
            title="Selecione o arquivo para importar",
            filetypes=filetypes
        )
        
        if filename:
            self.import_file_path.set(filename)
    
    def exportar_dados(self):
        """Exporta dados para um arquivo CSV ou JSON"""
        data_type = self.export_data_type.get()
        file_format = self.export_format.get()
        
        try:
            conn = sqlite3.connect(self.DB_PATH)
            cursor = conn.cursor()
            
            # Define o nome padrão do arquivo
            default_filename = f"export_{data_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            if file_format == "CSV":
                default_filename += ".csv"
            else:
                default_filename += ".json"
            
            # Abre a caixa de diálogo para salvar o arquivo
            filetypes = []
            if file_format == "CSV":
                filetypes = [("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")]
            else:
                filetypes = [("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")]
            
            filename = filedialog.asksaveasfilename(
                title="Salvar arquivo de exportação",
                initialfile=default_filename,
                filetypes=filetypes,
                defaultextension=f".{file_format.lower()}"
            )
            
            if not filename:  # Usuário cancelou
                return
            
            # Obtém os dados do banco de dados
            data = {}
            
            if data_type == "equipamentos" or data_type == "todos":
                cursor.execute("SELECT * FROM equipamentos")
                data["equipamentos"] = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
            
            if data_type == "funcionarios" or data_type == "todos":
                cursor.execute("SELECT * FROM funcionarios")
                data["funcionarios"] = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
            
            if data_type == "vinculos" or data_type == "todos":
                cursor.execute("SELECT * FROM vinculos")
                data["vinculos"] = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
            
            # Exporta para o formato selecionado
            if file_format == "CSV":
                self.exportar_para_csv(data, data_type, filename)
            else:
                self.exportar_para_json(data, filename)
            
            messagebox.showinfo("Sucesso", f"Dados exportados com sucesso para:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar dados: {str(e)}")
        finally:
            conn.close()
    
    def exportar_para_csv(self, data, data_type, filename):
        """Exporta dados para CSV"""
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            if data_type == "todos":
                # Exporta cada tabela para uma planilha diferente (não suportado diretamente em CSV)
                # Neste caso, vamos exportar cada tabela para um arquivo separado
                base_name = os.path.splitext(filename)[0]
                
                for table_name, table_data in data.items():
                    if table_data:  # Só exporta se houver dados
                        table_filename = f"{base_name}_{table_name}.csv"
                        with open(table_filename, 'w', newline='', encoding='utf-8') as table_file:
                            writer = csv.DictWriter(table_file, fieldnames=table_data[0].keys())
                            writer.writeheader()
                            writer.writerows(table_data)
            else:
                # Exporta uma única tabela
                table_data = data[data_type]
                if table_data:
                    writer = csv.DictWriter(file, fieldnames=table_data[0].keys())
                    writer.writeheader()
                    writer.writerows(table_data)
    
    def exportar_para_json(self, data, filename):
        """Exporta dados para JSON"""
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
    
    def importar_dados(self):
        """Importa dados de um arquivo CSV ou JSON"""
        filename = self.import_file_path.get()
        if not filename:
            messagebox.showerror("Erro", "Selecione um arquivo para importar!")
            return
        
        file_format = self.import_format.get()
        
        try:
            if file_format == "CSV":
                self.importar_de_csv(filename)
            else:
                self.importar_de_json(filename)
            
            messagebox.showinfo("Sucesso", "Dados importados com sucesso!")
            self.import_file_path.set("")  # Limpa o campo do arquivo
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao importar dados: {str(e)}")
    
    def importar_de_csv(self, filename):
        """Importa dados de um arquivo CSV"""
        try:
            conn = sqlite3.connect(self.DB_PATH)
            cursor = conn.cursor()
            
            with open(filename, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                # Determina o tipo de dados pelo nome do arquivo ou cabeçalho
                if "equipamentos" in filename.lower():
                    table = "equipamentos"
                elif "funcionarios" in filename.lower():
                    table = "funcionarios"
                elif "vinculos" in filename.lower():
                    table = "vinculos"
                else:
                    # Tenta determinar pela estrutura do arquivo
                    first_row = next(reader, None)
                    if first_row is None:
                        raise ValueError("Arquivo CSV vazio")
                    
                    if "numero" in first_row and "modelo" in first_row and "serial" in first_row:
                        table = "equipamentos"
                    elif "nome" in first_row and "matricula" in first_row:
                        table = "funcionarios"
                    elif "funcionario_id" in first_row and "equipamento_id" in first_row:
                        table = "vinculos"
                    else:
                        raise ValueError("Não foi possível determinar o tipo de dados no arquivo CSV")
                    
                    # Volta para o início do arquivo
                    file.seek(0)
                    next(reader)  # Pula o cabeçalho novamente
                
                # Importa os dados para a tabela correspondente
                if table == "equipamentos":
                    for row in reader:
                        cursor.execute(
                            "INSERT OR IGNORE INTO equipamentos (numero, modelo, serial, status) VALUES (?, ?, ?, ?)",
                            (row.get('numero'), row.get('modelo'), row.get('serial'), row.get('status', 'Disponível')))
                elif table == "funcionarios":
                    for row in reader:
                        cursor.execute(
                            "INSERT OR IGNORE INTO funcionarios (nome, matricula) VALUES (?, ?)",
                            (row.get('nome'), row.get('matricula')))
                elif table == "vinculos":
                    for row in reader:
                        cursor.execute(
                            "INSERT OR IGNORE INTO vinculos (funcionario_id, equipamento_id, data_entrega, data_devolucao) VALUES (?, ?, ?, ?)",
                            (row.get('funcionario_id'), row.get('equipamento_id'), 
                             row.get('data_entrega'), row.get('data_devolucao')))
                
                conn.commit()
                
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def importar_de_json(self, filename):
        """Importa dados de um arquivo JSON"""
        try:
            conn = sqlite3.connect(self.DB_PATH)
            cursor = conn.cursor()
            
            with open(filename, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
                # Verifica se é um arquivo com todas as tabelas ou apenas uma
                if isinstance(data, dict) and any(key in data for key in ['equipamentos', 'funcionarios', 'vinculos']):
                    # Arquivo com múltiplas tabelas
                    if 'equipamentos' in data:
                        for equip in data['equipamentos']:
                            cursor.execute(
                                "INSERT OR IGNORE INTO equipamentos (numero, modelo, serial, status) VALUES (?, ?, ?, ?)",
                                (equip.get('numero'), equip.get('modelo'), equip.get('serial'), equip.get('status', 'Disponível')))
                    
                    if 'funcionarios' in data:
                        for func in data['funcionarios']:
                            cursor.execute(
                                "INSERT OR IGNORE INTO funcionarios (nome, matricula) VALUES (?, ?)",
                                (func.get('nome'), func.get('matricula')))
                    
                    if 'vinculos' in data:
                        for vinc in data['vinculos']:
                            cursor.execute(
                                "INSERT OR IGNORE INTO vinculos (funcionario_id, equipamento_id, data_entrega, data_devolucao) VALUES (?, ?, ?, ?)",
                                (vinc.get('funcionario_id'), vinc.get('equipamento_id'), 
                                 vinc.get('data_entrega'), vinc.get('data_devolucao')))
                else:
                    # Arquivo com uma única tabela (array de objetos)
                    if not isinstance(data, list):
                        raise ValueError("Formato JSON inválido - esperado um array de objetos ou um objeto com tabelas")
                    
                    # Tenta determinar o tipo de dados pelo primeiro item
                    if len(data) > 0:
                        first_item = data[0]
                        
                        if 'numero' in first_item and 'modelo' in first_item and 'serial' in first_item:
                            for equip in data:
                                cursor.execute(
                                    "INSERT OR IGNORE INTO equipamentos (numero, modelo, serial, status) VALUES (?, ?, ?, ?)",
                                    (equip.get('numero'), equip.get('modelo'), equip.get('serial'), equip.get('status', 'Disponível')))
                        elif 'nome' in first_item and 'matricula' in first_item:
                            for func in data:
                                cursor.execute(
                                    "INSERT OR IGNORE INTO funcionarios (nome, matricula) VALUES (?, ?)",
                                    (func.get('nome'), func.get('matricula')))
                        elif 'funcionario_id' in first_item and 'equipamento_id' in first_item:
                            for vinc in data:
                                cursor.execute(
                                    "INSERT OR IGNORE INTO vinculos (funcionario_id, equipamento_id, data_entrega, data_devolucao) VALUES (?, ?, ?, ?)",
                                    (vinc.get('funcionario_id'), vinc.get('equipamento_id'), 
                                     vinc.get('data_entrega'), vinc.get('data_devolucao')))
                        else:
                            raise ValueError("Não foi possível determinar o tipo de dados no arquivo JSON")
                
                conn.commit()
                
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def cadastrar_funcionario(self):
        nome = self.entry_nome_func.get()
        matricula = self.entry_matricula.get()
        
        if not nome or not matricula:
            messagebox.showerror("Erro", "Preencha todos os campos!")
            return
        
        try:
            conn = sqlite3.connect(self.DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM funcionarios WHERE matricula = ?", (matricula,))
            if cursor.fetchone():
                messagebox.showerror("Erro", "Matrícula já cadastrada!")
                return
            
            cursor.execute("INSERT INTO funcionarios (nome, matricula) VALUES (?, ?)", (nome, matricula))
            conn.commit()
            messagebox.showinfo("Sucesso", "Funcionário cadastrado com sucesso!")
            
            # Limpa os campos
            self.entry_nome_func.delete(0, 'end')
            self.entry_matricula.delete(0, 'end')
            
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar funcionário: {e}")
        finally:
            conn.close()
    
    def cadastrar_equipamento(self):
        numero = self.entry_numero.get()
        modelo = self.entry_modelo.get()
        serial = self.entry_serial.get()
        
        if not numero or not modelo or not serial:
            messagebox.showerror("Erro", "Preencha todos os campos!")
            return
        
        try:
            conn = sqlite3.connect(self.DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM equipamentos WHERE numero = ? OR serial = ?", (numero, serial))
            if cursor.fetchone():
                messagebox.showerror("Erro", "Número de equipamento ou serial já cadastrado!")
                return
            
            cursor.execute("INSERT INTO equipamentos (numero, modelo, serial) VALUES (?, ?, ?)", 
                          (numero, modelo, serial))
            conn.commit()
            messagebox.showinfo("Sucesso", "Equipamento cadastrado com sucesso!")
            
            # Limpa os campos
            self.entry_numero.delete(0, 'end')
            self.entry_modelo.delete(0, 'end')
            self.entry_serial.delete(0, 'end')
            
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar equipamento: {e}")
        finally:
            conn.close()
    
    def entregar_equipamento(self):
        matricula = self.entry_matricula_entrega.get()
        numero_equipamento = self.entry_numero_entrega.get()
        
        if not matricula or not numero_equipamento:
            messagebox.showerror("Erro", "Preencha todos os campos!")
            return
        
        try:
            conn = sqlite3.connect(self.DB_PATH)
            cursor = conn.cursor()
            
            # Verifica funcionário
            cursor.execute("SELECT id, nome FROM funcionarios WHERE matricula = ?", (matricula,))
            funcionario = cursor.fetchone()
            if not funcionario:
                messagebox.showerror("Erro", "Funcionário não encontrado!")
                return
            
            # Verifica equipamento
            cursor.execute("SELECT id, status FROM equipamentos WHERE numero = ?", (numero_equipamento,))
            equipamento = cursor.fetchone()
            if not equipamento:
                messagebox.showerror("Erro", "Equipamento não encontrado!")
                return
                
            if equipamento[1] != 'Disponível':
                cursor.execute('''
                SELECT f.nome FROM vinculos v
                JOIN funcionarios f ON v.funcionario_id = f.id
                WHERE v.equipamento_id = ? AND v.data_devolucao IS NULL
                ''', (equipamento[0],))
                usuario = cursor.fetchone()
                msg = f"Equipamento em uso por {usuario[0]}" if usuario else "Equipamento já está em uso"
                messagebox.showerror("Erro", msg)
                return
            
            # Realiza a entrega
            data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("INSERT INTO vinculos (funcionario_id, equipamento_id, data_entrega) VALUES (?, ?, ?)", 
                          (funcionario[0], equipamento[0], data_atual))
            cursor.execute("UPDATE equipamentos SET status = 'Em uso' WHERE id = ?", (equipamento[0],))
            conn.commit()
            
            messagebox.showinfo("Sucesso", 
                               f"Equipamento {numero_equipamento} entregue para {funcionario[1]} com sucesso!")
            
            # Limpa os campos
            self.entry_matricula_entrega.delete(0, 'end')
            self.entry_numero_entrega.delete(0, 'end')
            
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao realizar entrega: {e}")
        finally:
            conn.close()
    
    def receber_equipamento(self):
        numero_equipamento = self.entry_numero_recebimento.get()
        
        if not numero_equipamento:
            messagebox.showerror("Erro", "Informe o número do equipamento!")
            return
        
        try:
            conn = sqlite3.connect(self.DB_PATH)
            cursor = conn.cursor()
            
            # Verifica equipamento
            cursor.execute("SELECT id, status FROM equipamentos WHERE numero = ?", (numero_equipamento,))
            equipamento = cursor.fetchone()
            if not equipamento:
                messagebox.showerror("Erro", "Equipamento não encontrado!")
                return
                
            if equipamento[1] == 'Disponível':
                messagebox.showinfo("Informação", "Este equipamento já está disponível.")
                return
            
            # Verifica vínculo ativo
            cursor.execute('''
            SELECT id FROM vinculos 
            WHERE equipamento_id = ? AND data_devolucao IS NULL
            ''', (equipamento[0],))
            vinculo = cursor.fetchone()
            if not vinculo:
                messagebox.showerror("Erro", "Nenhum vínculo ativo encontrado para este equipamento.")
                return
            
            # Realiza o recebimento
            data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("UPDATE vinculos SET data_devolucao = ? WHERE id = ?", (data_atual, vinculo[0]))
            cursor.execute("UPDATE equipamentos SET status = 'Disponível' WHERE id = ?", (equipamento[0],))
            conn.commit()
            
            messagebox.showinfo("Sucesso", f"Equipamento {numero_equipamento} recebido com sucesso!")
            
            # Limpa o campo
            self.entry_numero_recebimento.delete(0, 'end')
            
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao realizar recebimento: {e}")
        finally:
            conn.close()
    
    def consultar_equipamento(self):
        numero_equipamento = self.entry_numero_consulta.get()
        
        if not numero_equipamento:
            messagebox.showerror("Erro", "Informe o número do equipamento!")
            return
        
        try:
            conn = sqlite3.connect(self.DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT e.numero, e.modelo, e.serial, e.status, f.nome, f.matricula 
            FROM equipamentos e
            LEFT JOIN (
                SELECT v.equipamento_id, f.nome, f.matricula 
                FROM vinculos v
                JOIN funcionarios f ON v.funcionario_id = f.id
                WHERE v.data_devolucao IS NULL
            ) f ON e.id = f.equipamento_id
            WHERE e.numero = ?
            ''', (numero_equipamento,))
            
            resultado = cursor.fetchone()
            
            self.text_consulta.config(state='normal')
            self.text_consulta.delete('1.0', 'end')
            
            if not resultado:
                self.text_consulta.insert('end', "Equipamento não encontrado.")
            else:
                self.text_consulta.insert('end', "Informações do Equipamento:\n")
                self.text_consulta.insert('end', f"Número: {resultado[0]}\n")
                self.text_consulta.insert('end', f"Modelo: {resultado[1]}\n")
                self.text_consulta.insert('end', f"Serial: {resultado[2]}\n")
                self.text_consulta.insert('end', f"Status: {resultado[3]}\n")
                
                if resultado[3] == 'Em uso':
                    self.text_consulta.insert('end', f"Usuário: {resultado[4]} (Matrícula: {resultado[5]})\n")
            
            self.text_consulta.config(state='disabled')
            
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao consultar equipamento: {e}")
        finally:
            conn.close()
    
    def gerar_relatorio_usuarios(self):
        try:
            conn = sqlite3.connect(self.DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("SELECT nome, matricula FROM funcionarios ORDER BY nome")
            usuarios = cursor.fetchall()
            
            # Limpa a treeview
            for item in self.tree_relatorio.get_children():
                self.tree_relatorio.delete(item)
            
            # Configura colunas
            self.tree_relatorio['columns'] = ('Nome', 'Matrícula')
            self.tree_relatorio.column('#0', width=0, stretch=tk.NO)
            self.tree_relatorio.column('Nome', width=300, anchor='w')
            self.tree_relatorio.column('Matrícula', width=150, anchor='w')
            
            # Cabeçalhos
            self.tree_relatorio.heading('Nome', text='Nome')
            self.tree_relatorio.heading('Matrícula', text='Matrícula')
            
            # Adiciona dados
            for usuario in usuarios:
                self.tree_relatorio.insert('', 'end', values=usuario)
            
            messagebox.showinfo("Relatório", f"Total de usuários: {len(usuarios)}")
            
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório: {e}")
        finally:
            conn.close()
    
    def gerar_relatorio_equipamentos(self):
        try:
            conn = sqlite3.connect(self.DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT e.numero, e.modelo, e.serial, e.status, f.nome 
            FROM equipamentos e
            LEFT JOIN (
                SELECT v.equipamento_id, f.nome 
                FROM vinculos v
                JOIN funcionarios f ON v.funcionario_id = f.id
                WHERE v.data_devolucao IS NULL
            ) f ON e.id = f.equipamento_id
            ORDER BY e.numero
            ''')
            
            equipamentos = cursor.fetchall()
            
            # Limpa a treeview
            for item in self.tree_relatorio.get_children():
                self.tree_relatorio.delete(item)
            
            # Configura colunas
            self.tree_relatorio['columns'] = ('Número', 'Modelo', 'Serial', 'Status', 'Usuário')
            self.tree_relatorio.column('#0', width=0, stretch=tk.NO)
            self.tree_relatorio.column('Número', width=100, anchor='w')
            self.tree_relatorio.column('Modelo', width=200, anchor='w')
            self.tree_relatorio.column('Serial', width=150, anchor='w')
            self.tree_relatorio.column('Status', width=100, anchor='w')
            self.tree_relatorio.column('Usuário', width=200, anchor='w')
            
            # Cabeçalhos
            self.tree_relatorio.heading('Número', text='Número')
            self.tree_relatorio.heading('Modelo', text='Modelo')
            self.tree_relatorio.heading('Serial', text='Serial')
            self.tree_relatorio.heading('Status', text='Status')
            self.tree_relatorio.heading('Usuário', text='Usuário')
            
            # Adiciona dados
            for equip in equipamentos:
                self.tree_relatorio.insert('', 'end', values=equip)
            
            messagebox.showinfo("Relatório", f"Total de equipamentos: {len(equipamentos)}")
            
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório: {e}")
        finally:
            conn.close()
    
    def gerar_relatorio_em_uso(self):
        try:
            conn = sqlite3.connect(self.DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT e.numero, e.modelo, e.serial, f.nome, f.matricula, v.data_entrega 
            FROM vinculos v
            JOIN equipamentos e ON v.equipamento_id = e.id
            JOIN funcionarios f ON v.funcionario_id = f.id
            WHERE v.data_devolucao IS NULL
            ORDER BY e.numero
            ''')
            
            equipamentos = cursor.fetchall()
            
            # Limpa a treeview
            for item in self.tree_relatorio.get_children():
                self.tree_relatorio.delete(item)
            
            # Configura colunas
            self.tree_relatorio['columns'] = ('Número', 'Modelo', 'Serial', 'Usuário', 'Matrícula', 'Data Entrega')
            self.tree_relatorio.column('#0', width=0, stretch=tk.NO)
            self.tree_relatorio.column('Número', width=100, anchor='w')
            self.tree_relatorio.column('Modelo', width=150, anchor='w')
            self.tree_relatorio.column('Serial', width=150, anchor='w')
            self.tree_relatorio.column('Usuário', width=200, anchor='w')
            self.tree_relatorio.column('Matrícula', width=100, anchor='w')
            self.tree_relatorio.column('Data Entrega', width=150, anchor='w')
            
            # Cabeçalhos
            self.tree_relatorio.heading('Número', text='Número')
            self.tree_relatorio.heading('Modelo', text='Modelo')
            self.tree_relatorio.heading('Serial', text='Serial')
            self.tree_relatorio.heading('Usuário', text='Usuário')
            self.tree_relatorio.heading('Matrícula', text='Matrícula')
            self.tree_relatorio.heading('Data Entrega', text='Data Entrega')
            
            # Adiciona dados
            for equip in equipamentos:
                self.tree_relatorio.insert('', 'end', values=equip)
            
            messagebox.showinfo("Relatório", f"Total de equipamentos em uso: {len(equipamentos)}")
            
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório: {e}")
        finally:
            conn.close()
    
    def editar_funcionario(self):
        matricula = simpledialog.askstring("Editar Funcionário", "Digite a matrícula do funcionário:")
        if not matricula:
            return
        
        try:
            conn = sqlite3.connect(self.DB_PATH)
            cursor = conn.cursor()
            
            # Verifica se funcionário existe
            cursor.execute("SELECT id, nome, matricula FROM funcionarios WHERE matricula = ?", (matricula,))
            funcionario = cursor.fetchone()
            if not funcionario:
                messagebox.showerror("Erro", "Funcionário não encontrado.")
                return
            
            # Solicita novos dados
            novo_nome = simpledialog.askstring("Editar Funcionário", 
                                              f"Nome atual: {funcionario[1]}\nNovo nome:", 
                                              initialvalue=funcionario[1])
            if novo_nome is None:  # Usuário cancelou
                return
                
            nova_matricula = simpledialog.askstring("Editar Funcionário", 
                                                   f"Matrícula atual: {funcionario[2]}\nNova matrícula:", 
                                                   initialvalue=funcionario[2])
            if nova_matricula is None:  # Usuário cancelou
                return
            
            # Verifica se nova matrícula já existe (se foi alterada)
            if nova_matricula != funcionario[2]:
                cursor.execute("SELECT id FROM funcionarios WHERE matricula = ? AND id != ?", 
                              (nova_matricula, funcionario[0]))
                if cursor.fetchone():
                    messagebox.showerror("Erro", "Nova matrícula já está em uso por outro funcionário.")
                    return
            
            # Atualiza os dados
            cursor.execute("UPDATE funcionarios SET nome = ?, matricula = ? WHERE id = ?", 
                          (novo_nome, nova_matricula, funcionario[0]))
            conn.commit()
            messagebox.showinfo("Sucesso", "Funcionário atualizado com sucesso!")
            
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao editar funcionário: {e}")
        finally:
            conn.close()
    
    def remover_funcionario(self):
        matricula = simpledialog.askstring("Remover Funcionário", "Digite a matrícula do funcionário:")
        if not matricula:
            return
        
        try:
            conn = sqlite3.connect(self.DB_PATH)
            cursor = conn.cursor()
            
            # Verifica se funcionário existe
            cursor.execute("SELECT id, nome FROM funcionarios WHERE matricula = ?", (matricula,))
            funcionario = cursor.fetchone()
            if not funcionario:
                messagebox.showerror("Erro", "Funcionário não encontrado.")
                return
            
            # Verifica se funcionário tem equipamentos vinculados
            cursor.execute('''
            SELECT e.numero FROM vinculos v
            JOIN equipamentos e ON v.equipamento_id = e.id
            WHERE v.funcionario_id = ? AND v.data_devolucao IS NULL
            ''', (funcionario[0],))
            equipamentos = cursor.fetchall()
            
            if equipamentos:
                lista_equipamentos = "\n".join([f"- {equip[0]}" for equip in equipamentos])
                messagebox.showerror("Erro", 
                    f"O funcionário possui equipamentos em uso e não pode ser removido:\n{lista_equipamentos}")
                return
            
            # Confirma a remoção
            if messagebox.askyesno("Confirmar", f"Tem certeza que deseja remover o funcionário {funcionario[1]} (Matrícula: {matricula})?"):
                cursor.execute("DELETE FROM funcionarios WHERE id = ?", (funcionario[0],))
                conn.commit()
                messagebox.showinfo("Sucesso", "Funcionário removido com sucesso!")
            
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao remover funcionário: {e}")
        finally:
            conn.close()
    
    def editar_equipamento(self):
        numero = simpledialog.askstring("Editar Equipamento", "Digite o número do equipamento:")
        if not numero:
            return
        
        try:
            conn = sqlite3.connect(self.DB_PATH)
            cursor = conn.cursor()
            
            # Verifica se equipamento existe
            cursor.execute("SELECT id, numero, modelo, serial, status FROM equipamentos WHERE numero = ?", (numero,))
            equipamento = cursor.fetchone()
            if not equipamento:
                messagebox.showerror("Erro", "Equipamento não encontrado.")
                return
            
            # Solicita novos dados
            novo_numero = simpledialog.askstring("Editar Equipamento", 
                                               f"Número atual: {equipamento[1]}\nNovo número:", 
                                               initialvalue=equipamento[1])
            if novo_numero is None:  # Usuário cancelou
                return
                
            novo_modelo = simpledialog.askstring("Editar Equipamento", 
                                               f"Modelo atual: {equipamento[2]}\nNovo modelo:", 
                                               initialvalue=equipamento[2])
            if novo_modelo is None:  # Usuário cancelou
                return
                
            novo_serial = simpledialog.askstring("Editar Equipamento", 
                                               f"Serial atual: {equipamento[3]}\nNovo serial:", 
                                               initialvalue=equipamento[3])
            if novo_serial is None:  # Usuário cancelou
                return
            
            # Verifica se novo número ou serial já existem (se foram alterados)
            if novo_numero != equipamento[1]:
                cursor.execute("SELECT id FROM equipamentos WHERE numero = ? AND id != ?", 
                              (novo_numero, equipamento[0]))
                if cursor.fetchone():
                    messagebox.showerror("Erro", "Novo número já está em uso por outro equipamento.")
                    return
            
            if novo_serial != equipamento[3]:
                cursor.execute("SELECT id FROM equipamentos WHERE serial = ? AND id != ?", 
                              (novo_serial, equipamento[0]))
                if cursor.fetchone():
                    messagebox.showerror("Erro", "Novo serial já está em uso por outro equipamento.")
                    return
            
            # Atualiza os dados
            cursor.execute("UPDATE equipamentos SET numero = ?, modelo = ?, serial = ? WHERE id = ?", 
                          (novo_numero, novo_modelo, novo_serial, equipamento[0]))
            conn.commit()
            messagebox.showinfo("Sucesso", "Equipamento atualizado com sucesso!")
            
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao editar equipamento: {e}")
        finally:
            conn.close()
    
    def remover_equipamento(self):
        numero = simpledialog.askstring("Remover Equipamento", "Digite o número do equipamento:")
        if not numero:
            return
        
        try:
            conn = sqlite3.connect(self.DB_PATH)
            cursor = conn.cursor()
            
            # Verifica se equipamento existe
            cursor.execute("SELECT id, numero, modelo, status FROM equipamentos WHERE numero = ?", (numero,))
            equipamento = cursor.fetchone()
            if not equipamento:
                messagebox.showerror("Erro", "Equipamento não encontrado.")
                return
            
            # Verifica se equipamento está em uso
            if equipamento[3] == 'Em uso':
                cursor.execute('''
                SELECT f.nome FROM vinculos v
                JOIN funcionarios f ON v.funcionario_id = f.id
                WHERE v.equipamento_id = ? AND v.data_devolucao IS NULL
                ''', (equipamento[0],))
                usuario = cursor.fetchone()
                msg = f"O equipamento está em uso por {usuario[0]} e não pode ser removido." if usuario else "O equipamento está em uso e não pode ser removido."
                messagebox.showerror("Erro", msg)
                return
            
            # Confirma a remoção
            if messagebox.askyesno("Confirmar", f"Tem certeza que deseja remover o equipamento {equipamento[1]} (Modelo: {equipamento[2]})?"):
                # Remove primeiro os vínculos associados
                cursor.execute("DELETE FROM vinculos WHERE equipamento_id = ?", (equipamento[0],))
                # Depois remove o equipamento
                cursor.execute("DELETE FROM equipamentos WHERE id = ?", (equipamento[0],))
                conn.commit()
                messagebox.showinfo("Sucesso", "Equipamento removido com sucesso!")
            
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao remover equipamento: {e}")
        finally:
            conn.close()
    
    def visualizar_historico_equipamento(self):
        numero = self.entry_numero_historico.get()
        if not numero:
            messagebox.showerror("Erro", "Informe o número do equipamento!")
            return
        
        try:
            conn = sqlite3.connect(self.DB_PATH)
            cursor = conn.cursor()
            
            # Verifica se equipamento existe
            cursor.execute("SELECT id, numero, modelo FROM equipamentos WHERE numero = ?", (numero,))
            equipamento = cursor.fetchone()
            if not equipamento:
                messagebox.showerror("Erro", "Equipamento não encontrado.")
                return
            
            # Obtém o histórico
            cursor.execute('''
            SELECT f.nome, f.matricula, v.data_entrega, v.data_devolucao 
            FROM vinculos v
            JOIN funcionarios f ON v.funcionario_id = f.id
            WHERE v.equipamento_id = ?
            ORDER BY v.data_entrega DESC
            ''', (equipamento[0],))
            
            historico = cursor.fetchall()
            
            # Exibe na área de texto
            self.text_historico.config(state='normal')
            self.text_historico.delete('1.0', 'end')
            
            if not historico:
                self.text_historico.insert('end', f"Nenhum histórico encontrado para o equipamento {equipamento[1]} ({equipamento[2]})")
            else:
                self.text_historico.insert('end', f"Histórico do Equipamento {equipamento[1]} ({equipamento[2]}):\n\n")
                for registro in historico:
                    self.text_historico.insert('end', f"Usuário: {registro[0]}\n")
                    self.text_historico.insert('end', f"Matrícula: {registro[1]}\n")
                    self.text_historico.insert('end', f"Data Entrega: {registro[2]}\n")
                    self.text_historico.insert('end', f"Data Devolução: {registro[3] if registro[3] else 'Não devolvido'}\n")
                    self.text_historico.insert('end', "-"*50 + "\n")
            
            self.text_historico.config(state='disabled')
            
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao consultar histórico: {e}")
        finally:
            conn.close()
    
    def criar_aba_cadastro(self):
        aba = ttk.Frame(self.notebook)
        self.notebook.add(aba, text="Cadastro")
        
        # Frame principal com padding
        frame_principal = ttk.Frame(aba, padding=20)
        frame_principal.pack(expand=True, fill='both')
        
        # Card para cadastro de funcionário
        card_func = ttk.Frame(frame_principal, style='Card.TFrame', padding=15)
        card_func.pack(fill='x', pady=10)
        
        ttk.Label(card_func, text="Cadastrar Funcionário", style='Title.TLabel').pack(anchor='w', pady=(0, 10))
        
        # Grid para os campos do funcionário
        campos_func_frame = ttk.Frame(card_func)
        campos_func_frame.pack(fill='x')
        
        ttk.Label(campos_func_frame, text="Nome:").grid(row=0, column=0, sticky='w', pady=5, padx=5)
        self.entry_nome_func = ttk.Entry(campos_func_frame, width=30)
        self.entry_nome_func.grid(row=0, column=1, sticky='ew', pady=5, padx=5)
        
        ttk.Label(campos_func_frame, text="Matrícula:").grid(row=1, column=0, sticky='w', pady=5, padx=5)
        self.entry_matricula = ttk.Entry(campos_func_frame, width=30)
        self.entry_matricula.grid(row=1, column=1, sticky='ew', pady=5, padx=5)
        
        btn_func_frame = ttk.Frame(card_func)
        btn_func_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(btn_func_frame, text="Cadastrar", command=self.cadastrar_funcionario, 
                style='Primary.TButton').pack(side='right')

        # Card para cadastro de equipamento (completo)
        card_equip = ttk.Frame(frame_principal, style='Card.TFrame', padding=15)
        card_equip.pack(fill='x', pady=10)
        
        ttk.Label(card_equip, text="Cadastrar Equipamento", style='Title.TLabel').pack(anchor='w', pady=(0, 10))
        
        # Grid para os campos do equipamento
        campos_equip_frame = ttk.Frame(card_equip)
        campos_equip_frame.pack(fill='x')
        
        # Número do equipamento
        ttk.Label(campos_equip_frame, text="Número:").grid(row=0, column=0, sticky='w', pady=5, padx=5)
        self.entry_numero = ttk.Entry(campos_equip_frame, width=30)
        self.entry_numero.grid(row=0, column=1, sticky='ew', pady=5, padx=5)
        
        # Modelo do equipamento
        ttk.Label(campos_equip_frame, text="Modelo:").grid(row=1, column=0, sticky='w', pady=5, padx=5)
        self.entry_modelo = ttk.Entry(campos_equip_frame, width=30)
        self.entry_modelo.grid(row=1, column=1, sticky='ew', pady=5, padx=5)
        
        # Serial do equipamento
        ttk.Label(campos_equip_frame, text="Serial:").grid(row=2, column=0, sticky='w', pady=5, padx=5)
        self.entry_serial = ttk.Entry(campos_equip_frame, width=30)
        self.entry_serial.grid(row=2, column=1, sticky='ew', pady=5, padx=5)
        
        # Botão de cadastro
        btn_equip_frame = ttk.Frame(card_equip)
        btn_equip_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(btn_equip_frame, text="Cadastrar", command=self.cadastrar_equipamento,
                style='Primary.TButton').pack(side='right')
        
        # Configuração de peso para centralização
        frame_principal.grid_rowconfigure(0, weight=1)
        frame_principal.grid_columnconfigure(0, weight=1)
    
    def criar_aba_operacoes(self):
        aba = ttk.Frame(self.notebook)
        self.notebook.add(aba, text="Operações")
        
        # Frame principal para centralizar
        frame_principal = ttk.Frame(aba)
        frame_principal.pack(expand=True, fill='both', padx=50, pady=20)
        
        # Frame para entrega de equipamentos
        frame_entrega = ttk.LabelFrame(frame_principal, text="Entregar Equipamento", padding=20)
        frame_entrega.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(frame_entrega, text="Matrícula do Funcionário:").grid(row=0, column=0, sticky='w', pady=5)
        self.entry_matricula_entrega = ttk.Entry(frame_entrega, width=40)
        self.entry_matricula_entrega.grid(row=0, column=1, sticky='ew', padx=10, pady=5)
        
        ttk.Label(frame_entrega, text="Número do Equipamento:").grid(row=1, column=0, sticky='w', pady=5)
        self.entry_numero_entrega = ttk.Entry(frame_entrega, width=40)
        self.entry_numero_entrega.grid(row=1, column=1, sticky='ew', padx=10, pady=5)
        
        ttk.Button(frame_entrega, text="Entregar", command=self.entregar_equipamento).grid(row=2, column=1, pady=15, sticky='e')
        
        # Frame para recebimento de equipamentos
        frame_recebimento = ttk.LabelFrame(frame_principal, text="Receber Equipamento", padding=20)
        frame_recebimento.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(frame_recebimento, text="Número do Equipamento:").grid(row=0, column=0, sticky='w', pady=5)
        self.entry_numero_recebimento = ttk.Entry(frame_recebimento, width=40)
        self.entry_numero_recebimento.grid(row=0, column=1, sticky='ew', padx=10, pady=5)
        
        ttk.Button(frame_recebimento, text="Receber", command=self.receber_equipamento).grid(row=1, column=1, pady=15, sticky='e')
        
        # Configuração de peso para centralização
        frame_principal.grid_rowconfigure(0, weight=1)
        frame_principal.grid_columnconfigure(0, weight=1)
    
    def criar_aba_consulta(self):
        aba = ttk.Frame(self.notebook)
        self.notebook.add(aba, text="Consulta")
        
        # Frame para consulta de equipamentos
        frame_consulta = ttk.LabelFrame(aba, text="Consultar Equipamento", padding=10)
        frame_consulta.pack(fill='both', expand=True, padx=10, pady=5)
        
        ttk.Label(frame_consulta, text="Número do Equipamento:").grid(row=0, column=0, sticky='w')
        self.entry_numero_consulta = ttk.Entry(frame_consulta)
        self.entry_numero_consulta = self.entry_numero_consulta  # Corrigindo o nome da variável
        self.entry_numero_consulta.grid(row=0, column=1, sticky='ew', padx=5, pady=2)
        
        ttk.Button(frame_consulta, text="Consultar", command=self.consultar_equipamento).grid(row=0, column=2, padx=5)
        
        # Área de texto para exibir resultados
        self.text_consulta = tk.Text(frame_consulta, height=10, state='disabled')
        self.text_consulta.grid(row=1, column=0, columnspan=3, sticky='nsew', pady=10)
        
        # Scrollbar
        scroll = ttk.Scrollbar(frame_consulta, command=self.text_consulta.yview)
        scroll.grid(row=1, column=3, sticky='ns')
        self.text_consulta.config(yscrollcommand=scroll.set)
        
        # Configuração do grid para expansão
        frame_consulta.grid_rowconfigure(1, weight=1)
        frame_consulta.grid_columnconfigure(1, weight=1)
    
    def criar_aba_relatorios(self):
        aba = ttk.Frame(self.notebook)
        self.notebook.add(aba, text="Relatórios")
        
        # Frame principal
        frame_principal = ttk.Frame(aba, padding=20)
        frame_principal.pack(expand=True, fill='both')
        
        # Card de seleção de relatório
        card_selecao = ttk.Frame(frame_principal, style='Card.TFrame', padding=15)
        card_selecao.pack(fill='x', pady=10)
        
        ttk.Label(card_selecao, text="Selecionar Relatório", style='Title.TLabel').pack(anchor='w', pady=(0, 10))
        
        btn_frame = ttk.Frame(card_selecao)
        btn_frame.pack(fill='x')
        
        ttk.Button(btn_frame, text="Lista de Usuários", command=self.gerar_relatorio_usuarios,
                style='Primary.TButton').pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Lista de Equipamentos", command=self.gerar_relatorio_equipamentos,
                style='Primary.TButton').pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Equipamentos em Uso", command=self.gerar_relatorio_em_uso,
                style='Primary.TButton').pack(side='left', padx=5)
        
        # Card de exibição do relatório
        card_relatorio = ttk.Frame(frame_principal, style='Card.TFrame', padding=15)
        card_relatorio.pack(fill='both', expand=True, pady=10)
        
        ttk.Label(card_relatorio, text="Relatório", style='Title.TLabel').pack(anchor='w', pady=(0, 10))
        
        # Treeview com scrollbars
        self.tree_relatorio = ttk.Treeview(card_relatorio)
        self.tree_relatorio.pack(fill='both', expand=True)
        
        vsb = ttk.Scrollbar(card_relatorio, orient="vertical", command=self.tree_relatorio.yview)
        hsb = ttk.Scrollbar(card_relatorio, orient="horizontal", command=self.tree_relatorio.xview)
        self.tree_relatorio.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')
    
    def criar_aba_edicao(self):
        aba = ttk.Frame(self.notebook)
        self.notebook.add(aba, text="Edição")
        
        # Frame para edição de funcionários
        frame_func = ttk.LabelFrame(aba, text="Editar Funcionários", padding=10)
        frame_func.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(frame_func, text="Editar Funcionário", command=self.editar_funcionario).pack(side='left', padx=5)
        ttk.Button(frame_func, text="Remover Funcionário", command=self.remover_funcionario).pack(side='left', padx=5)
        
        # Frame para edição de equipamentos
        frame_equip = ttk.LabelFrame(aba, text="Editar Equipamentos", padding=10)
        frame_equip.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(frame_equip, text="Editar Equipamento", command=self.editar_equipamento).pack(side='left', padx=5)
        ttk.Button(frame_equip, text="Remover Equipamento", command=self.remover_equipamento).pack(side='left', padx=5)
    
    def criar_aba_historico(self):
        aba = ttk.Frame(self.notebook)
        self.notebook.add(aba, text="Histórico")
        
        # Frame principal
        frame_principal = ttk.Frame(aba)
        frame_principal.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Frame para consulta de histórico
        frame_consulta = ttk.LabelFrame(frame_principal, text="Consultar Histórico do Equipamento", padding=15)
        frame_consulta.pack(fill='both', expand=True, padx=10, pady=10)
        
        ttk.Label(frame_consulta, text="Número do Equipamento:").grid(row=0, column=0, sticky='w', pady=10)
        self.entry_numero_historico = ttk.Entry(frame_consulta, width=30)
        self.entry_numero_historico.grid(row=0, column=1, sticky='ew', padx=10, pady=10)
        
        ttk.Button(frame_consulta, text="Consultar", command=self.visualizar_historico_equipamento).grid(row=0, column=2, padx=10)
        
        # Área para exibir o histórico (será preenchida quando o método for chamado)
        self.text_historico = tk.Text(frame_consulta, height=15, state='disabled')
        self.text_historico.grid(row=1, column=0, columnspan=3, sticky='nsew', pady=10)
        
        # Scrollbar
        scroll = ttk.Scrollbar(frame_consulta, command=self.text_historico.yview)
        scroll.grid(row=1, column=3, sticky='ns')
        self.text_historico.config(yscrollcommand=scroll.set)
        
        # Configuração do grid para expansão
        frame_consulta.grid_rowconfigure(1, weight=1)
        frame_consulta.grid_columnconfigure(1, weight=1)

if __name__ == "__main__":
    root = tk.Tk()
    app = SistemaGerenciamentoEquipamentos(root)
    root.mainloop()