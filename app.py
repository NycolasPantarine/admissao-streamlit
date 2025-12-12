import streamlit as st
import pandas as pd
import os
import zipfile
import smtplib
from email.message import EmailMessage
from datetime import datetime
from io import BytesIO

# ===============================
# CONFIGURAÇÃO DA PÁGINA
# ===============================
st.set_page_config(
    page_title="Formulário de Admissão",
    layout="centered"
)

st.title("📋 Formulário de Admissão")

# ===============================
# FUNÇÃO DE ENVIO DE EMAIL
# ===============================
def enviar_email(destinatario, assunto, corpo, anexos):
    msg = EmailMessage()
    msg["From"] = st.secrets["SMTP_FROM"]
    msg["To"] = destinatario
    msg["Subject"] = assunto
    msg.set_content(corpo)

    for nome, conteudo, mime in anexos:
        tipo, subtipo = mime.split("/")
        msg.add_attachment(
            conteudo,
            maintype=tipo,
            subtype=subtipo,
            filename=nome
        )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(
            st.secrets["SMTP_USER"],
            st.secrets["SMTP_PASS"]
        )
        server.send_message(msg)

# ===============================
# FORMULÁRIO
# ===============================
with st.form("form_admissao"):
    st.subheader("Dados Pessoais")

    nome = st.text_input("Nome Completo *")
    cpf = st.text_input("CPF * (somente números)")
    data_nasc = st.date_input("Data de Nascimento *")
    sexo = st.selectbox("Sexo *", ["", "Masculino", "Feminino", "Outro"])
    estado_civil = st.selectbox("Estado Civil *", ["", "Solteiro(a)", "Casado(a)", "Divorciado(a)", "Viúvo(a)"])
    email_pessoal = st.text_input("E-mail Pessoal *")
    celular = st.text_input("Celular *")

    st.subheader("Endereço")
    cep = st.text_input("CEP")
    logradouro = st.text_input("Logradouro")
    numero = st.text_input("Número")
    bairro = st.text_input("Bairro")

    st.subheader("Documentos Obrigatórios")
    cpf_file = st.file_uploader("CPF (PDF/JPG/PNG) *", type=["pdf", "jpg", "png"])
    rg_file = st.file_uploader("RG (PDF/JPG/PNG) *", type=["pdf", "jpg", "png"])
    ctps_file = st.file_uploader("Carteira de Trabalho (PDF/JPG/PNG) *", type=["pdf", "jpg", "png"])

    enviar = st.form_submit_button("📨 Enviar Admissão")

# ===============================
# PROCESSAMENTO
# ===============================
if enviar:
    if not all([nome, cpf, email_pessoal, celular, cpf_file, rg_file, ctps_file]):
        st.error("❌ Preencha todos os campos obrigatórios.")
        st.stop()

    # -------------------------------
    # CRIA DATAFRAME
    # -------------------------------
    dados = {
        "Nome Completo": nome,
        "CPF": cpf,
        "Data Nascimento": data_nasc.strftime("%d/%m/%Y"),
        "Sexo": sexo,
        "Estado Civil": estado_civil,
        "E-mail": email_pessoal,
        "Celular": celular,
        "CEP": cep,
        "Logradouro": logradouro,
        "Número": numero,
        "Bairro": bairro,
        "Data Envio": datetime.now().strftime("%d/%m/%Y %H:%M")
    }

    df = pd.DataFrame([dados])

    # -------------------------------
    # GERA EXCEL EM MEMÓRIA
    # -------------------------------
    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False)
    excel_bytes = excel_buffer.getvalue()

    # -------------------------------
    # CRIA ZIP EM MEMÓRIA (BINÁRIO)
    # -------------------------------
    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr("Documentos/CPF.pdf", cpf_file.getvalue())
        zipf.writestr("Documentos/RG.pdf", rg_file.getvalue())
        zipf.writestr("Documentos/CTPS.pdf", ctps_file.getvalue())

    zip_bytes = zip_buffer.getvalue()

    # -------------------------------
    # ENVIO DE EMAIL
    # -------------------------------
    assunto = f"Nova Admissão Polachini – {nome}"

    corpo = f"""
Olá,

Uma nova admissão foi enviada pelo formulário.

Nome: {nome}
CPF: {cpf}

Em anexo:
- Planilha com os dados preenchidos
- Documentação do colaborador (ZIP)

Atenciosamente,
Sistema de Admissão – Futto RH
"""

    anexos = [
        ("Dados_Admissao.xlsx", excel_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
        ("Documentacao.zip", zip_bytes, "application/zip")
    ]

    enviar_email(
        destinatario="nycolas.pantarine@futtorh.com.br",
        assunto=assunto,
        corpo=corpo,
        anexos=anexos
    )

    st.success("✅ Admissão enviada com sucesso! E-mail disparado.")
