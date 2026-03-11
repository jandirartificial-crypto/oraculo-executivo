# terapeuta_digital.py

import streamlit as st
import google.generativeai as genai
from utils import prompts
from utils.config import get_api_key # Função hipotética para pegar a chave

# --- Configuração da Página (se for rodar standalone, mas geralmente é chamado) ---
# st.set_page_config(page_title="Terapeuta Digital", layout="wide")

def show_terapeuta_digital():
    """
    Exibe a interface do Terapeuta Digital no Streamlit.
    """
    st.markdown("<h1 style='text-align: center;'>🧘 TERAPEUTA DIGITAL</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2rem;'>Um espaço para clareza, direção e acolhimento.</p>", unsafe_allow_html=True)
    st.divider()

    # --- Sessão de Entrada do Usuário ---
    with st.container():
        st.markdown("### Compartilhe o que te traz aqui hoje")
        pergunta = st.text_area(
            "Seu desabafo ou pergunta:",
            placeholder="Ex: 'Me sinto perdido na minha carreira, não sei se devo mudar de área.' ou 'Estou passando por um término e não consigo seguir em frente...'",
            height=150,
            label_visibility="collapsed"
        )
        
        # Botão para processar
        if st.button("Buscar Orientação", type="primary", use_container_width=True):
            if pergunta:
                processar_consulta(pergunta)
            else:
                st.warning("Por favor, compartilhe um pouco da sua situação para que eu possa te orientar.")
        st.divider()


def processar_consulta(pergunta: str):
    """
    Função que chama a API do Gemini e exibe a resposta.
    """
    with st.spinner("Processando sua questão com sabedoria e ciência..."):
        try:
            # 1. Configurar o modelo (pegue sua chave de forma segura)
            api_key = get_api_key() # Sua lógica para pegar a chave
            genai.configure(api_key=api_key)
            
            # Usando um modelo capaz e com bom custo-benefício
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash", 
                generation_config={
                    "temperature": 0.7, # Um pouco de criatividade, mas sem perder o foco
                    "max_output_tokens": 2048,
                }
            )
            
            # 2. Obter o prompt sistêmico
            prompt_sistemico = prompts.get_terapeuta_prompt(pergunta)
            
            # 3. Fazer a chamada para a API
            response = model.generate_content(prompt_sistemico)
            
            # 4. Exibir a resposta formatada
            st.markdown("---")
            st.markdown("### 🫂 Sua Orientação")
            
            # Usamos um container para aplicar CSS ou apenas exibir
            with st.container():
                # A resposta já vem em markdown com os cabeçalhos ##
                st.markdown(response.text)
            
            st.markdown("---")
            st.caption("Lembre-se: esta é uma orientação para reflexão e não substitui o acompanhamento de um profissional de saúde mental.")
            
        except Exception as e:
            st.error(f"Ocorreu um erro ao processar sua solicitação: {e}")
            st.info("Por favor, tente novamente em alguns instantes.")

