import streamlit as st
import os

# ============================================
# CONFIGURAÇÕES DA API
# ============================================

def get_api_key() -> str:
    """
    Obtém a chave da API do Gemini de forma segura.
    Prioriza secrets do Streamlit, depois variáveis de ambiente.
    """
    try:
        # Tentar obter dos secrets do Streamlit (para produção)
        api_key = st.secrets["GOOGLE_API_KEY"]
        return api_key
    except (KeyError, AttributeError):
        # Se não encontrar nos secrets, tentar variável de ambiente
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            return api_key
        else:
            # Se não encontrar em lugar nenhum, mostrar erro amigável
            st.error("""
            🔑 Chave da API não encontrada!
            
            Para usar o Terapeuta Digital, você precisa configurar sua chave da API do Google Gemini.
            
            **Como configurar:**
            1. Obtenha uma chave em: https://makersuite.google.com/app/apikey
            2. Adicione nos secrets do Streamlit ou como variável de ambiente GOOGLE_API_KEY
            """)
            st.stop()


# ============================================
# CONFIGURAÇÕES GERAIS DO APP
# ============================================

APP_CONFIG = {
    "nome": "Terapeuta Digital",
    "versao": "1.0.0",
    "modelo_gemini": "gemini-1.5-flash",
    "temperatura_padrao": 0.8,
    "max_tokens": 4096,
}

def get_app_config():
    """Retorna as configurações do app"""
    return APP_CONFIG
