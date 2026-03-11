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

# Identificação da Supervisão
st.subheader("Responsável pela Avaliação")
supervisor_name = st.text_input("Nome do Supervisor (Entrevistador) *", placeholder="Ex: Carlos Silva")

st.markdown("---")

# Dados do Candidato
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
    if not supervisor_name or not candidate_name:
        st.warning("Preencha o nome do supervisor e do candidato antes de gerar.")
        st.stop()
        
    with st.spinner("A processar diretrizes operacionais..."):
        sys_instruction = f"""Você é um Coordenador Operacional sênior.
        Crie um roteiro de entrevista prático que será APLICADO PELOS SEUS SUPERVISORES DE CAMPO para avaliar {candidate_name} ({role}).
        Adapte o vocabulário para um candidato com experiência: '{experience}' e escolaridade: '{education}'.
        
        REGRA ESTRITA: Não crie diálogos, introduções ou encerramentos. Entregue APENAS as 4 perguntas diretas que o supervisor deve fazer, focadas em:
        1. Estabilidade nos contratos.
        2. Conhecimento técnico prático.
        3. Disciplina e respeito à hierarquia do supervisor.
        4. Postura adequada para o ambiente ({environment}).
        Seja direto, objetivo e focado no resultado da operação."""
        
        try:
            model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=sys_instruction)
            response = model.generate_content("Gere o roteiro.")
            st.session_state.roteiro = response.text
        except Exception as e:
            st.error(f"Erro na comunicação com a IA: {e}")

if st.session_state.roteiro:
    st.info(st.session_state.roteiro)
    
    st.markdown("### Avaliação Final")
    col_nota, col_parecer = st.columns([1, 3])
    with col_nota:
        score = st.number_input("Nota (0 a 10)", min_value=0, max_value=10, value=5, step=1)
    with col_parecer:
        parecer = st.text_area("Parecer da Supervisão", placeholder="Comportamento, pontos fortes e fracos...")
    
    if st.button("💾 Gravar na Planilha Oficial", use_container_width=True):
        with st.spinner("A enviar dados para controlo central..."):
            
            texto_final = f"**ROTEIRO UTILIZADO:**\n{st.session_state.roteiro}\n\n**PARECER DA SUPERVISÃO:**\n{parecer}"
            
            payload = {
                "supervisorName": supervisor_name,
                "candidateName": candidate_name,
                "role": role,
                "experience": experience,
                "education": education,
                "status": status,
                "score": score,
                "observations": texto_final
            }
            
            try:
                requests.post(google_sheets_url, json=payload)
                st.success("✅ Avaliação registada com sucesso!")
                st.session_state.roteiro = None 
            except Exception as e:
                st.error("Falha ao comunicar com o Google Sheets.")
