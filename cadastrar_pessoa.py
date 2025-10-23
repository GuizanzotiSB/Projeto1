import face_recognition
import numpy as np
import psycopg2
import os
from dotenv import load_dotenv  # <-- Importamos a biblioteca aqui
import sys # Para parar o script se a senha não for encontrada

# -----------------------------------------------------------------
# CARREGANDO A SENHA DE FORMA SEGURA (IGUAL AO OUTRO SCRIPT)
# -----------------------------------------------------------------
load_dotenv()  # Carrega as variáveis do arquivo .env

# Lê a senha do arquivo .env que você criou
SENHA_DO_BANCO = os.getenv("DB_PASSWORD")

if not SENHA_DO_BANCO:
    print("="*50)
    print("ERRO: Senha do banco de dados não encontrada!")
    print("Verifique se você criou o arquivo '.env' e colocou DB_PASSWORD='sua_senha' nele.")
    print("="*50)
    sys.exit() # Para o script
# -----------------------------------------------------------------


def conectar_bd():
    """Conecta ao banco de dados PostgreSQL."""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="reconhecimento_db", 
            user="postgres", 
            password=SENHA_DO_BANCO # <-- Agora usa a senha segura
        )
        return conn
    except psycopg2.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

def cadastrar_novo_funcionario(nome, caminho_foto):
    """Carrega uma foto, gera o encoding e salva no banco de dados."""
    
    print(f"Processando foto: {caminho_foto}...")
    
    try:
        imagem = face_recognition.load_image_file(caminho_foto)
        encoding = face_recognition.face_encodings(imagem)[0]
    except IndexError:
        print(f"Erro: Nenhum rosto foi encontrado em {caminho_foto}.")
        return
    except Exception as e:
        print(f"Erro ao processar a imagem: {e}")
        return

    encoding_binario = encoding.tobytes()
    
    conn = conectar_bd()
    if conn is None:
        return

    try:
        with conn.cursor() as cur:
            sql = "INSERT INTO funcionarios (nome, encoding_facial) VALUES (%s, %s)"
            cur.execute(sql, (nome, encoding_binario))
        
        conn.commit() 
        print(f"Sucesso! Funcionário '{nome}' cadastrado no banco de dados.")
    
    except psycopg2.Error as e:
        print(f"Erro ao salvar no banco de dados: {e}")
        conn.rollback() 
    finally:
        if conn:
            conn.close()

# --- PONTO DE EXECUÇÃO PRINCIPAL ---
if __name__ == "__main__":
    
    caminho_base = r"C:\Users\guilh\Desktop\projeto_reconhecimento_facial"
    
    # Verifique se os nomes dos arquivos estão corretos aqui
    pessoas_para_cadastrar = [
        ("caio", "pessoas_conhecidas/caio.jpg.jpeg"),
        ("guilherme", "pessoas_conhecidas/guilherme.jpg.jpeg"),
        ("joao", "pessoas_conhecidas/joao.jpg.jpeg"),
        ("pedro", "pessoas_conhecidas/pedro.jpg.jpeg")
    ]
    
    print("Iniciando cadastro em lote no Banco de Dados...")
    
    for nome, arquivo_foto in pessoas_para_cadastrar:
        caminho_completo_foto = os.path.join(caminho_base, arquivo_foto)
        if os.path.exists(caminho_completo_foto):
            cadastrar_novo_funcionario(nome, caminho_completo_foto)
        else:
            print(f"Erro Crítico: Arquivo não encontrado em {caminho_completo_foto}. Verifique o nome.")
        print("-" * 20)

    print("Cadastro em lote finalizado.")
    print("Verifique seu pgAdmin para ver os dados na tabela 'funcionarios'.")