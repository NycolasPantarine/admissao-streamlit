import streamlit as st
import os
import pandas as pd
from datetime import datetime
from validate_docbr import CPF

st.set_page_config(page_title="Formulário de Admissão", layout="centered")

st.title("📋 Formulário de Admissão")

BASE_PATH = "data/admissoes"
os.makedirs(BASE_PATH, exist_ok=True)

cpf_validator = CPF()

# ========================
# DADOS PESSOAIS
# ========================
st.header("Dados Pessoais")

nome = st.text_input("Nome Completo *")
cpf = st.text_input("CPF * (somente números)")
cpf_anexo = st.file_uploader("Anexar CPF *", type=["pdf", "jpg", "png"])

data_nasc = st.text_input("Data de Nascimento * (dd/mm/yyyy)")
sexo = st.selectbox("Sexo *", ["", "Masculino", "Feminino", "Outro"])
estado_civil = st.selectbox("Estado Civil *", ["", "Solteiro(a)", "Casado(a)", "Divorciado(a)", "Viúvo(a)"])
pais_nasc = st.text_input("País de Nascimento *")
pais_nacionalidade = st.text_input("País de Nacionalidade *")
raca = st.selectbox("Raça/Cor *", ["", "Branca", "Preta", "Parda", "Amarela", "Indígena"])
filiacao1 = st.text_input("Filiação 1 *")
filiacao2 = st.text_input("Filiação 2 (opcional)")

# ========================
# ENDEREÇO
# ========================
st.header("Endereço")

cep = st.text_input("CEP *")
logradouro = st.text_input("Logradouro *")
bairro = st.text_input("Bairro *")
numero = st.text_input("Número da Residência *")

# ========================
# CONTATO
# ========================
st.header("Contato")

celular = st.text_input("Celular *")
email = st.text_input("E-mail Pessoal *")

# ========================
# DADOS BANCÁRIOS
# ========================
st.header("Dados Bancários")

tipo_conta = st.selectbox("Tipo de Conta *", ["", "Corrente", "Poupança"])
agencia = st.text_input("Agência *")
conta = st.text_input("Conta *")
chave_pix = st.text_input("Chave PIX")

# ========================
# DOCUMENTOS
# ========================
st.header("Documentos Obrigatórios")

rg = st.file_uploader("RG *", type=["pdf", "jpg", "png"])
ctps = st.file_uploader("Carteira de Trabalho (CTPS) *", type=["pdf", "jpg", "png"])

# ========================
# RESERVISTA (CONDICIONAL)
# ========================
reservista_num = reservista_ra = reservista_cat = ""

if sexo == "Masculino":
    st.subheader("Reservista (se aplicável)")
    reservista_num = st.text_input("Número do Certificado")
    reservista_ra = st.text_input("RA")
    reservista_cat = st.text_input("Categoria")

# ========================
# DEPENDENTES
# ========================
st.header("Dependentes")

tem_dependente = st.radio("Possui dependentes?", ["Não", "Sim"])

dependentes = []

if tem_dependente == "Sim":
    qtd = st.number_input("Quantidade de dependentes", min_value=1, step=1)

    for i in range(int(qtd)):
        st.subheader(f"Dependente {i+1}")
        dep_nome = st.text_input(f"Nome do Dependente {i+1}")
        dep_cpf = st.text_input(f"CPF do Dependente {i+1}")
        dep_cpf_anexo = st.file_uploader(f"Anexar CPF Dependente {i+1}", type=["pdf","jpg","png"], key=f"cpf_dep_{i}")
        dep_nasc = st.text_input(f"Data de Nascimento {i+1}")
        dep_sexo = st.selectbox(f"Sexo {i+1}", ["Masculino","Feminino","Outro"], key=f"sexo_dep_{i}")
        dep_parentesco = st.text_input(f"Parentesco {i+1}")
        dep_filiacao = st.text_input(f"Filiação {i+1}")
        dep_ir = st.selectbox(f"Entra no IR?", ["Sim","Não"], key=f"ir_dep_{i}")
        dep_sf = st.selectbox(f"Salário Família?", ["Sim","Não"], key=f"sf_dep_{i}")

        dependentes.append({
            "Nome": dep_nome,
            "CPF": dep_cpf,
            "Nascimento": dep_nasc,
            "Sexo": dep_sexo,
            "Parentesco": dep_parentesco,
            "Filiação": dep_filiacao,
            "IR": dep_ir,
            "Salário Família": dep_sf
        })

# ========================
# ENVIO
# ========================
if st.button("Enviar Admissão"):
    obrigatorios = [
        nome, cpf, cpf_anexo, data_nasc, sexo, estado_civil, pais_nasc,
        pais_nacionalidade, raca, filiacao1, cep, logradouro, bairro,
        numero, celular, email, tipo_conta, agencia, conta, rg, ctps
    ]

    if "" in obrigatorios or None in obrigatorios:
        st.error("❌ Preencha todos os campos obrigatórios")
    elif not cpf_validator.validate(cpf):
        st.error("❌ CPF inválido")
    else:
        pasta = f"{BASE_PATH}/{cpf}"
        os.makedirs(pasta, exist_ok=True)

        # salvar arquivos
        for arq, nome_arq in [
            (cpf_anexo, "CPF.pdf"),
            (rg, "RG.pdf"),
            (ctps, "CTPS.pdf")
        ]:
            with open(f"{pasta}/{nome_arq}", "wb") as f:
                f.write(arq.getbuffer())

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
            "Endereço": f"{logradouro}, {numero} - {bairro}",
            "CEP": cep,
            "Celular": celular,
            "Email": email,
            "Banco Tipo": tipo_conta,
            "Agência": agencia,
            "Conta": conta,
            "PIX": chave_pix,
            "Reservista Número": reservista_num,
            "RA": reservista_ra,
            "Categoria": reservista_cat,
            "Data Envio": datetime.now()
        }

        pd.DataFrame([dados]).to_excel(f"{pasta}/dados_admissao.xlsx", index=False)

        if dependentes:
            pd.DataFrame(dependentes).to_excel(f"{pasta}/dependentes.xlsx", index=False)

        st.success("✅ Admissão enviada com sucesso!")
