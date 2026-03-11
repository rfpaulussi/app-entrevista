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
    # LISTA DE CARGOS ATUALIZADA
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
        
    with st.spinner("A processar diretrizes operacionais rigorosas..."):
        
        # LÓGICA DE CONDICIONAMENTO TÁTICO DOS CARGOS
        regra_cargo = ""
        if role == "Ajudante de Limpeza":
            regra_cargo = "ATENÇÃO MÁXIMA: Na nossa operação, o 'Ajudante de Limpeza' NÃO limpa e NÃO abastece banheiros sob nenhuma hipótese. Crie perguntas focadas apenas em áreas comuns, varrição, recolha de lixo comum e postura."
        elif role == "Agente de Higienização":
            regra_cargo = "ATENÇÃO MÁXIMA: O 'Agente de Higienização' é responsável por TODA a limpeza, com FOCO PESADO em limpar, desinfetar e abastecer banheiros e sanitários. Teste a disposição dele para este trabalho mais insalubre e pesado."
        
        # INSTRUÇÃO DO SISTEMA MAIS DURA E EXIGENTE
        sys_instruction = f"""Você é um Coordenador Operacional e Engenheiro de Segurança sênior (com 18 anos de experiência em contratos públicos exigentes).
        Crie 4 perguntas de entrevista EXTREMAMENTE RIGOROSAS E PRÁTICAS para o seu supervisor aplicar em {candidate_name} ({role}).
        Adapte a cobrança para alguém com experiência: '{experience}' e escolaridade: '{education}'.
        
        {regra_cargo}
        
        REGRA ESTRITA: Sem introduções simpáticas, sem encerramentos. APENAS as 4 perguntas diretas.
        Evite perguntas teóricas. Crie cenários que 'apertem' o candidato com problemas reais. Foque em:
        1. Estabilidade: Teste a resistência a faltas, atrasos e rotina pesada de trabalho.
        2. Técnica: Cenário prático de uso de produtos (diluição) e EPIs obrigatórios para o cargo dele.
        3. Disciplina: Como ele reage se o supervisor chamar a atenção dele de forma dura na frente de outros, ou mandar refazer um serviço que ele achava que estava bom.
        4. Postura: Uma situação de conflito ou quebra de protocolo no ambiente ({environment})."""
        
        try:
            model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=sys_instruction)
            response = model.generate_content("Gere o roteiro tático.")
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
