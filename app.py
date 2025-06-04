from flask import Flask, request, render_template, redirect, url_for, session, jsonify, send_file
from flask_cors import CORS
from configuracoes import C_Servidor, C_UID, C_PWD
import pyodbc
import logging
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "ENORSIG"
app.permanent_session_lifetime = timedelta(hours=1)
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
        cursor.execute("SELECT ID, NOME_BASE, ESTADO, CIDADE, ENDERECO, STATUS FROM dbo.tab_base")
        bases = []
        for row in cursor.fetchall():
            bases.append({
                "id": row.ID,
                "nome": row.NOME_BASE,
                "estado": row.ESTADO,
                "cidade": row.CIDADE,
                "endereco": row.ENDERECO,  # <-- sem acento
                "status": row.STATUS
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
            INSERT INTO dbo.tab_base (NOME_BASE, ESTADO, CIDADE, ENDERECO, STATUS)
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
            UPDATE dbo.tab_base SET STATUS = ? WHERE ID = ?
        """, novo_status, id)
        conn.commit()
        conn.close()
        return jsonify({"mensagem": "Status atualizado com sucesso!"})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# APLICAÇÃO ABAIXO É REFERENTE A PAGINA "CENTRO DE CUSTO"----------------------------------------------------

@app.route('/api/centros_custo/<int:id>', methods=['PUT'])
def atualizar_status_centro_custo(id):
    try:
        data = request.get_json()
        print("DADOS RECEBIDOS:", data)  # debug
        novo_status = data.get('status')

        if novo_status not in ['Ativo', 'Inativo']:
            return jsonify({"erro": "Status inválido"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE dbo.tab_centrocusto
            SET STATUS = ?
            WHERE ID_CENTRO_CUSTO = ?
        """, (novo_status, id))
        conn.commit()
        conn.close()
        return jsonify({"mensagem": "Status atualizado com sucesso!"}), 200

    except Exception as e:
        print("ERRO AO ATUALIZAR STATUS:", e)
        return jsonify({"erro": str(e)}), 500


































@app.route('/api/centros_custo', methods=['GET'])
def listar_centros_custo():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT ID, ID_CENTRO_CUSTO, NOME, RESPONSAVEL, STATUS FROM dbo.tab_centrocusto")
        centros = []
        for row in cursor.fetchall():
            centros.append({
                "id": row.ID,
                "id_centro_custo": row.ID_CENTRO_CUSTO,
                "nome": row.NOME,
                "responsavel": row.RESPONSAVEL,
                "status": row.STATUS
            })
        conn.close()
        return jsonify(centros)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/centros_custo', methods=['POST'])
def adicionar_centro_custo():
    try:
        data = request.get_json()

        id_centro = data['ID_CENTRO_CUSTO']
        nome = data['NOME']
        responsavel = data['RESPONSAVEL']
        status = data['STATUS']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO dbo.tab_centrocusto (ID_CENTRO_CUSTO, NOME, RESPONSAVEL, STATUS)
            VALUES (?, ?, ?, ?)
        """, id_centro, nome, responsavel, status)
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
            SELECT MARCA, MODELO, ANO, RENAVAM, PLACA, TIPO_COMBUSTIVEL, HODOMETRO_INICIAL, CONDUTOR, TIPO_LOCACAO, DOCUMENTO, STATUS
            FROM dbo.tab_veiculos
        """)
        veiculos = []
        for row in cursor.fetchall():
            veiculos.append({
                "Marca": row.MARCA,
                "Modelo": row.MODELO,
                "Ano": row.ANO,
                "Renavam": row.RENAVAM,
                "Placa": row.PLACA,
                "Tipo_combustivel": row.TIPO_COMBUSTIVEL,
                "Hodometro_inicial": row.HODOMETRO_INICIAL,
                "Motorista": row.CONDUTOR,  # Aqui também
                "Tipo_Locacao": row.TIPO_LOCACAO,
                "Documento": row.DOCUMENTO,
                "Status": row.STATUS    
            })
        conn.close()
        return jsonify(veiculos)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route('/api/veiculos', methods=['POST'])
def adicionar_veiculo():
    try:
        data = request.get_json()
        print("Recebido para inserir:", data)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO dbo.tab_veiculos
            (MARCA, MODELO, ANO, RENAVAM, PLACA, TIPO_COMBUSTIVEL, HODOMETRO_INICIAL, CONDUTOR, TIPO_LOCACAO, DOCUMENTO, STATUS)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        data['MARCA'],
        data['MODELO'],
        data['ANO'],
        data['RENAVAM'],
        data['PLACA'],
        data['TIPO_COMBUSTIVEL'],
        data['HODOMETRO_INICIAL'],
        data['CONDUTOR'],
        data['TIPO_LOCACAO'],
        data['DOCUMENTO'],
        data['STATUS'])
        conn.commit()
        conn.close()
        return jsonify({"mensagem": "Veículo cadastrado com sucesso!"}), 201
    except Exception as e:
        print("ERRO AO INSERIR VEÍCULO:", e)
        return jsonify({"erro": str(e)}), 500


@app.route('/api/veiculos/<placa>', methods=['PUT'])
def atualizar_veiculo(placa):
    try:
        data = request.get_json()
        print("Recebido para atualizar:", placa, data)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE dbo.tab_veiculos
            SET MARCA = ?, MODELO = ?, ANO = ?, RENAVAM = ?, TIPO_COMBUSTIVEL = ?, HODOMETRO_INICIAL = ?, CONDUTOR = ?, TIPO_LOCACAO = ?, DOCUMENTO = ?, STATUS = ?
            WHERE PLACA = ?
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
        senha_hash = generate_password_hash(data['SENHA'])
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO dbo.tab_funcionarios
            (NOME, RG, CPF, CENTRO_CUSTO, CNH, CATEGORIA_CNH, VALIDADE_CNH, NIVEL_ACESSO, DATA_NASCIMENTO, PLACA, ID_CARTAO, EMAIL, SENHA, TELEFONE)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['NOME'],
            data['RG'],
            data['CPF'],
            data['CENTRO_CUSTO'],
            data['CNH'],
            data['CATEGORIA_CNH'],
            data['VALIDADE_CNH'],
            data['NIVEL_ACESSO'],
            data['DATA_NASCIMENTO'],
            data['PLACA'],
            data['ID_CARTAO'],
            data['EMAIL'],
            senha_hash,
            data['TELEFONE']
        ))
        conn.commit()
        conn.close()
        return jsonify({"mensagem": "Funcionário cadastrado com sucesso!"}), 201
    except Exception as e:
        print("ERRO EM /api/funcionarios [POST]:", e)
        return jsonify({"erro": str(e)}), 500


@app.route('/api/funcionarios', methods=['GET'])
def listar_funcionarios():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT CPF, RG, NOME, DATA_NASCIMENTO, NIVEL_ACESSO, CNH, CATEGORIA_CNH, 
                   VALIDADE_CNH, PLACA, CENTRO_CUSTO, ID_CARTAO, STATUS
            FROM dbo.tab_funcionarios
            --WHERE PLACA IS NULL
        """)
        funcionarios = []
        for row in cursor.fetchall():
            funcionarios.append({
                "cpf": row[0],
                "rg": row[1],
                "nome": row[2],
                "data_nascimento": row[3],
                "nivel_acesso": row[4],
                "cnh": row[5],
                "categoria_cnh": row[6],
                "validade_cnh": row[7],
                "placa": row[8],
                "centro_custo": row[9],
                "cartao": row[10],
                "status": row[11]
            })
        conn.close()
        return jsonify(funcionarios)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    

@app.route('/api/funcionarios/<cpf>', methods=['PUT'])
def atualizar_funcionario(cpf):
    try:
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        senha_hash = generate_password_hash(data['senha'])
        cursor.execute("""
            UPDATE dbo.tab_funcionarios
            SET NOME = ?, RG = ?, CENTRO_CUSTO = ?, CNH = ?, CATEGORIA_CNH = ?, VALIDADE_CNH = ?, NIVEL_ACESSO = ?, DATA_NASCIMENTO = ?, PLACA = ?, ID_CARTAO = ?, EMAIL = ?, SENHA = ?, TELEFONE = ?
            WHERE CPF = ?
        """, (
            data['nome'],
            data['rg'],
            data['centro_custo'],
            data['cnh'],
            data['categoria_cnh'],
            data['validade_cnh'],
            data['nivel_acesso'],
            data['data_nascimento'],
            data['placa'],
            data['cartao'],
            data['email'],
            senha_hash,
            data['telefone'],
            cpf
        ))
        conn.commit()
        conn.close()
        return jsonify({"mensagem": "Funcionário atualizado com sucesso!"})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

    
@app.route('/api/envio_km', methods=['POST'])
def cadastrarkm():
    data = request.get_json()
    from datetime import datetime

    data_formatada = datetime.strptime(data['data'], '%Y-%m-%d')
    total_formatado = int(data['kmRodada'])
    if total_formatado < 0: 
        return jsonify({"status": "erro", "mensagem": "A quilometragem não pode ser negativa."}), 400
    

    print(f"Dados recebidos: {data}")
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        try:
            cursor.execute("SELECT CENTRO_CUSTO, NOME, PLACA, ID_CARTAO FROM tab_funcionarios WHERE ID = ?", (session['user_id'],))
            resultado = cursor.fetchone()
            centrocusto = resultado[0]
            nome = resultado[1]
            placa = resultado[2]
            id_cartao = resultado[3]
            base = centrocusto
        except Exception as e:
            print("ERRO AO BUSCAR DADOS DO USUÁRIO:", e)  # <-- Adicione esta linha
            return jsonify({"status": "erro", "mensagem": "Erro ao buscar dados do usuário."}), 500
        try:
            cursor.execute("""
            SELECT TOP 1 HODOMETRO_FINAL
            FROM tab_relatorio
            WHERE PLACA = ?
            ORDER BY DATA DESC, ID DESC
        """, (placa,))
            ultimo_hodometro = cursor.fetchone()
            if ultimo_hodometro:
                ultimo_hodometro = ultimo_hodometro[0]
                print(f"Último hodômetro encontrado: {int(ultimo_hodometro)}, hodometro saída: {int(data['hodometroSaida'])}") 
            if ultimo_hodometro and int(data['hodometroSaida']) < int(ultimo_hodometro[0]):
                return jsonify({"status": "erro", "mensagem": f"Hodômetro atual menor que o último registro: {ultimo_hodometro[0]}."}), 400
        except Exception as e:
            print("ERRO AO BUSCAR ÚLTIMO HODÔMETRO:", e)
            return jsonify({"status": "erro", "mensagem": "Erro ao buscar último hodômetro."}), 500
        try:
            cursor.execute("""
                INSERT INTO tab_relatorio(
                    CENTRO_CUSTO,
                    DATA,
                    NOME,
                    PLACA,
                    BASE,
                    HODOMETRO_INICIAL,
                    HODOMETRO_FINAL,
                    TOTAL,
                    ID_CARTAO,
                    LOCAL_INICIAL,
                    LOCAL_FINAL
                    )VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (centrocusto,
                            data_formatada,
                            nome, 
                            placa,
                            base,
                            data['hodometroSaida'],
                            data['hodometroRetorno'],
                            total_formatado,
                            id_cartao,
                            data['localSaida'],
                            data['localRetorno']))
            conn.commit()
            return jsonify({"status": "ok", "mensagem": "Dados inseridos com sucesso"})
        except Exception as e:
            print("ERRO AO INSERIR DADOS:", e)
            return jsonify({"status": "erro", "mensagem": "Erro ao inserir dados."}), 500
        
    except Exception as e:
        print("ERRO AO INSERIR KM:", e)  # <-- Adicione esta linha
        import traceback
        traceback.print_exc()

        return jsonify({"status": "erro", "mensagem": str(e)}), 500
    

@app.route('/api/envio_abastecimento', methods=['POST'])
def cadastrodeabastecimento():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        hodometro = request.form.get('hodometro')
        combustivel = request.form.get('combustivel')
        litros = request.form.get('litros')
        valor_unitario = request.form.get('valor_unitario')
        valor_total = request.form.get('valor_total')
        comprovante = request.files.get('comprovante')



        cursor.execute("SELECT ID_CARTAO, NOME, PLACA FROM tab_funcionarios WHERE ID = ?", (session['user_id'],))
        dados = cursor.fetchone()
        if not dados:
            return jsonify({"status": "erro", "mensagem": "Cartão não encontrado para o usuário"}), 400
        id_cartao = dados[0]
        nome = dados[1]
        placa = dados[2]

        comprovante_bytes = comprovante.read() if comprovante else None

        cursor.execute("""
            SELECT TOP 1 HODOMETRO
            FROM tab_abastecimento
            WHERE PLACA = ?
            ORDER BY DATA DESC, ID DESC
        """, (placa,))
        ultimo_hodometro = cursor.fetchone()
        if ultimo_hodometro and hodometro < ultimo_hodometro[0]:
            return jsonify({"status": "erro", "mensagem": f"Hodômetro atual menor que o último registro: {ultimo_hodometro[0]}."}), 400

        


        cursor.execute("""
            INSERT INTO tab_abastecimento(
                DATA,
                CONDUTOR,
                HODOMETRO,
                PLACA,
                COMBUSTIVEL,
                LITROS,
                VALOR_UN,
                VALOR_ABASTECIMENTO,
                COMPROVANTE,
                ID_CARTAO
            ) VALUES (
                GETDATE(), ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        """, (
            nome,
            hodometro,
            placa,
            combustivel,
            litros,
            valor_unitario,
            valor_total,
            comprovante_bytes,
            id_cartao
        ))

        conn.commit()
        return jsonify({"status": "ok", "mensagem": "Dados inseridos com sucesso"})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

# ROTAS DE ACESSO AS PÁGINAS #
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM dbo.tab_veiculos")
    total_veiculos = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM dbo.tab_veiculos WHERE Status = 'Inativo'") #ou outro status a definir para veiculos em manutenção

    total_veiculos_inativos = cursor.fetchone()[0]
    cursor.execute("""
    SELECT COUNT(*) FROM dbo.tab_abastecimento
""")
    total_abastecimento = cursor.fetchone()[0] or 0
    return render_template('home.html', total_veiculos=total_veiculos, total_veiculos_inativos=total_veiculos_inativos, total_abastecimento=total_abastecimento)

@app.route('/editarviagem')
def editarviagem():
    #TODO carregar os dados de edição conforme usuário que fez login
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('editar_viagem.html')



@app.route('/login' , methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['emaillogin']
        senha = request.form['password']

        if not email or not senha:
            return redirect(url_for('login'))
        

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM dbo.tab_funcionarios WHERE Email = ?", email)
        usuario = cursor.fetchone()
        conn.close()
        if usuario:
            if check_password_hash(usuario[13], senha):
                session.permanent = True
                session['user_id'] = usuario[0]
                session['acesso'] = usuario[8]
                session['user_name'] = usuario[1]

                if session['acesso'] == "Motorista":
                    return redirect(url_for('cadastroabastecimento'))

                return redirect(url_for('index'))
            else:
                logging.warning(f"Senha incorreta para o usuário: {email}")
                return render_template('Frota.index.html', error='Senha incorreta')
           
        else:
            logging.warning(f"Usuário não encontrado: {email}")
            return render_template('Frota.index.html', error='Usuário não encontrado')
        
    return render_template('Frota.index.html')


@app.route('/cadastroabastecimento')
def cadastroabastecimento():
    #TODO carregar os dados de edição conforme usuário que fez login
    # Verifica se o usuário está logado

    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Verifica se o usuário tem acesso de motorista
    if session.get('acesso') == 'Motorista':
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT Placa FROM dbo.tab_funcionarios WHERE ID = ?", session['user_id'])
        placa = cursor.fetchone()[0]
        cursor.execute("SELECT NUMERO_CARTAO, VALIDADE_CARTAO FROM dbo.tab_cartao WHERE PLACA_CARTAO = ?", placa)
        dados = cursor.fetchone()
        if not dados:
            return render_template('cadastro_abastecimento.html', error='Cartão não encontrado para o veículo associado ao usuário.')
        id_cartao = dados[0]
        validade_cartao = dados[1]
        cursor.execute("SELECT DATA, VALOR_ABASTECIMENTO FROM dbo.tab_abastecimento WHERE ID_CARTAO = ? ORDER BY DATA DESC", placa)
        abastecimentos = cursor.fetchall()
        if not abastecimentos:
            return render_template('cadastro_abastecimento.html', id_cartao=id_cartao, placa=placa, validade_cartao=validade_cartao)


        abastecimentos = [{'data': ab[0], 'valor': ab[1]} for ab in abastecimentos]
        conn.commit()
        conn.close()

        return render_template('cadastro_abastecimento.html', id_cartao=id_cartao, placa=placa, validade_cartao=validade_cartao, abastecimentos=abastecimentos)

    return render_template('cadastro_abastecimento.html')


@app.route('/cadastrokm')
def cadastrokm():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('cadastro_km.html')

#LISTAR RELATÓRIOS ABAIXO ---------------------------------------------------------------------------------------------

@app.route('/relatorios')
def relatorios():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT CENTRO_CUSTO, DATA, NOME, PLACA, BASE, HODOMETRO_INICIAL, HODOMETRO_FINAL, TOTAL, ID_CARTAO, LOCAL_INICIAL, LOCAL_FINAL FROM tab_relatorio")
    relatorios = []
    for row in cursor.fetchall():
        relatorios.append({
            'centrocusto' : row[0],
            'data' : row[1],
            'nome' : row[2],
            'placa' : row[3],
            'base' : row[4],
            'hodometro_inicial': row[5],
            'hodometro_final' : row[6],
            'total' : row[7],
            'id_cartao':row[8],
            'local_inicial': row[9],
            'local_final' :row[10]

        })
    return render_template('relatorios.html', relatorios=relatorios)


@app.route('/api/relatorios', methods=['GET'])
def listar_relatorios():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ID, CENTRO_CUSTO, DATA, NOME, PLACA, BASE, HODOMETRO_INICIAL, HODOMETRO_FINAL, TOTAL, ID_CARTAO, LOCAL_INICIAL, LOCAL_FINAL
            FROM dbo.tab_relatorio
        """)
        relatorios = []
        for row in cursor.fetchall():
            relatorios.append({
                "id": row[0],
                "centro_custo": row[1],
                "data": str(row[2]),
                "nome": row[3],
                "placa": row[4],
                "base": row[5],
                "hodometro_inicial": row[6],
                "hodometro_final": row[7],
                "total": row[8],
                "id_cartao": row[9],
                "local_inicial": row[10],
                "local_final": row[11]
            })
        conn.close()
        return jsonify(relatorios)
    except Exception as e:
        print("ERRO EM /api/relatorios:", e)
        return jsonify({"erro": str(e)}), 500


@app.route('/api/relatorios/<int:id>', methods=['PUT'])
def atualizar_relatorio(id):
    try:
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE dbo.tab_relatorio
            SET CENTRO_CUSTO=?, DATA=?, NOME=?, PLACA=?, BASE=?, HODOMETRO_INICIAL=?, HODOMETRO_FINAL=?, TOTAL=?, ID_CARTAO=?, LOCAL_INICIAL=?, LOCAL_FINAL=?
            WHERE ID=?
        """, (
            data['centro_custo'],
            data['data'],
            data['nome'],
            data['placa'],
            data['base'],
            data['hodometro_inicial'],
            data['hodometro_final'],
            data['total'],
            data['id_cartao'],
            data['local_inicial'],
            data['local_final'],
            id
        ))
        conn.commit()
        conn.close()
        return jsonify({"mensagem": "Relatório atualizado com sucesso!"})
    except Exception as e:
        print("ERRO EM /api/relatorios/<id>:", e)
        return jsonify({"erro": str(e)}), 500


@app.route('/veiculos')
def veiculos():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session.get('acesso') != 'operador':
        return render_template('veiculos.html')
    else:
        return redirect(url_for('index'))
    

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/abastecimento')
def abastecimento():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session.get('acesso') != 'operador':
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tab_abastecimento ORDER BY DATA DESC")
        #SELECT ID, DATA, CONDUTOR, HODOMETRO, PLACA, COMBUSTIVEL, LITROS, VALOR_UN, VALOR_ABASTECIMENTO, COMPROVANTE, ID_CARTAO
        abastecimentos = cursor.fetchall()
        conn.close()
        return render_template('abastecimento.html', abastecimentos=abastecimentos)
    else:
        return redirect(url_for('index'))


@app.route('/usuarios')
def usuarios():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session.get('acesso') != 'operador':
        return render_template('usuarios.html')
    else:
        return redirect(url_for('index'))


@app.route('/usuarios_principal')
def usuarios_principal():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session.get('acesso') != 'operador':
        return render_template('usuarios-principal.html')
    else:
        return redirect(url_for('index'))


@app.route('/centrocusto')
def centrocusto():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session.get('acesso') != 'operador':
        return render_template('cc.html')
    else:
        return redirect(url_for('index'))
    

@app.route('/base')
def base():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session.get('acesso') != 'operador':
       
        
            
        return render_template('base.html')
    else:
        
        return redirect(url_for('index'))


@app.route('/cartaocombustivel')
def cartaocombustivel():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session.get('acesso') != 'operador':
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""SELECT NOME_BASE FROM tab_base""")
        bases = []
        for row in cursor.fetchall():
            bases.append({
                'Nome':row[0]
            })

        cursor.execute("""SELECT PLACA, MODELO FROM tab_veiculos """)
                       # WHERE CARTAO_ATIVO <> 1
        veiculos = []
        for row in cursor.fetchall():
            veiculos.append({
                'Placa':row[0],
                'Modelo':row[1]
            })

        return render_template('cartao_novo.html', bases=bases,veiculos=veiculos)
    else:
        return redirect(url_for('index'))


@app.route('/recebimentocartao')
def recebimentocartao():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session.get('acesso') != 'operador':
        return render_template('recebimento_cartao.html')
    else:
        return redirect(url_for('index'))
    
@app.route('/listacartoes')
def listacartoes():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session.get('acesso') != 'operador':
        return render_template('lista_cartoes.html')
    else:
        return redirect(url_for('index'))
    
@app.route('/veiculossecundaria')
def veiculossecundaria():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session.get('acesso') != 'operador':
        return render_template('veiculos_secundaria.html')
    else:
        return redirect(url_for('index'))
    
@app.route('/api/abastecimentos/<int:id>', methods=['POST'])
def atualizar_abastecimento(id):
    try:
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()

        # Se comprovante vier no JSON e não for vazio, atualiza; senão, não altera o campo
        if 'comprovante' in data and data['comprovante']:
            cursor.execute("""
                UPDATE dbo.tab_abastecimento
                SET DATA = ?, CONDUTOR = ?, HODOMETRO = ?, PLACA = ?, COMBUSTIVEL = ?, LITROS = ?, VALOR_UN = ?, VALOR_ABASTECIMENTO = ?, COMPROVANTE = ?, ID_Cartao = ?
                WHERE ID = ?
            """, (
                data['data'],
                data['condutor'],
                data['hodometro'],
                data['placa'],
                data['combustivel'],
                data['litros'],
                data['valor_un'],
                data['valor_abastecimento'],
                data['comprovante'],
                data['id_cartao'],
                id
            ))
        else:
            cursor.execute("""
                UPDATE dbo.tab_abastecimento
                SET DATA = ?, CONDUTOR = ?, HODOMETRO = ?, PLACA = ?, COMBUSTIVEL = ?, LITROS = ?, VALOR_UN = ?, VALOR_ABASTECIMENTO = ?, ID_Cartao = ?
                WHERE ID = ?
            """, (
                data['data'],
                data['condutor'],
                data['hodometro'],
                data['placa'],
                data['combustivel'],
                data['litros'],
                data['valor_un'],
                data['valor_abastecimento'],
                data['id_cartao'],
                id
            ))

        conn.commit()
        conn.close()
        return jsonify({"mensagem": "Abastecimento atualizado com sucesso!"})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/Veiculos.html')
def veiculos_html():
    return render_template('Veiculos.html')

# APLICAÇÃO ABAIXO É REFERENTE A PAGINA "CARTÕES"----------------------------------------------------------------

@app.route('/salvar-cartao', methods=['POST'])
def salvar_cartao():
    try:
        data = request.get_json()
        placa = data.get('placa_cartao')
        marca = data.get('marca')
        base = data.get('base')
        centro_custo = data.get('centro_custo')
        status = data.get('status')

        # Conecte ao banco e insira os dados
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO dbo.tab_cartao (PLACA_CARTAO, MARCA, BASE, CENTRO_CUSTO, STATUS)
            VALUES (?, ?, ?, ?, ?)
        """, (placa, marca, base, centro_custo, status))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Cartão salvo com sucesso!'}), 200
    except Exception as e:
        return jsonify({'message': f'Erro ao salvar: {str(e)}'}), 500

@app.route('/api/solicitacoes-pendentes')
def api_solicitacoes_pendentes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DATA_SOLICITACAO, PLACA_CARTAO, BASE, MARCA, CENTRO_CUSTO, STATUS
        FROM dbo.tab_cartao
        WHERE STATUS = 'Pendente'
    """)
    rows = cursor.fetchall()
    conn.close()
    result = []
    for row in rows:
        result.append({
            "data_solicitacao": row.DATA_SOLICITACAO.strftime('%d/%m/%Y') if hasattr(row.DATA_SOLICITACAO, 'strftime') else str(row.DATA_SOLICITACAO),
            "placa_cartao": row.PLACA_CARTAO,
            "base": row.BASE,
            "marca": row.MARCA,
            "centro_custo": row.CENTRO_CUSTO,
            "status": row.STATUS
        })
    return jsonify(result)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)