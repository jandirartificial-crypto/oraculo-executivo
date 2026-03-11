import streamlit as st
import google.generativeai as genai
from utils import prompts
from utils.config import get_api_key

# ============================================
# FUNÇÃO PRINCIPAL DO TERAPEUTA DIGITAL
# ============================================
def show_terapeuta_digital():
    """
    Exibe a interface do Terapeuta Digital no Streamlit.
    """
    st.markdown("<h2 style='text-align: center;'>🧘 TERAPEUTA DIGITAL</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6C757D; margin-bottom: 30px;'>Um espaço para clareza, direção e acolhimento</p>", unsafe_allow_html=True)
    
    # Inicialização do estado da sessão
    if 'terapeuta_etapa' not in st.session_state:
        st.session_state.terapeuta_etapa = 'entrada'
    if 'terapeuta_pergunta' not in st.session_state:
        st.session_state.terapeuta_pergunta = ""
    if 'terapeuta_resultado' not in st.session_state:
        st.session_state.terapeuta_resultado = None
    
    st.divider()
    
    # Container central
    with st.container():
        
        # ETAPA 1: ENTRADA DO USUÁRIO
        if st.session_state.terapeuta_etapa == 'entrada':
            mostrar_etapa_entrada()
        
        # ETAPA 2: PROCESSAMENTO E RESULTADO
        elif st.session_state.terapeuta_etapa == 'resultado':
            mostrar_etapa_resultado()


# ============================================
# ETAPA 1: ENTRADA DO USUÁRIO
# ============================================
def mostrar_etapa_entrada():
    """Mostra o campo de entrada para o usuário fazer sua pergunta/desabafo"""
    
    st.markdown("### Compartilhe o que te traz aqui hoje")
    
    # Texto de exemplo para inspirar o usuário
    exemplos = [
        "Me sinto perdido na minha carreira, não sei se devo mudar de área...",
        "Estou passando por um término e não consigo seguir em frente...",
        "Sinto uma ansiedade constante que me paralisa...",
        "Não sei se devo continuar nesse relacionamento...",
        "Procuro um propósito maior na minha vida..."
    ]
    
    import random
    exemplo_sugerido = random.choice(exemplos)
    
    # Campo de texto para a pergunta/desabafo
    pergunta = st.text_area(
        "Seu desabafo ou pergunta:",
        placeholder=exemplo_sugerido,
        height=180,
        key="terapeuta_input",
        label_visibility="collapsed"
    )
    
    if pergunta:
        st.session_state.terapeuta_pergunta = pergunta
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Botão para processar
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Buscar Orientação", type="primary", use_container_width=True):
            if st.session_state.terapeuta_pergunta:
                with st.spinner("Processando sua questão com sabedoria e ciência..."):
                    processar_consulta(st.session_state.terapeuta_pergunta)
            else:
                st.warning("Por favor, compartilhe um pouco da sua situação para que eu possa te orientar.")


# ============================================
# PROCESSAMENTO DA CONSULTA
# ============================================
def processar_consulta(pergunta: str):
    """
    Função que chama a API do Gemini e processa a resposta.
    """
    try:
        # Configurar a API
        api_key = get_api_key()
        genai.configure(api_key=api_key)
        
        # Configurar o modelo com parâmetros adequados
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={
                "temperature": 0.8,  # Um pouco de criatividade para respostas mais humanas
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 4096,  # Suficiente para as 8 seções
            },
            safety_settings={
                "HARASSMENT": "BLOCK_NONE",
                "HATE_SPEECH": "BLOCK_NONE",
                "SEXUALLY_EXPLICIT": "BLOCK_NONE",
                "DANGEROUS_CONTENT": "BLOCK_NONE",
            }
        )
        
        # Obter o prompt sistêmico
        prompt_sistemico = prompts.get_terapeuta_prompt(pergunta)
        
        # Fazer a chamada para a API
        response = model.generate_content(prompt_sistemico)
        
        # Verificar se a resposta é válida
        if response and response.text:
            st.session_state.terapeuta_resultado = response.text
            st.session_state.terapeuta_etapa = 'resultado'
            st.rerun()
        else:
            st.error("Não foi possível gerar uma orientação. Por favor, tente novamente.")
            
    except Exception as e:
        st.error(f"Ocorreu um erro ao processar sua solicitação: {str(e)}")
        st.info("Por favor, tente novamente em alguns instantes.")


# ============================================
# ETAPA 2: EXIBIÇÃO DO RESULTADO
# ============================================
def mostrar_etapa_resultado():
    """Mostra o resultado da orientação para o usuário"""
    
    if st.session_state.terapeuta_resultado:
        # Container estilizado para o resultado
        with st.container():
            st.markdown("### 🫂 Sua Orientação")
            
            # Usar markdown para exibir o resultado com a formatação correta
            # O resultado já vem com os cabeçalhos ## das 8 seções
            st.markdown(f'<div class="resultado-container">{st.session_state.terapeuta_resultado}</div>', unsafe_allow_html=True)
            
            st.divider()
            
            # Feedback sutil
            st.caption("Esta orientação foi gerada com base em sabedoria ancestral e conhecimento científico, como um espelho para sua reflexão.")
    
    # Botões de ação após o resultado
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Botão para nova consulta
        if st.button("🔄 Fazer nova pergunta", use_container_width=True):
            # Limpar o estado para começar de novo
            st.session_state.terapeuta_etapa = 'entrada'
            st.session_state.terapeuta_pergunta = ""
            st.session_state.terapeuta_resultado = None
            st.rerun()
    
    # Opção de salvar/exportar (simulada)
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("📝 Dicas para aproveitar esta orientação"):
        st.markdown("""
        - **Leia em um momento tranquilo**: Reserve um tempo para absorver cada seção
        - **Anote insights**: Tenha um caderno para registrar o que ressoa com você
        - **Comece pequeno**: Escolha 2-3 ações práticas para implementar hoje
        - **Releia depois**: Volte a esta orientação em alguns dias para novas percepções
        """)
