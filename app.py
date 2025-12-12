import streamlit as st
import pandas as pd
import smtplib
import zipfile
from email.message import EmailMessage
from datetime import datetime
from io import BytesIO

# ===============================
# CONFIGURAÇÃO
# ===============================
st.set_page_config(page_title="Formulário de Admissão", layout="centered")
st.title("📋 Formulário de Admissão")

# ===============================
# FUNÇÃO EMAIL
# ===============================
def enviar_email(destinatario, assunto, corpo, anexos):
    msg = EmailMessage()
    msg["From"] = st.secrets["SMTP_FROM"]
    msg["To"] = destinatario
    msg["Subject"] = assunto
    msg.set_content(corpo)

    for nome, conteudo, mime in anexos:
        tipo, subtipo = mime.split("/")
        msg.add_attachment(conteudo, maintype=tipo, subtype=subtipo, filename=nome)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(st.secrets["SMTP_USER"], st.secrets["SMTP_PASS"])
        server.send_message(msg)

# ===============================
# DADOS DO COLABORADOR (FORA DO FORM)
# ===============================
st.subheader("👤 Dados do Colaborador")

nome = st.text_input("Nome Completo *")
cpf = st.text_input("CPF *")
data_nasc = st.date_input("Data de Nascimento *")
sexo = st.selectbox("Sexo *", ["Masculino", "Feminino", "Outro"])
estado_civil = st.selectbox(
    "Estado Civil *",
    ["Solteiro(a)", "Casado(a)", "Divorciado(a)", "Viúvo(a)"]
)

filiacao1 = st.text_input("Filiação 1 *")
filiacao2 = st.text_input("Filiação 2")

# ===============================
# DOCUMENTOS COLABORADOR
# ===============================
st.subheader("📄 Documentos do Colaborador")

cpf_file = st.file_uploader("CPF *", type=["pdf", "jpg", "png"])
rg_file = st.file_uploader("RG *", type=["pdf", "jpg", "png"])
ctps_file = st.file_uploader("CTPS *", type=["pdf", "jpg", "png"])

# ===============================
# DEPENDENTES — DINÂMICO (FORA DO FORM)
# ===============================
st.subheader("👶 Dependentes")

possui_dependentes = st.checkbox("Possui dependentes?")
dependentes = []

if possui_dependentes:
    qtd_dep = st.number_input("Quantidade de dependentes", 1, 5, 1)

    for i in range(int(qtd_dep)):
        st.markdown(f"### Dependente {i+1}")

        dep_nome = st.text_input("Nome", key=f"dep_nome_{i}")
        dep_cpf = st.text_input("CPF", key=f"dep_cpf_{i}")
        dep_data = st.date_input("Data de Nascimento", key=f"dep_data_{i}")
        dep_sexo = st.selectbox("Sexo", ["Masculino", "Feminino", "Outro"], key=f"dep_sexo_{i}")
        dep_parentesco = st.text_input("Parentesco", key=f"dep_parentesco_{i}")
        dep_filiacao = st.text_input("Filiação", key=f"dep_filiacao_{i}")
        dep_ir = st.checkbox("Entra no IR", key=f"dep_ir_{i}")
        dep_sf = st.checkbox("Salário Família", key=f"dep_sf_{i}")

        dep_doc = st.file_uploader(
            "Documento do Dependente",
            type=["pdf", "jpg", "png"],
            key=f"dep_doc_{i}"
        )

        dependentes.append({
            "Nome": dep_nome,
            "CPF": dep_cpf,
            "Nascimento": dep_data.strftime("%d/%m/%Y"),
            "Sexo": dep_sexo,
            "Parentesco": dep_parentesco,
            "Filiação": dep_filiacao,
            "IR": dep_ir,
            "Salário Família": dep_sf,
            "Arquivo": dep_doc
        })

# ===============================
# BOTÃO DE ENVIO (ÚNICO SUBMIT)
# ===============================
st.markdown("---")
enviar = st.button("📨 Enviar Admissão")

# ===============================
# PROCESSAMENTO
# ===============================
if enviar:
    if not all([nome, cpf, filiacao1, cpf_file, rg_file, ctps_file]):
        st.error("❌ Preencha todos os campos obrigatórios.")
        st.stop()

    # Excel
    df_colab = pd.DataFrame([{
        "Nome": nome,
        "CPF": cpf,
        "Nascimento": data_nasc.strftime("%d/%m/%Y"),
        "Sexo": sexo,
        "Estado Civil": estado_civil,
        "Filiação 1": filiacao1,
        "Filiação 2": filiacao2,
        "Data Envio": datetime.now().strftime("%d/%m/%Y %H:%M")
    }])

    df_dep = pd.DataFrame(dependentes) if dependentes else pd.DataFrame()

    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
        df_colab.to_excel(writer, index=False, sheet_name="Colaborador")
        if not df_dep.empty:
            df_dep.drop(columns=["Arquivo"]).to_excel(writer, index=False, sheet_name="Dependentes")

    excel_bytes = excel_buffer.getvalue()

    # ZIP
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr(f"CPF_{cpf_file.name}", cpf_file.getvalue())
        zipf.writestr(f"RG_{rg_file.name}", rg_file.getvalue())
        zipf.writestr(f"CTPS_{ctps_file.name}", ctps_file.getvalue())

        for i, d in enumerate(dependentes):
            if d["Arquivo"]:
                zipf.writestr(f"Dependente_{i+1}_{d['Arquivo'].name}", d["Arquivo"].getvalue())

    zip_bytes = zip_buffer.getvalue()

    enviar_email(
        "nycolas.pantarine@futtorh.com.br",
        f"Nova Admissão Polachini – {nome}",
        "Nova admissão enviada.",
        [
            ("Dados_Admissao.xlsx", excel_bytes,
             "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
            ("Documentacao.zip", zip_bytes, "application/zip")
        ]
    )

    st.success("✅ Admissão enviada com sucesso!")
