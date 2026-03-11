import streamlit as st
from terapeuta_digital import show_terapeuta_digital

# ============================================
# CONFIGURAÇÃO INICIAL
# ============================================
st.set_page_config(
    page_title="Sistema de Orientação",
    page_icon="🧘",
    layout="centered"
)

# ============================================
# CSS GLOBAL
# ============================================
st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF; }
        .block-container { max-width: 800px; padding-top: 2rem; }
        
        /* Estilo dos botões */
        .stButton button {
            background: #000000 !important;
            color: white !important;
            border: none !important;
            border-radius: 50px !important;
            padding: 10px 30px !important;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .stButton button:hover {
            background: #333333 !important;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        /* Estilo dos inputs */
        .stTextArea textarea {
            border-radius: 16px !important;
            border: 2px solid #E9ECEF !important;
            padding: 20px !important;
            font-size: 18px !important;
            resize: vertical;
            min-height: 150px;
            transition: border-color 0.3s ease;
        }
        
        .stTextArea textarea:focus {
            border-color: #000000 !important;
            box-shadow: none !important;
        }
        
        /* Estilo das abas */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
            background-color: #F8F9FA;
            border-radius: 50px;
            padding: 4px;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 50px;
            padding: 10px 20px;
            font-weight: 500;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #000000 !important;
            color: white !important;
        }
        
        /* Esconder elementos padrão */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Títulos */
        h1 {
            color: #000000 !important;
            font-weight: 700 !important;
            text-align: center;
            margin-bottom: 0.5rem;
        }
        
        h2 {
            color: #000000 !important;
            font-weight: 600 !important;
            margin-top: 2rem;
        }
        
        h3 {
            color: #000000 !important;
            font-weight: 500 !important;
        }
        
        /* Divisores */
        hr {
            margin: 2rem 0;
            border: none;
            border-top: 2px solid #F0F0F0;
        }
        
        /* Mensagens de sucesso/erro */
        .stAlert {
            border-radius: 12px;
            border: none;
        }
        
        /* Container de resultado */
        .resultado-container {
            background: #F8F9FA;
            border-radius: 24px;
            padding: 40px 30px;
            margin: 30px 0;
            box-shadow: 0 4px 12px rgba(0,0,0,0.03);
            font-family: 'Georgia', serif;
            line-height: 1.8;
            color: #212529;
        }
        
        /* Texto do rodapé */
        .footer-note {
            text-align: center;
            color: #6C757D;
            font-size: 0.9rem;
            margin-top: 3rem;
        }
    </style>
""", unsafe_allow_html=True)

# ============================================
# INTERFACE PRINCIPAL COM ABAS
# ============================================
def main():
    st.markdown("<h1>🧘 SISTEMA DE ORIENTAÇÃO</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6C757D; margin-bottom: 30px;'>Escolha sua ferramenta de orientação</p>", unsafe_allow_html=True)
    
    # Criar as abas
    tab1, tab2, tab3 = st.tabs(["🔮 Tarot", "🃏 Baralho Cigano", "🧘 Terapeuta Digital"])
    
    with tab1:
        st.info("Módulo de Tarot em desenvolvimento...")
        # Aqui você pode adicionar seu código do Tarot
    
    with tab2:
        st.info("Módulo do Baralho Cigano em desenvolvimento...")
        # Aqui você pode adicionar seu código do Baralho Cigano
    
    with tab3:
        # CHAMADA PARA O MÓDULO TERAPEUTA DIGITAL
        show_terapeuta_digital()
    
    st.markdown("<div class='footer-note'>Lembre-se: esta é uma ferramenta de reflexão e não substitui acompanhamento profissional.</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
