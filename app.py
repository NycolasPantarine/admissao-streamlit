import streamlit as st
import pandas as pd
import smtplib
import zipfile
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
    # -------------------------------
    # DADOS PESSOAIS
    # -------------------------------
    st.subheader("👤 Dados Pessoais")

    nome = st.text_input("Nome Completo *")
    cpf = st.text_input("CPF * (somente números)")
    data_nasc = st.date_input("Data de Nascimento *")
    sexo = st.selectbox("Sexo *", ["Masculino", "Feminino", "Outro"])
    estado_civil = st.selectbox(
        "Estado Civil *",
        ["Solteiro(a)", "Casado(a)", "Divorciado(a)", "Viúvo(a)"]
    )
    pais_nascimento = st.text_input("País de Nascimento")
    nacionalidade = st.text_input("Nacionalidade")
    raca_cor = st.selectbox(
        "Raça/Cor",
        ["Branca", "Preta", "Parda", "Amarela", "Indígena", "Não informado"]
    )

    filiacao1 = st.text_input("Filiação 1 *")
    filiacao2 = st.text_input("Filiação 2 (opcional)")

    # -------------------------------
    # ENDEREÇO
    # -------------------------------
    st.subheader("🏠 Endereço")

    cep = st.text_input("CEP")
    logradouro = st.text_input("Logradouro")
    numero = st.text_input("Número")
    bairro = st.text_input("Bairro")

    # -------------------------------
    # CONTATO
    # -------------------------------
    st.subheader("📞 Contato")

    celular = st.text_input("Celular *")
    email_pessoal = st.text_input("E-mail Pessoal *")

    # -------------------------------
    # DADOS BANCÁRIOS
    # -------------------------------
    st.subheader("🏦 Dados Bancários")

    banco = st.text_input("Banco")
    tipo_conta = st.selectbox("Tipo de Conta", ["Corrente", "Poupança"])
    agencia = st.text_input("Agência")
    conta = st.text_input("Conta")
    chave_pix = st.text_input("Chave Pix")

    # -------------------------------
    # DOCUMENTOS
    # -------------------------------
    st.subheader("📄 Documentos Obrigatórios")

    cpf_file = st.file_uploader("CPF *", type=["pdf", "jpg", "png"])
    rg_file = st.file_uploader("RG *", type=["pdf", "jpg", "png"])
    ctps_file = st.file_uploader("Carteira de Trabalho *", type=["pdf", "jpg", "png"])

    # -------------------------------
    # DEPENDENTES
    # -------------------------------
    st.subheader("👶 Dependentes")

    possui_dependentes = st.checkbox("Possui dependentes?", key="possui_dependentes")
    dependentes = []

    if possui_dependentes:
        qtd_dep = st.number_input(
            "Quantidade de dependentes",
            min_value=1,
            max_value=5,
            step=1,
            key="qtd_dependentes"
        )

        for i in range(int(qtd_dep)):
            st.markdown(f"### Dependente {i+1}")

            dep_nome = st.text_input("Nome do Dependente", key=f"dep_nome_{i}")
            dep_cpf = st.text_input("CPF do Dependente", key=f"dep_cpf_{i}")
            dep_data = st.date_input("Data de Nascimento", key=f"dep_data_{i}")
            dep_sexo = st.selectbox(
                "Sexo",
                ["Masculino", "Feminino", "Outro"],
                key=f"dep_sexo_{i}"
            )
            dep_parentesco = st.text_input("Parentesco", key=f"dep_parentesco_{i}")
            dep_filiacao = st.text_input("Filiação", key=f"dep_filiacao_{i}")

            dep_ir = st.checkbox(
                "Entra para o Imposto de Renda",
                key=f"dep_ir_{i}"
            )
            dep_sf = st.checkbox(
                "Possui Salário Família",
                key=f"dep_sf_{i}"
            )

            dep_doc = st.file_uploader(
                "Documento do Dependente (PDF / JPG / PNG)",
                type=["pdf", "jpg", "png"],
                key=f"dep_doc_{i}"
            )

            dependentes.append({
                "Nome": dep_nome,
                "CPF": dep_cpf,
                "Data Nascimento": dep_data.strftime("%d/%m/%Y"),
                "Sexo": dep_sexo,
                "Parentesco": dep_parentesco,
                "Filiação": dep_filiacao,
                "IR": dep_ir,
                "Salário Família": dep_sf,
                "Arquivo": dep_doc
            })

    enviar = st.form_submit_button("📨 Enviar Admissão")

# ===============================
# PROCESSAMENTO
# ===============================
if enviar:
    if not all([nome, cpf, celular, email_pessoal, filiacao1, cpf_file, rg_file, ctps_file]):
        st.error("❌ Preencha todos os campos obrigatórios.")
        st.stop()

    # -------------------------------
    # DATAFRAMES
    # -------------------------------
    dados_colaborador = {
        "Nome": nome,
        "CPF": cpf,
        "Nascimento": data_nasc.strftime("%d/%m/%Y"),
        "Sexo": sexo,
        "Estado Civil": estado_civil,
        "País Nascimento": pais_nascimento,
        "Nacionalidade": nacionalidade,
        "Raça/Cor": raca_cor,
        "Filiação 1": filiacao1,
        "Filiação 2": filiacao2,
        "CEP": cep,
        "Logradouro": logradouro,
        "Número": numero,
        "Bairro": bairro,
        "Celular": celular,
        "E-mail": email_pessoal,
        "Banco": banco,
        "Tipo Conta": tipo_conta,
        "Agência": agencia,
        "Conta": conta,
        "Pix": chave_pix,
        "Data Envio": datetime.now().strftime("%d/%m/%Y %H:%M")
    }

    df_colaborador = pd.DataFrame([dados_colaborador])
    df_dependentes = pd.DataFrame(dependentes) if dependentes else pd.DataFrame()

    # -------------------------------
    # EXCEL
    # -------------------------------
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
        df_colaborador.to_excel(writer, index=False, sheet_name="Colaborador")
        if not df_dependentes.empty:
            df_dependentes.drop(columns=["Arquivo"]).to_excel(
                writer,
                index=False,
                sheet_name="Dependentes"
            )

    excel_bytes = excel_buffer.getvalue()

    # -------------------------------
    # ZIP
    # -------------------------------
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr(f"Documentos/CPF_{cpf_file.name}", cpf_file.getvalue())
        zipf.writestr(f"Documentos/RG_{rg_file.name}", rg_file.getvalue())
        zipf.writestr(f"Documentos/CTPS_{ctps_file.name}", ctps_file.getvalue())

        for i, dep in enumerate(dependentes):
            if dep["Arquivo"]:
                zipf.writestr(
                    f"Documentos/Dependente_{i+1}_{dep['Arquivo'].name}",
                    dep["Arquivo"].getvalue()
                )

    zip_bytes = zip_buffer.getvalue()

    # -------------------------------
    # EMAIL
    # -------------------------------
    assunto = f"Nova Admissão Polachini – {nome}"

    corpo = f"""
Olá,

Uma nova admissão foi enviada.

Colaborador: {nome}
CPF: {cpf}

Em anexo:
- Excel com todos os dados
- ZIP com toda a documentação

Sistema de Admissão – Futto RH
"""

    anexos = [
        ("Dados_Admissao.xlsx", excel_bytes,
         "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
        ("Documentacao.zip", zip_bytes, "application/zip")
    ]

    enviar_email(
        destinatario="nycolas.pantarine@futtorh.com.br",
        assunto=assunto,
        corpo=corpo,
        anexos=anexos
    )

    st.success("✅ Admissão enviada com sucesso!")
