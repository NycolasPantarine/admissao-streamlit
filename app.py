import streamlit as st
import pandas as pd
import os
import io
import zipfile
import smtplib
from email.message import EmailMessage
from datetime import datetime
from validate_docbr import CPF

# =====================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================
st.set_page_config(
    page_title="Formulário de Admissão",
    layout="centered"
)

st.title("📋 Formulário de Admissão – Polachini")

cpf_validator = CPF()

# =====================================================
# FUNÇÕES AUXILIARES
# =====================================================
def dataframe_to_excel_bytes(df: pd.DataFrame, sheet_name="Dados"):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    return output.getvalue()


def criar_zip(arquivos: list):
    """
    arquivos = [(caminho_no_zip, bytes), ...]
    """
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
        for nome, conteudo in arquivos:
            zf.writestr(nome, conteudo)
    return output.getvalue()


def enviar_email(destinatario, assunto, corpo, anexos):
    """
    anexos = [(nome_arquivo, bytes, mime_type)]
    """
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

    with smtplib.SMTP(st.secrets["SMTP_HOST"], int(st.secrets["SMTP_PORT"])) as server:
        server.starttls()
        server.login(st.secrets["SMTP_USER"], st.secrets["SMTP_PASS"])
        server.send_message(msg)

# =====================================================
# DADOS PESSOAIS
# =====================================================
st.header("🧍 Dados Pessoais")

nome = st.text_input("Nome Completo *")
cpf = st.text_input("CPF * (somente números)")
data_nasc = st.text_input("Data de Nascimento * (dd/mm/yyyy)")
sexo = st.selectbox("Sexo *", ["", "Masculino", "Feminino", "Outro"])
estado_civil = st.selectbox("Estado Civil *", ["", "Solteiro(a)", "Casado(a)", "Divorciado(a)", "Viúvo(a)"])
pais_nasc = st.text_input("País de Nascimento *")
pais_nacionalidade = st.text_input("País de Nacionalidade *")
raca = st.selectbox("Raça/Cor *", ["", "Branca", "Preta", "Parda", "Amarela", "Indígena"])
filiacao1 = st.text_input("Filiação 1 *")
filiacao2 = st.text_input("Filiação 2 (opcional)")

# =====================================================
# ENDEREÇO
# =====================================================
st.header("🏠 Endereço")

cep = st.text_input("CEP *")
logradouro = st.text_input("Logradouro *")
bairro = st.text_input("Bairro *")
numero = st.text_input("Número da Residência *")

# =====================================================
# CONTATO
# =====================================================
st.header("📞 Contato")

celular = st.text_input("Celular *")
email_pessoal = st.text_input("E-mail Pessoal *")

# =====================================================
# DADOS BANCÁRIOS
# =====================================================
st.header("🏦 Dados Bancários")

tipo_conta = st.selectbox("Tipo de Conta *", ["", "Corrente", "Poupança"])
agencia = st.text_input("Agência *")
conta = st.text_input("Conta *")
chave_pix = st.text_input("Chave PIX")

# =====================================================
# DOCUMENTOS OBRIGATÓRIOS
# =====================================================
st.header("📎 Documentos Obrigatórios")

cpf_anexo = st.file_uploader("Anexar CPF *", type=["pdf", "jpg", "png"])
rg_anexo = st.file_uploader("Anexar RG *", type=["pdf", "jpg", "png"])
ctps_anexo = st.file_uploader("Anexar Carteira de Trabalho (CTPS) *", type=["pdf", "jpg", "png"])

# =====================================================
# RESERVISTA (SE HOMEM)
# =====================================================
reservista_num = reservista_ra = reservista_cat = ""

if sexo == "Masculino":
    st.header("🎖️ Reservista")
    reservista_num = st.text_input("Número do Certificado")
    reservista_ra = st.text_input("RA")
    reservista_cat = st.text_input("Categoria")

# =====================================================
# DEPENDENTES
# =====================================================
st.header("👶 Dependentes")

dependentes = []
dependentes_anexos = []

tem_dependentes = st.radio("Possui dependentes?", ["Não", "Sim"])

if tem_dependentes == "Sim":
    qtd = st.number_input("Quantidade de dependentes", min_value=1, step=1)

    for i in range(int(qtd)):
        st.subheader(f"Dependente {i+1}")
        d_nome = st.text_input("Nome", key=f"dn_{i}")
        d_cpf = st.text_input("CPF", key=f"dcpf_{i}")
        d_cpf_anexo = st.file_uploader("Anexar CPF *", type=["pdf","jpg","png"], key=f"dcpf_anexo_{i}")
        d_nasc = st.text_input("Data de Nascimento", key=f"dnasc_{i}")
        d_sexo = st.selectbox("Sexo", ["Masculino","Feminino","Outro"], key=f"dsexo_{i}")
        d_parentesco = st.text_input("Parentesco", key=f"dpar_{i}")
        d_filiacao = st.text_input("Filiação", key=f"dfil_{i}")
        d_ir = st.selectbox("Entra no IR?", ["Sim","Não"], key=f"dir_{i}")
        d_sf = st.selectbox("Salário Família?", ["Sim","Não"], key=f"dsf_{i}")

        dependentes.append({
            "Nome": d_nome,
            "CPF": d_cpf,
            "Nascimento": d_nasc,
            "Sexo": d_sexo,
            "Parentesco": d_parentesco,
            "Filiação": d_filiacao,
            "IR": d_ir,
            "Salário Família": d_sf
        })

        if d_cpf_anexo:
            ext = os.path.splitext(d_cpf_anexo.name)[1]
            dependentes_anexos.append(
                (f"Dependentes/{d_nome}_CPF{ext}", d_cpf_anexo.getbuffer().tobytes())
            )

# =====================================================
# ENVIO
# =====================================================
if st.button("📤 Enviar Admissão"):
    obrigatorios = [
        nome, cpf, data_nasc, sexo, estado_civil, pais_nasc,
        pais_nacionalidade, raca, filiacao1, cep, logradouro,
        bairro, numero, celular, email_pessoal,
        tipo_conta, agencia, conta,
        cpf_anexo, rg_anexo, ctps_anexo
    ]

    if "" in obrigatorios or None in obrigatorios:
        st.error("❌ Preencha todos os campos obrigatórios.")
    elif not cpf_validator.validate(cpf):
        st.error("❌ CPF inválido.")
    else:
        dados = {
            "Nome": nome,
            "CPF": cpf,
            "Nascimento": data_nasc,
            "Sexo": sexo,
            "Estado Civil": estado_civil,
            "País Nascimento": pais_nasc,
            "Nacionalidade": pais_nacionalidade,
            "Raça": raca,
            "Filiação 1": filiacao1,
            "Filiação 2": filiacao2,
            "CEP": cep,
            "Logradouro": logradouro,
            "Bairro": bairro,
            "Número": numero,
            "Celular": celular,
            "Email": email_pessoal,
            "Tipo Conta": tipo_conta,
            "Agência": agencia,
            "Conta": conta,
            "PIX": chave_pix,
            "Reservista Número": reservista_num,
            "Reservista RA": reservista_ra,
            "Reservista Categoria": reservista_cat,
            "Data Envio": datetime.now()
        }

        # Excel
        excel_bytes = dataframe_to_excel_bytes(pd.DataFrame([dados]), "Admissao")
        anexos_zip = [
            ("Planilhas/Admissao.xlsx", excel_bytes),
            ("Documentos/CPF.pdf", cpf_anexo.getbuffer().tobytes()),
            ("Documentos/RG.pdf", rg_anexo.getbuffer().tobytes()),
            ("Documentos/CTPS.pdf", ctps_anexo.getbuffer().tobytes())
        ]

        if dependentes:
            excel_dep = dataframe_to_excel_bytes(pd.DataFrame(dependentes), "Dependentes")
            anexos_zip.append(("Planilhas/Dependentes.xlsx", excel_dep))
            anexos_zip.extend(dependentes_anexos)

        zip_bytes = criar_zip(anexos_zip)

        enviar_email(
            destinatario="nycolas.pantarine@futtorh.com.br",
            assunto=f"Nova Admissão Polachini - {nome}",
            corpo=f"Nova admissão recebida.\n\nNome: {nome}\nCPF: {cpf}",
            anexos=[
                (f"Admissao_{cpf}.xlsx", excel_bytes,
                 "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
                (f"Documentacao_{cpf}.zip", zip_bytes, "application/zip")
            ]
        )

        st.success("✅ Admissão enviada com sucesso! E-mail disparado.")
