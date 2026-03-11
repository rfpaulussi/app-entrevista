import streamlit as st
import google.generativeai as genai
import requests

# Configuração da página
st.set_page_config(page_title="Assistente de Entrevista", page_icon="📋", layout="centered")

st.title("📋 Recrutamento Técnico")
st.markdown("Gerador de roteiro técnico com integração automática à folha de controle operacional.")

# Resgate seguro das Chaves (invisíveis no código)
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    google_sheets_url = st.secrets["GOOGLE_SHEETS_URL"]
    genai.configure(api_key=api_key)
except KeyError:
    st.error("Erro de configuração: Chaves não encontradas nos Secrets.")
    st.stop()

# Interface de Configuração da Vaga
st.subheader("Configurar Vaga")
candidate_name = st.text_input("Candidato (Opcional)", placeholder="Ex: João da Silva")

roles = ["Auxiliar de Limpeza", "Limpador de Vidros", "Encarregado de Limpeza", "Encarregado Volante", "Jardineiro / Podador"]
role = st.selectbox("Cargo Pretendido *", roles)

envs = ["Escola / Creche", "Prédio Administrativo", "Parque / Praça Pública", "UBS / Posto de Saúde"]
environment = st.selectbox("Ambiente / Unidade *", envs)

# Controle de estado para manter o texto gerado visível
if "roteiro_gerado" not in st.session_state:
    st.session_state.roteiro_gerado = None

# Botão de Geração
if st.button("✨ Gerar Perguntas", type="primary", use_container_width=True):
    with st.spinner("Criando parâmetros técnicos da entrevista..."):
        
        # Instruções alinhadas à coordenação operacional de contratos públicos
        sys_instruction = f"""Você é Engenheiro de Segurança do Trabalho e Coordenador Operacional com 18 anos de experiência em gestão de serviços.
        Gere um roteiro de entrevista técnico com EXATAMENTE 4 perguntas diretas.
        1. Tempo nos empregos anteriores (avaliação de estabilidade).
        2. Conhecimento técnico sobre diluição de químicos concentrados.
        3. Como reage ao receber ordens da chefia (subordinação e disciplina).
        4. Questão de atitude rigorosamente adaptada ao ambiente ({environment}).
        Use formatação limpa (sem tags HTML, apenas Markdown). Seja prático e exigente na postura operacional."""
        
        prompt = f"Candidato: {candidate_name if candidate_name else 'Candidato'}. Cargo: '{role}'. Ambiente: '{environment}'. Gere as 4 perguntas."
        
        try:
            model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=sys_instruction)
            response = model.generate_content(prompt)
            st.session_state.roteiro_gerado = response.text
        except Exception as e:
            st.error(f"Erro na comunicação com a IA: {e}")

# Exibição do Resultado e Gravação
if st.session_state.roteiro_gerado:
    st.markdown("### 💬 Roteiro de Entrevista")
    st.info(st.session_state.roteiro_gerado)
    
    st.markdown("---")
    if st.button("💾 Gravar na Folha de Controle", use_container_width=True):
        with st.spinner("A enviar dados para a planilha..."):
            
            # Preparação do pacote de dados para o Google Sheets
            payload = {
                "candidateName": candidate_name if candidate_name.strip() else "Candidato Sem Nome",
                "role": role,
                "environment": environment,
                "contentHTML": st.session_state.roteiro_gerado
            }
            
            try:
                # Envio seguro pelo servidor
                response = requests.post(google_sheets_url, json=payload)
                st.success("✅ Entrevista gravada na folha de cálculo com sucesso!")
                
                # Limpa o roteiro após salvar para a próxima entrevista
                st.session_state.roteiro_gerado = None
            except Exception as e:
                st.error("Falha ao comunicar com a planilha. Verifique a conexão.")
