from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from configuracoes import C_Servidor, C_UID, C_PWD
import pyodbc
import logging

app = Flask(__name__)
CORS(app)  # Permite requisições de outros domínios

def get_db_connection():
    try:
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            f'SERVER={C_Servidor};'
            'DATABASE=BD_ENORFROTA;'
            f'UID={C_UID};'
            f'PWD={C_PWD}'
        )
        return conn
    except pyodbc.Error as e:
        logging.error(f"Erro ao conectar com o banco de dados: {e}")
        raise Exception("Erro ao conectar com o servidor. Tente novamente.")

@app.route('/api/bases', methods=['GET'])
def listar_bases():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT ID, Nome_Base, Estado, Cidade, Endereco, Status FROM dbo.tab_base")
        bases = []
        for row in cursor.fetchall():
            bases.append({
                "id": row.ID,
                "nome": row.Nome_Base,
                "estado": row.Estado,
                "cidade": row.Cidade,
                "endereco": row.Endereco,  # <-- sem acento
                "status": row.Status
            })
        conn.close()
        return jsonify(bases)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/bases', methods=['POST'])
def adicionar_base():
    try:
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO dbo.tab_base (Nome_Base, Estado, Cidade, Endereco, Status)
            VALUES (?, ?, ?, ?, ?)
        """,
        data['nome'],         # Nome_Base
        data['estado'],       # Estado
        data['cidade'],       # Cidade
        data['endereco'],     # Endereco (sem acento)
        data['status'])       # Status
        conn.commit()
        conn.close()
        return jsonify({"mensagem": "Base salva com sucesso!"}), 201
    except Exception as e:
        print("ERRO AO SALVAR BASE:", e)  # <-- Adicione esta linha
        return jsonify({"erro": str(e)}), 500

@app.route('/api/bases/<int:id>', methods=['PUT'])
def atualizar_status(id):
    try:
        data = request.get_json()
        novo_status = data.get('status')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE dbo.tab_base SET Status = ? WHERE ID = ?
        """, novo_status, id)
        conn.commit()
        conn.close()
        return jsonify({"mensagem": "Status atualizado com sucesso!"})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# APLICAÇÃO ABAIXO É REFERENTE A PAGINA "CENTRO DE CUSTO"----------------------------------------------------

@app.route('/api/centros_custo', methods=['GET'])
def listar_centros_custo():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT ID, ID_CentroCusto, Nome, Responsavel, Status FROM dbo.tab_centrocusto")
        centros = []
        for row in cursor.fetchall():
            centros.append({
                "id": row.ID,
                "id_centro_custo": row.ID_CentroCusto,
                "nome": row.Nome,
                "responsavel": row.Responsavel,
                "status": row.Status
            })
        conn.close()
        return jsonify(centros)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/centros_custo', methods=['POST'])
def adicionar_centro_custo():
    try:
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO dbo.tab_centrocusto (ID_CentroCusto, Nome, Responsavel, Status)
            VALUES (?, ?, ?, ?)
        """, data['id_centro_custo'], data['nome'], data['responsavel'], data['status'])
        conn.commit()
        conn.close()
        return jsonify({"mensagem": "Centro de Custo cadastrado com sucesso!"}), 201
    except Exception as e:
        print("ERRO AO SALVAR CENTRO DE CUSTO:", e)
        return jsonify({"erro": str(e)}), 500

# APLICAÇÃO ABAIXO É REFERENTE A PAGINA "VEICULOS"----------------------------------------------------

@app.route('/api/veiculos', methods=['GET'])
def listar_veiculos():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Marca, Modelo, Ano, Renavam, Placa, Tipo_combustivel, Hodometro_inicial, Motorista, Tipo_Locacao, Documento, Status
            FROM dbo.tab_veiculos
        """)
        veiculos = []
        for row in cursor.fetchall():
            veiculos.append({
                "Marca": row.Marca,
                "Modelo": row.Modelo,
                "Ano": row.Ano,
                "Renavam": row.Renavam,
                "Placa": row.Placa,
                "Tipo_combustivel": row.Tipo_combustivel,
                "Hodometro_inicial": row.Hodometro_inicial,
                "Motorista": row.Motorista,
                "Tipo_Locacao": row.Tipo_Locacao,
                "Documento": row.Documento,
                "Status": row.Status
            })
        conn.close()
        return jsonify(veiculos)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/veiculos', methods=['POST'])
def adicionar_veiculo():
    try:
        data = request.get_json()
        print("Recebido para inserir:", data)  # <-- Para depuração
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO dbo.tab_veiculos
            (Marca, Modelo, Ano, Renavam, Placa, Tipo_combustivel, Hodometro_inicial, Motorista, Tipo_Locacao, Documento, Status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        data['Marca'],
        data['Modelo'],
        data['Ano'],
        data['Renavam'],
        data['Placa'],
        data['Tipo_combustivel'],
        data['Hodometro_inicial'],
        data['Motorista'],
        data['Tipo_Locacao'],
        data['Documento'],
        data['Status'])
        conn.commit()
        conn.close()
        return jsonify({"mensagem": "Veículo cadastrado com sucesso!"}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/veiculos/<placa>', methods=['PUT'])
def atualizar_veiculo(placa):
    try:
        data = request.get_json()
        print("Recebido para atualizar:", placa, data)  # <-- Adicione esta linha
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE dbo.tab_veiculos
            SET Marca = ?, Modelo = ?, Ano = ?, Renavam = ?, Tipo_combustivel = ?, Hodometro_inicial = ?, Motorista = ?, Tipo_Locacao = ?, Documento = ?, Status = ?
            WHERE Placa = ?
        """, data['Marca'], data['Modelo'], data['Ano'], data['Renavam'], data['Tipo_combustivel'], data['Hodometro_inicial'], data['Motorista'], data['Tipo_Locacao'], data['Documento'], data['Status'], placa)
        conn.commit()
        conn.close()
        return jsonify({"mensagem": "Veículo atualizado com sucesso!"})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# APLICAÇÃO ABAIXO É REFERENTE A PAGINA "FUNCIONARIOS"----------------------------------------------------

@app.route('/api/funcionarios', methods=['POST'])
def adicionar_funcionario():
    try:
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO dbo.tab_funcionarios
            (Nome, RG, CPF, CentroCusto, CNH, Categoria_CNH, Validade_CNH, Nivel_acesso, Data_nascimento, Placa, ID_Cartao, Email, Senha)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['Nome'],
            data['RG'],
            data['CPF'],
            data['CentroCusto'],
            data['CNH'],
            data['Categoria_CNH'],
            data['Validade_CNH'],
            data['Nivel_acesso'],
            data['Data_nascimento'],
            data['Placa'],
            data['ID_Cartao'],
            data['Email'],
            data['Senha']
        ))
        conn.commit()
        conn.close()
        return jsonify({"mensagem": "Funcionário cadastrado com sucesso!"}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/funcionarios', methods=['GET'])
def listar_funcionarios():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT CPF, RG, Nome, Data_nascimento, Nivel_acesso, CNH, Categoria_CNH, 
                   Validade_CNH, Placa, CentroCusto, ID_Cartao, Status
            FROM dbo.tab_funcionarios
        """)
        funcionarios = []
        for row in cursor.fetchall():
            funcionarios.append({
                "cpf": row.CPF,
                "rg": row.RG,
                "nome": row.Nome,
                "data_nascimento": row.Data_nascimento,
                "nivel_acesso": row.Nivel_acesso,
                "cnh": row.CNH,
                "categoria_cnh": row.Categoria_CNH,
                "validade_cnh": row.Validade_CNH,
                "placa": row.Placa,
                "centro_custo": row.CentroCusto,
                "cartao": row.ID_Cartao,
                "status": row.Status
            })
        conn.close()
        return jsonify(funcionarios)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)