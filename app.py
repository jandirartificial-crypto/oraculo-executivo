import streamlit as st
import google.generativeai as genai

# Configuração da Página para manter o estilo minimalista e profissional
st.set_page_config(page_title="Executivo do Tarô", page_icon="🃏", layout="centered")

# Estilização básica para cores neutras
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { background-color: #2c3e50; color: white; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ Oráculo Digital: Executivo do Tarô")
st.write("Bem-vindo à sua consultoria arquetípica de alto nível.")

# --- ENTRADA DE DADOS ---
pergunta = st.text_area("Descreva seu cenário ou faça sua pergunta estratégica:", placeholder="Ex: Devo avançar com a nova parceria de negócios?")

st.subheader("Selecione as Cartas da sua Tiragem")
col1, col2, col3 = st.columns(3)

# Lista de Arcanos Maiores para o seletor
cartas = [
    "O Louco", "O Mago", "A Sacerdotisa", "A Imperatriz", "O Imperador", 
    "O Hierofante", "Os Enamorados", "O Carro", "A Justiça", "O Eremita", 
    "Roda da Fortuna", "A Força", "O Pendurado", "A Morte", "A Temperança", 
    "O Diabo", "A Torre", "A Estrela", "A Lua", "O Sol", "O Julgamento", "O Mundo"
]

with col1:
    c1 = st.selectbox("Carta 1 (Passado/Base)", cartas)
with col2:
    c2 = st.selectbox("Carta 2 (Presente/Ação)", cartas)
with col3:
    c3 = st.selectbox("Carta 3 (Futuro/Potencial)", cartas)

# --- PROCESSAMENTO DA IA ---
if st.button("Realizar Interpretação"):
    if pergunta:
        try:
            # Busca a API Key de forma segura nos Secrets do Streamlit
            genai.configure(api_key=st.secrets["AIzaSyAEGGkPege03hvEDjetQryAvi-kLD0m3lU"])
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Monte o seu prompt aqui - Substitua o texto abaixo pelas suas instruções reais
            prompt_sistema = f"""
            Você é o Executivo do Tarô, um consultor que une a sabedoria dos arquétipos com uma visão pragmática e profissional.
            
            CONTEXTO DO CLIENTE: {pergunta}
            TIRAGEM: {c1}, {c2} e {c3}.
            
            INSTRUÇÕES: Forneça uma análise precisa, mantendo o tom de coach executivo. 
            Não use linguagem excessivamente mística; foque em insights acionáveis e clareza mental.
            """
            
            with st.spinner('O Executivo está analisando as cartas...'):
                response = model.generate_content(prompt_sistema)
                st.markdown("---")
                st.markdown("### 📜 Sua Resposta Estratégica")
                st.write(response.text)
                
                # Rodapé opcional para promover seus produtos Amati
                st.info("💡 Dica: Complemente esta clareza mental com nossos Sais de Banho Terapêuticos.")
        
        except Exception as e:
            st.error("Erro técnico: Certifique-se de que a API Key foi configurada nos Secrets do Streamlit.")
    else:
        st.warning("Por favor, descreva sua dúvida antes de consultar o oráculo.")
