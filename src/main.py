import pandas as pd
import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import time
import threading

# === MODO DE DESENVOLVIMENTO ===
DEBUG = True

if not DEBUG:
    import pywhatkit as kit

# Caminho do log
LOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'logs', 'enviado.log')

def enviar_mensagens(caminho_arquivo, status_label):
    try:
        status_label.config(text="Lendo planilha...", fg="blue")

        df = pd.read_excel(caminho_arquivo)
        df.columns = df.columns.str.strip().str.lower()

        nome_coluna = next((col for col in df.columns if "nome" in col), None)
        telefone_coluna = next((col for col in df.columns if "telefone" in col), None)
        vencimento_coluna = next((col for col in df.columns if "vencimento" in col), None)
        valor_coluna = next((col for col in df.columns if "valor" in col), None)

        if not all([nome_coluna, telefone_coluna, vencimento_coluna, valor_coluna]):
            raise ValueError("Colunas obrigatórias não encontradas na planilha.")

        df[vencimento_coluna] = pd.to_datetime(df[vencimento_coluna], errors='coerce').dt.date
        hoje = datetime.date.today()

        clientes_hoje = df[df[vencimento_coluna] == hoje]

        if clientes_hoje.empty:
            status_label.config(text="Nenhum vencimento para hoje.", fg="orange")
            return

        with open(LOG_PATH, "a") as log:
            for idx, row in clientes_hoje.iterrows():
                nome = row[nome_coluna]
                telefone = str(row[telefone_coluna])
                vencimento = row[vencimento_coluna].strftime("%d/%m/%Y")
                valor = float(row[valor_coluna])

                mensagem = f"""
Olá, {nome}

Esta é uma gentil lembrança, percebemos que há título da sua operação de crédito com vencimento para hoje, {vencimento}, no valor de R$ {valor:.2f}. Gostaria de receber novamente o boleto ou a chave PIX para pagamento?

ATENÇÃO: ANTES DE EFETUAR O PAGAMENTO VERIFIQUE O NOME DO BENEFICIÁRIO.

Lembramos que a falta de pagamento na data de vencimento implica aplicação de multa e demais encargos contratuais e legais.

Contamos com você,

Atenciosamente,

Cactos Crédito Fácil
"""

                if DEBUG:
                    print(f"[SIMULADO] Enviaria para {telefone}:\n{mensagem}\n")
                    log.write(f"[SIMULADO] {nome} ({telefone}) - {vencimento}\n")
                else:
                    hora = datetime.datetime.now().hour
                    minuto = datetime.datetime.now().minute + 2
                    status_label.config(text=f"Enviando para {nome}...", fg="blue")
                    kit.sendwhatmsg(f"+{telefone}", mensagem, hora, minuto)
                    log.write(f"[{datetime.datetime.now()}] Enviado para {nome} ({telefone})\n")
                    time.sleep(10)

        status_label.config(text="Processo concluído com sucesso!", fg="green")

    except Exception as e:
        status_label.config(text=f"Erro: {str(e)}", fg="red")

def escolher_arquivo(entry, status_label):
    caminho = filedialog.askopenfilename(
        title="Selecione a planilha",
        filetypes=[("Planilhas Excel", "*.xlsx")]
    )
    if caminho:
        entry.delete(0, tk.END)
        entry.insert(0, caminho)
        status_label.config(text="Arquivo carregado, pronto para envio.", fg="black")

def iniciar_envio(entry, status_label):
    caminho = entry.get()
    if not caminho:
        messagebox.showwarning("Atenção", "Selecione uma planilha primeiro.")
        return

    thread = threading.Thread(target=enviar_mensagens, args=(caminho, status_label))
    thread.start()

# GUI
root = tk.Tk()
root.title("Notificador WhatsApp - Cactos Crédito Fácil")
root.geometry("600x250")
root.resizable(False, False)

tk.Label(root, text="Selecione a planilha de clientes:").pack(pady=10)

frame = tk.Frame(root)
frame.pack()

entry = tk.Entry(frame, width=60)
entry.pack(side=tk.LEFT, padx=5)

btn_browse = tk.Button(frame, text="Procurar", command=lambda: escolher_arquivo(entry, status_label=None))
btn_browse.pack(side=tk.LEFT)

status_label = tk.Label(root, text="", fg="black")
status_label.pack(pady=10)

btn_enviar = tk.Button(root, text="Enviar Mensagens", bg="#28a745", fg="white",
                       command=lambda: iniciar_envio(entry, status_label))
btn_enviar.pack(pady=5)

status_label = tk.Label(root, text="", fg="black")
status_label.pack()

root.mainloop()
