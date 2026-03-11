import streamlit as st
import google.generativeai as genai
import requests

st.set_page_config(page_title="Recrutamento Operacional", page_icon="📋", layout="centered")
st.title("📋 Entrevista e Avaliação")

try:
    api_key = st.secrets["GEMINI_API_KEY"]
    google_sheets_url = st.secrets["GOOGLE_SHEETS_URL"]
    genai.configure(api_key=api_key)
except KeyError:
    st.error("Erro: Chaves não configuradas nos Secrets.")
    st.stop()

# Campos recuperados para igualar a sua planilha
st.subheader("Dados do Candidato")
candidate_name = st.text_input("Nome do Candidato *", placeholder="Ex: João da Silva")

col1, col2 = st.columns(2)
with col1:
    role = st.selectbox("Vaga Pretendida *", ["Auxiliar de Limpeza", "Limpador de Vidros", "Encarregado de Limpeza", "Encarregado Volante", "Jardineiro / Podador"])
    experience = st.selectbox("Experiência *", ["Sem experiência", "Até 1 ano", "1 a 3 anos", "Mais de 3 anos"])
with col2:
    education = st.selectbox("Escolaridade *", ["Fundamental Incompleto", "Fundamental Completo", "Médio Incompleto", "Médio Completo"])
    status = st.selectbox("Situação *", ["Em Análise", "Aprovado", "Reprovado", "Banco de Talentos"])

environment = st.selectbox("Ambiente / Unidade (Para guiar a IA)", ["Escola / Creche", "Prédio Administrativo", "Parque / Praça Pública", "UBS / Posto de Saúde"])

if "roteiro" not in st.session_state:
    st.session_state.roteiro = None

if st.button("✨ Gerar Perguntas Técnicas", type="primary", use_container_width=True):
    if not candidate_name:
        st.warning("Preencha o nome do candidato antes de gerar.")
        st.stop()
        
    with st.spinner("Analisando perfil..."):
        sys_instruction = f"""Você é Coordenador Operacional com 18 anos de experiência em serviços.
        Gere 4 perguntas de entrevista para {candidate_name} ({role}).
        Adapte a exigência para alguém com experiência: '{experience}' e escolaridade: '{education}'.
        Foque em: 1. Estabilidade, 2. Conhecimento técnico, 3. Disciplina/Subordinação, 4. Postura no ambiente ({environment})."""
        
        try:
            model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=sys_instruction)
            response = model.generate_content("Gere o roteiro.")
            st.session_state.roteiro = response.text
        except Exception as e:
            st.error(f"Erro na IA: {e}")

if st.session_state.roteiro:
    st.info(st.session_state.roteiro)
    
    # Novo campo para o Coordenador colocar o parecer final
    parecer = st.text_area("Seu Parecer Técnico / Observações da Entrevista", placeholder="Como o candidato se comportou?")
    
    if st.button("💾 Gravar na Planilha Oficial", use_container_width=True):
        with st.spinner("Salvando dados..."):
            
            # Monta o texto final juntando as perguntas da IA e o seu parecer
            texto_final = f"**ROTEIRO UTILIZADO:**\n{st.session_state.roteiro}\n\n**PARECER DO COORDENADOR:**\n{parecer}"
            
            payload = {
                "candidateName": candidate_name,
                "role": role,
                "experience": experience,
                "education": education,
                "status": status,
                "observations": texto_final
            }
            
            try:
                requests.post(google_sheets_url, json=payload)
                st.success("✅ Avaliação registrada com sucesso!")
                st.session_state.roteiro = None # Limpa a tela para o próximo candidato
            except Exception as e:
                st.error("Erro de conexão com o Google Sheets.")
