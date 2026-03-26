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
    role = st.selectbox("Vaga Pretendida *", ["Ajudante de Limpeza", "Agente de Higienização", "Limpador de Vidros", "Encarregado de Limpeza", "Encarregado Volante"])
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
        
    with st.spinner("A estruturar roteiro profissional de entrevista..."):
        
        # LÓGICA DE CONDICIONAMENTO DOS CARGOS
        regra_cargo = ""
        if role == "Ajudante de Limpeza":
            regra_cargo = "IMPORTANTE: O 'Ajudante de Limpeza' NÃO atua em banheiros. Focar em áreas comuns, varrição, recolha de lixo e organização."
        elif role == "Agente de Higienização":
            regra_cargo = "IMPORTANTE: O 'Agente de Higienização' atua fortemente na limpeza e desinfeção de banheiros e sanitários. Abordar essa vivência e o uso de EPIs."
        
        # INSTRUÇÃO DO SISTEMA NEUTRA E FOCADA EM COMPETÊNCIAS
        sys_instruction = f"""Você é um Coordenador Operacional orientando seus supervisores.
        Crie 4 perguntas de entrevista PROFISSIONAIS, NEUTRAS E REALISTAS para avaliar {candidate_name} ({role}).
        Adapte a linguagem para alguém com experiência: '{experience}' e escolaridade: '{education}'.
        
        {regra_cargo}
        
        REGRA ESTRITA: Sem introduções ou encerramentos. APENAS as 4 perguntas diretas.
        Foque em um ambiente de trabalho saudável, avaliando:
        1. Vivência Profissional: Como o candidato lida com a rotina diária da profissão e o que considera importante para manter a assiduidade e pontualidade.
        2. Conhecimento Técnico/Prático: Uma pergunta realista sobre o uso de equipamentos básicos, produtos de limpeza ou EPIs de acordo com a função.
        3. Trabalho em Equipe e Supervisão: Como ele reage ao receber novas orientações da chefia ou ao trabalhar em conjunto com outros colegas.
        4. Postura no Ambiente: Como manter a discrição, o respeito e a postura adequada ao trabalhar em {environment}."""
        
        try:
            model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=sys_instruction)
            response = model.generate_content("Gere o roteiro neutro e profissional.")
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
                st.rerun() # Atualiza o ecrã instantaneamente após a gravação
            except Exception as e:
                st.error("Falha ao comunicar com o Google Sheets.")
