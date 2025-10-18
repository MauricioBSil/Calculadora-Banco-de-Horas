import sqlite3
from datetime import datetime, timedelta

#tabelas

def get_connection():
    con = sqlite3.connect("calculadora_bh.db")
    return con

def inicializar_db():
    con = get_connection()
    cur = con.cursor()


    cur.execute("""
    CREATE TABLE IF NOT EXISTS banco_de_hora (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                data TEXT NOT NULL,
                entrada TEXT NOT NULL,
                k3_ida  TEXT NOT NULL,
                k3_volta TEXT NOT NULL,
                saida TEXT NOT NULL,
                total_trabalhado TEXT NOT NULL,
                hora_extra TEXT NOT NULL,
                hora_negativa TEXT NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id))
            """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf INTEGER NOT NULL,
                gmid TEXT NOT NULL)
                """)
    con.commit()
    con.close()

#funções

#listar usuarios cadastrados

def listar_usuarios():
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT id, nome, cpf, gmid FROM usuarios")
    usuarios = cur.fetchall()

    if not usuarios:
        print("Nenhum usuário cadastrado.")
    else:
        print("/// Usuários Cadastrados ///")
        for u in usuarios:
            print(f"ID: {u[0]} | Nome: {u[1]} | CPF: {u[2]} | Mateus Id: {u[3]}")
    return usuarios

def calcular_jornada(data_str, entrada_str, k3_ida_str, k3_volta_str, saida_str):
    jornada_minima = timedelta(hours=7, minutes=20)

    FORMATO_HORA = "%H:%M"
    FORMATO_DATA = "%d/%m/%Y"

    #converte str para datetime
    data_base = datetime.strptime(data_str, FORMATO_DATA).date()
    
    entrada = datetime.combine(data_base, datetime.strptime(entrada_str, FORMATO_HORA).time())
    k3_ida   = datetime.combine(data_base, datetime.strptime(k3_ida_str, FORMATO_HORA).time())
    k3_volta = datetime.combine(data_base, datetime.strptime(k3_volta_str, FORMATO_HORA).time())
    saida = datetime.combine(data_base, datetime.strptime(saida_str, FORMATO_HORA).time())

    #cacular intervalos de trabalho
    periodo_1 = k3_ida - entrada
    periodo_2 = saida - k3_volta
    total_trabalhado = periodo_1 + periodo_2
    diferenca = total_trabalhado - jornada_minima

    hora_extra = timedelta(0)
    hora_negativa = timedelta(0)

    if diferenca > timedelta(0):
        hora_extra = diferenca
    elif diferenca < timedelta(0):
        hora_negativa = -diferenca

    return str(total_trabalhado), str(hora_extra), str(hora_negativa)

#cadastro de pontos
def cadastrar_pontos():
    print("--- Cadastro de pontos ---")
    usuarios = listar_usuarios()
    if not usuarios:
        print("Nenhum usuário cadastrado. Faça o Cadastro e tente novamente.")
        return
    try:
        usuario_id = int(input("Informe o Id do usuário: "))
    except ValueError:
        print("ID de usuário inválido. Digite apenas números.")
        return

    #verificar se usuario existe
    if not any(u[0] == usuario_id for u in usuarios):
        print("Usuário não encontrado, verifique o cadastro.")
        return
    data = input("Informe a Data (DD/MM/AAA): ")
    entrada = input("Informe o horario de Entrada (HH:MM): ")
    k3_ida = input("Informe o horario de ida ao K3 (HH:MM): ")
    k3_volta = input("Informe o horario de volta do K3 (HH:MM): ")
    saida = input("Informe o horario ded Saída (HH:MM): ")

    #validar formato
    try:
        datetime.strptime(data, "%d/%m/%Y")
        datetime.strptime(entrada, "%H:%M")
        datetime.strptime(k3_ida, "%H:%M")
        datetime.strptime(k3_volta, "%H:%M")
        datetime.strptime(saida, "%H:%M")
    except ValueError:
        print("Data ou Hora Inválida. Verifique o formato inserido.")
        return
    
    
    #integração do calculo
    try: 
        total_trabalhado, hora_extra, hora_negativa = calcular_jornada( data, entrada, k3_ida, k3_volta, saida)

        print("\n--- Resumo do Ponto ---")
        print(f"Total Trabalhado: {total_trabalhado}")
        print(f"Horas Extras: {hora_extra}")
        print(f"Horas Negativas: {hora_negativa}")

    except Exception as e:
        print(f"Erro ao calcular jornada: {e}")
        return

    con = get_connection()
    cur = con.cursor()
    cur.execute("INSERT INTO banco_de_hora (usuario_id, data, entrada, k3_ida, k3_volta, saida, total_trabalhado, hora_extra, hora_negativa) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                (usuario_id, data, entrada, k3_ida, k3_volta, saida, total_trabalhado, hora_extra, hora_negativa))
    con.commit()
    con.close()
    print("Ponto(s) cadastrado(s) com sucesso!")

#cadastro de usuarios
def cadastrar_usuario():
    print("/// Cadastro de Usuário ///")
    nome = input("Nome Completo: ")

    try:
        cpf = int(input("CPF (somente numeros): "))
    except ValueError:
        print("CPF inválido. Digite apenas números.")
        return
    
    gmid = input("Mateus Id (padrão GmXXXXXX): ")
    print("Usuário cadastrado com sucesso!")

    con = get_connection()
    cur = con.cursor()
    cur.execute("INSERT INTO usuarios (nome, cpf, gmid) VALUES (?, ?, ?)", (nome, cpf, gmid))
    con.commit()
    con.close()

#pesquisa de usuarios
def buscar_usuario():
    gmid = input("Informe o Mateus Id desejado: ")
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM usuarios WHERE gmid LIKE ?", (f"%{gmid}",))
    usuarios = cur.fetchone()
    con.close()

    if usuarios:
        print("/// Usuário encontrado ///")
        print(f"ID: {usuarios[0]} | Nome: {usuarios[1]} | CPF: {usuarios[2]} | Mateus Id: {usuarios[3]}")
    else:
        print("Usuario não encontrado! Verifique os dados ou cadastre o usuário.")

def menu():
    print("/// Menu Principal ///")
    print("1. Cadastrar Usuário")
    print("2. Cadastrar pontos")
    print("3. Usuários Cadastrados")
    print("0. Sair")
    try:
        return int(input("Escolha uma opção: "))
    except ValueError: 
        return -1

if __name__ =="__main__":
    inicializar_db()
    while True:
        try:
            opcao = menu()
            if opcao == 1:
                cadastrar_usuario()
            elif opcao == 2:
                cadastrar_pontos()
            elif opcao == 3:
                listar_usuarios()
            elif opcao == 0:
                break
            elif opcao == -1:
                print("Opção inválida!")

        except ValueError:
            print("Desculpe, opção inválida. Tente novamente.")