import streamlit as st
import google.generativeai as genai
from datetime import datetime

# ============================================
# CONFIGURAÇÃO INICIAL - MÍNIMA
# ============================================
st.set_page_config(
    page_title="🔮 Baralho Cigano",
    page_icon="🃏",
    layout="centered"
)

# Configurar API do Gemini
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception as e:
    st.error("🔑 Erro na configuração da API. Verifique sua chave no Streamlit Secrets.")
    st.stop()

# ============================================
# CSS MÍNIMO - APENAS O ESSENCIAL
# ============================================
st.markdown("""
    <style>
        /* Fundo branco limpo */
        .stApp {
            background-color: #FFFFFF;
        }
        
        /* Centralizar conteúdo */
        .block-container {
            max-width: 800px;
            padding-top: 2rem;
        }
        
        /* Botão preto minimalista */
        .stButton button {
            background: #000000 !important;
            color: white !important;
            font-weight: 600 !important;
            border: none !important;
            border-radius: 50px !important;
            padding: 10px 30px !important;
            width: 100%;
        }
        
        .stButton button:hover {
            background: #333333 !important;
        }
        
        /* Campo de texto limpo */
        .stTextInput input {
            border-radius: 12px !important;
            border: 1px solid #DEE2E6 !important;
            padding: 12px !important;
        }
        
        .stTextInput input:focus {
            border-color: #000000 !important;
            box-shadow: 0 0 0 1px #000000 !important;
        }
        
        /* Área de pergunta */
        .stTextArea textarea {
            border-radius: 16px !important;
            border: 2px solid #E9ECEF !important;
            padding: 20px !important;
            font-size: 18px !important;
            resize: none;
        }
        
        .stTextArea textarea:focus {
            border-color: #000000 !important;
            box-shadow: none !important;
        }
        
        /* Container centralizado */
        .centralizado {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            margin: 40px 0;
        }
        
        /* Título minimalista */
        h1 {
            color: #000000 !important;
            font-weight: 700 !important;
            text-align: center;
            margin-bottom: 20px !important;
        }
        
        /* Card minimalista para resultado */
        .resultado {
            background: #F8F9FA;
            border-left: 6px solid #000000;
            padding: 30px;
            border-radius: 0 16px 16px 0;
            margin: 40px 0;
            font-size: 18px;
            line-height: 1.8;
            color: #212529;
        }
        
        /* Esconder elementos do Streamlit */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ============================================
# BASE DE CONHECIMENTO - 36 CARTAS
# ============================================
BARALHO_CIGANO = {
    1: {"nome": "O Cavaleiro", "simbolo": "♞", "palavras_chave": "Notícias, movimento, chegada",
        "significado_normal": "Notícias chegando, visitas, movimento rápido. Indica mensagens importantes a caminho.",
        "significado_invertido": "Atrasos, notícias adiadas, visitas indesejadas ou cancelamento de planos."},
    2: {"nome": "O Trevo", "simbolo": "🍀", "palavras_chave": "Sorte, esperança, brevidade",
        "significado_normal": "Pequena sorte, oportunidades passageiras. Momento de esperança e otimismo.",
        "significado_invertido": "Sorte atrasada, pequenas frustrações. Cuidado com expectativas irreais."},
    3: {"nome": "O Navio", "simbolo": "⛵", "palavras_chave": "Viagem, comércio, distância",
        "significado_normal": "Viagens, negócios à distância, mudanças. Expansão de horizontes.",
        "significado_invertido": "Viagem adiada, problemas no transporte, negócios no exterior com dificuldades."},
    4: {"nome": "A Casa", "simbolo": "🏠", "palavras_chave": "Lar, família, estabilidade",
        "significado_normal": "Segurança doméstica, harmonia familiar, questões imobiliárias.",
        "significado_invertido": "Problemas em casa, desarmonia familiar, necessidade de mudança."},
    5: {"nome": "A Árvore", "simbolo": "🌳", "palavras_chave": "Saúde, crescimento, ancestralidade",
        "significado_normal": "Boa saúde, crescimento pessoal, conexão com raízes familiares.",
        "significado_invertido": "Problemas de saúde, estagnação, bloqueios energéticos."},
    6: {"nome": "As Nuvens", "simbolo": "☁️", "palavras_chave": "Confusão, dúvida, incerteza",
        "significado_normal": "Período de confusão, falta de clareza. Busque informações antes de decidir.",
        "significado_invertido": "Esclarecimento, névoa se dissipando. A verdade virá à tona."},
    7: {"nome": "A Serpente", "simbolo": "🐍", "palavras_chave": "Traição, sabedoria, tentação",
        "significado_normal": "Cuidado com pessoas falsas. Sabedoria feminina, intuição aguçada.",
        "significado_invertido": "Perigo afastado, falsidade descoberta. Livramento de uma armadilha."},
    8: {"nome": "O Caixão", "simbolo": "⚰️", "palavras_chave": "Fim, transformação, renascimento",
        "significado_normal": "Fim de ciclo, transformação profunda. Necessário deixar algo morrer.",
        "significado_invertido": "Renascimento, superação. O pior já passou."},
    9: {"nome": "O Buquê", "simbolo": "💐", "palavras_chave": "Felicidade, convite, beleza",
        "significado_normal": "Alegria, presentes, convites. Reconhecimento e momentos felizes.",
        "significado_invertido": "Felicidade adiada, convite recusado. Pequenas decepções."},
    10: {"nome": "A Foice", "simbolo": "🔪", "palavras_chave": "Corte, decisão, separação",
        "significado_normal": "Decisões rápidas, cortes necessários. Separação ou mudança brusca.",
        "significado_invertido": "Decisão adiada, perigo evitado. Acidente quase ocorreu."},
    11: {"nome": "O Chicote", "simbolo": "🪢", "palavras_chave": "Conflito, discussão, tensão",
        "significado_normal": "Discussões, conflitos, tensões. Necessidade de diálogo claro.",
        "significado_invertido": "Trégua, resolução de conflitos. Paz após tempestade."},
    12: {"nome": "Os Pássaros", "simbolo": "🐦", "palavras_chave": "Conversas, ansiedade, contato",
        "significado_normal": "Boas conversas, contatos sociais. Notícias através de pessoas.",
        "significado_invertido": "Fofocas, ansiedade, conversas desagradáveis."},
    13: {"nome": "A Criança", "simbolo": "👶", "palavras_chave": "Novo começo, inocência, confiança",
        "significado_normal": "Novos projetos, gravidez, confiança. Começos promissores.",
        "significado_invertido": "Imaturidade, atraso em projetos. Cuidado com ingenuidade."},
    14: {"nome": "A Raposa", "simbolo": "🦊", "palavras_chave": "Esperteza, desconfiança, trabalho",
        "significado_normal": "Pessoa astuta, inteligente. Cuidado com malícia alheia.",
        "significado_invertido": "Engano descoberto, pessoa confiável. Esperteza usada para o bem."},
    15: {"nome": "O Urso", "simbolo": "🐻", "palavras_chave": "Força, poder, proteção",
        "significado_normal": "Autoridade, proteção materna, força interior.",
        "significado_invertido": "Abuso de poder, ciúmes, pessoa possessiva."},
    16: {"nome": "As Estrelas", "simbolo": "⭐", "palavras_chave": "Espiritualidade, esperança, destino",
        "significado_normal": "Boa sorte espiritual, realização de desejos. Proteção divina.",
        "significado_invertido": "Desesperança, bloqueio espiritual. Momento de fé."},
    17: {"nome": "A Cegonha", "simbolo": "🕊️", "palavras_chave": "Mudança, parto, evolução",
        "significado_normal": "Mudança positiva, nascimento, evolução na vida.",
        "significado_invertido": "Mudança difícil, resistência a transformações."},
    18: {"nome": "O Cachorro", "simbolo": "🐕", "palavras_chave": "Amizade, lealdade, confiança",
        "significado_normal": "Amigo verdadeiro, parceria fiel, amor incondicional.",
        "significado_invertido": "Amizade falsa, deslealdade, confiança quebrada."},
    19: {"nome": "A Torre", "simbolo": "🏰", "palavras_chave": "Solidão, autoridade, isolamento",
        "significado_normal": "Instituições, orgulho, posição social. Sabedoria na solidão.",
        "significado_invertido": "Aprisionamento, arrogância, isolamento forçado."},
    20: {"nome": "O Jardim", "simbolo": "🌺", "palavras_chave": "Socialização, eventos, admiração",
        "significado_normal": "Eventos sociais, networking, admiração pública.",
        "significado_invertido": "Fofocas, eventos cancelados, vida social negativa."},
    21: {"nome": "A Montanha", "simbolo": "⛰️", "palavras_chave": "Obstáculo, desafio, bloqueio",
        "significado_normal": "Desafios a superar, obstáculos temporários. Paciência.",
        "significado_invertido": "Obstáculo superado, caminho livre. Vitória."},
    22: {"nome": "O Caminho", "simbolo": "🛤️", "palavras_chave": "Escolha, decisão, opções",
        "significado_normal": "Escolhas a fazer, encruzilhada. Novas direções.",
        "significado_invertido": "Indecisão, caminho errado. Momento de parar."},
    23: {"nome": "O Rato", "simbolo": "🐀", "palavras_chave": "Perda, roubo, desgaste",
        "significado_normal": "Pequenas perdas, desgaste, algo se esvaindo.",
        "significado_invertido": "Perda recuperada, problema resolvido. Alívio."},
    24: {"nome": "O Coração", "simbolo": "❤️", "palavras_chave": "Amor, paixão, emoção",
        "significado_normal": "Amor verdadeiro, romance, felicidade no amor.",
        "significado_invertido": "Desamor, coração partido, decepção amorosa."},
    25: {"nome": "A Aliança", "simbolo": "💍", "palavras_chave": "Compromisso, casamento, parceria",
        "significado_normal": "Casamento, sociedade, contratos. União promissora.",
        "significado_invertido": "Compromisso quebrado, divórcio, parceria desfeita."},
    26: {"nome": "O Livro", "simbolo": "📚", "palavras_chave": "Segredo, conhecimento, estudo",
        "significado_normal": "Aprendizado, segredos revelados. Busca por conhecimento.",
        "significado_invertido": "Segredo mantido, ignorância. Mistério não resolvido."},
    27: {"nome": "A Carta", "simbolo": "✉️", "palavras_chave": "Mensagem, comunicação, documento",
        "significado_normal": "Notícias formais, documentos, comunicação oficial.",
        "significado_invertido": "Mensagem não entregue, comunicação falha."},
    28: {"nome": "O Homem", "simbolo": "👨", "palavras_chave": "Masculino, ação, figura paterna",
        "significado_normal": "Figura masculina, parceiro, ação e iniciativa.",
        "significado_invertido": "Homem ausente, masculino tóxico, passividade."},
    29: {"nome": "A Mulher", "simbolo": "👩", "palavras_chave": "Feminino, intuição, figura materna",
        "significado_normal": "Figura feminina, parceira, intuição e acolhimento.",
        "significado_invertido": "Mulher ausente, feminino bloqueado. Intuição falha."},
    30: {"nome": "Os Lírios", "simbolo": "⚜️", "palavras_chave": "Virtude, paz, harmonia",
        "significado_normal": "Paz interior, harmonia familiar, pureza de intenções.",
        "significado_invertido": "Conflito familiar, desarmonia, impureza."},
    31: {"nome": "O Sol", "simbolo": "☀️", "palavras_chave": "Sucesso, energia, felicidade",
        "significado_normal": "Sucesso garantido, energia vital, felicidade plena.",
        "significado_invertido": "Sucesso temporário, energia baixa. Otimismo necessário."},
    32: {"nome": "A Lua", "simbolo": "🌙", "palavras_chave": "Intuição, emoção, ciclo",
        "significado_normal": "Intuição aguçada, emoções à flor da pele, ciclo feminino.",
        "significado_invertido": "Confusão emocional, intuição falha. Medos internos."},
    33: {"nome": "A Chave", "simbolo": "🔑", "palavras_chave": "Solução, destino, abertura",
        "significado_normal": "Solução encontrada, portas abertas, destino se revelando.",
        "significado_invertido": "Oportunidade perdida, solução escondida."},
    34: {"nome": "O Peixe", "simbolo": "🐟", "palavras_chave": "Dinheiro, abundância, prosperidade",
        "significado_normal": "Ganhos financeiros, prosperidade, negócios lucrativos.",
        "significado_invertido": "Dificuldade financeira, dinheiro mal investido."},
    35: {"nome": "A Âncora", "simbolo": "⚓", "palavras_chave": "Estabilidade, segurança, permanência",
        "significado_normal": "Segurança no trabalho, relacionamento estável. Firmeza.",
        "significado_invertido": "Instabilidade, insegurança. Necessidade de mudança."},
    36: {"nome": "A Cruz", "simbolo": "✝️", "palavras_chave": "Fardo, destino, espiritualidade",
        "significado_normal": "Fardo a carregar, destino, provação espiritual.",
        "significado_invertido": "Alívio, fardo retirado, superação de provação."}
}

# ============================================
# FUNÇÕES DE BUSCA
# ============================================
def buscar_carta_por_nome(nome_busca):
    nome_busca = nome_busca.strip().lower()
    
    variacoes = {
        "cavaleiro": "O Cavaleiro", "cavalo": "O Cavaleiro",
        "trevo": "O Trevo", "navio": "O Navio", "barco": "O Navio",
        "casa": "A Casa", "arvore": "A Árvore", "árvore": "A Árvore",
        "nuvens": "As Nuvens", "nuvem": "As Nuvens",
        "serpente": "A Serpente", "cobra": "A Serpente",
        "caixao": "O Caixão", "caixão": "O Caixão",
        "buque": "O Buquê", "buquê": "O Buquê", "flores": "O Buquê",
        "foice": "A Foice", "chicote": "O Chicote",
        "passaros": "Os Pássaros", "pássaros": "Os Pássaros", "passaro": "Os Pássaros",
        "crianca": "A Criança", "criança": "A Criança",
        "raposa": "A Raposa", "urso": "O Urso",
        "estrelas": "As Estrelas", "cegonha": "A Cegonha",
        "cachorro": "O Cachorro", "cao": "O Cachorro", "cão": "O Cachorro",
        "torre": "A Torre", "jardim": "O Jardim",
        "montanha": "A Montanha", "caminho": "O Caminho",
        "rato": "O Rato", "coracao": "O Coração", "coração": "O Coração",
        "alianca": "A Aliança", "aliança": "A Aliança",
        "livro": "O Livro", "carta": "A Carta",
        "homem": "O Homem", "mulher": "A Mulher",
        "lirios": "Os Lírios", "lírios": "Os Lírios",
        "sol": "O Sol", "lua": "A Lua", "chave": "A Chave",
        "peixe": "O Peixe", "ancora": "A Âncora", "âncora": "A Âncora",
        "cruz": "A Cruz"
    }
    
    if nome_busca in variacoes:
        nome_correto = variacoes[nome_busca]
        for id, carta in BARALHO_CIGANO.items():
            if carta["nome"].lower() == nome_correto.lower():
                return id, carta
    
    for id, carta in BARALHO_CIGANO.items():
        if carta["nome"].lower() == nome_busca or nome_busca in carta["nome"].lower():
            return id, carta
    
    return None, None

def validar_carta(nome_carta):
    id, carta = buscar_carta_por_nome(nome_carta)
    if carta:
        return True, id, carta
    return False, None, None

# ============================================
# FUNÇÃO DE INTERPRETAÇÃO
# ============================================
def interpretar_tiragem(cartas, pergunta_usuario):
    try:
        modelo = genai.GenerativeModel('gemini-pro')
        
        # Preparar dados das cartas
        cartas_descricao = []
        for carta_info in cartas:
            carta = carta_info['carta']
            orientacao = carta_info['orientacao']
            significado = carta['significado_invertido'] if orientacao == 'invertida' else carta['significado_normal']
            
            cartas_descricao.append(
                f"{carta_info['posicao']}: {carta['nome']} ({orientacao})\nSignificado: {significado}"
            )
        
        prompt = f"""Você é um especialista em Baralho Cigano.

Pergunta do consulente: {pergunta_usuario if pergunta_usuario else "Consulta geral"}

Cartas tiradas:
{chr(10).join(cartas_descricao)}

Faça uma interpretação empática, acolhedora e detalhada destas 3 cartas na sequência Passado → Presente → Futuro.
Conecte os significados entre si e responda diretamente à pergunta do consulente.
Use linguagem fluida, sem tópicos. Mínimo de 15 linhas."""
        
        response = modelo.generate_content(prompt)
        
        if response and response.text:
            return response.text
        else:
            return gerar_fallback(cartas, pergunta_usuario)
            
    except Exception as e:
        return gerar_fallback(cartas, pergunta_usuario)

def gerar_fallback(cartas, pergunta):
    """Fallback simples quando API falha"""
    if len(cartas) < 3:
        return "🔮 Aguarde..."
    
    texto = f"""
No **passado**, {cartas[0]['carta']['nome']} {'(invertida)' if cartas[0]['orientacao'] == 'invertida' else ''} revela: {cartas[0]['carta']['significado_invertido'] if cartas[0]['orientacao'] == 'invertida' else cartas[0]['carta']['significado_normal']}

**Agora, no presente**, {cartas[1]['carta']['nome']} {'(invertida)' if cartas[1]['orientacao'] == 'invertida' else ''} indica: {cartas[1]['carta']['significado_invertido'] if cartas[1]['orientacao'] == 'invertida' else cartas[1]['carta']['significado_normal']}

**Olhando adiante**, {cartas[2]['carta']['nome']} {'(invertida)' if cartas[2]['orientacao'] == 'invertida' else ''} anuncia: {cartas[2]['carta']['significado_invertido'] if cartas[2]['orientacao'] == 'invertida' else cartas[2]['carta']['significado_normal']}

💫 Esta sequência revela um processo de {pergunta if pergunta else 'transformação pessoal'}. Confie no seu caminho.
"""
    return texto

# ============================================
# INTERFACE PRINCIPAL - MÍNIMA
# ============================================
def main():
    st.title("🔮")
    st.markdown("<div style='text-align: center; margin-bottom: 40px;'><small>Baralho Cigano</small></div>", unsafe_allow_html=True)
    
    # ============================================
    # INICIALIZAÇÃO DO ESTADO
    # ============================================
    if 'etapa' not in st.session_state:
        st.session_state.etapa = 'pergunta'  # pergunta, carta1, carta2, carta3, resultado
    if 'pergunta' not in st.session_state:
        st.session_state.pergunta = ""
    if 'cartas' not in st.session_state:
        st.session_state.cartas = []
    if 'resultado' not in st.session_state:
        st.session_state.resultado = None
    if 'orientacoes' not in st.session_state:
        st.session_state.orientacoes = {}
    
    # ============================================
    # FLUXO DA INTERFACE
    # ============================================
    
    # Container centralizado
    with st.container():
        st.markdown('<div class="centralizado">', unsafe_allow_html=True)
        
        # ETAPA 1: PERGUNTA
        if st.session_state.etapa == 'pergunta':
            pergunta = st.text_area(
                "💭",
                placeholder="Qual sua pergunta?",
                height=120,
                key="pergunta_input",
                label_visibility="collapsed"
            )
            
            if pergunta:
                st.session_state.pergunta = pergunta
            
            if st.button("Próximo", use_container_width=True):
                if st.session_state.pergunta:
                    st.session_state.etapa = 'carta1'
                    st.rerun()
                else:
                    st.warning("Digite sua pergunta")
        
        # ETAPA 2: PRIMEIRA CARTA
        elif st.session_state.etapa == 'carta1':
            st.markdown("**1ª Carta - PASSADO**")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                carta1 = st.text_input(
                    "Nome da carta",
                    placeholder="Ex: O Cavaleiro",
                    key="carta1_input",
                    label_visibility="collapsed"
                )
            with col2:
                orientacao1 = st.selectbox(
                    "",
                    ["normal", "invertida"],
                    key="orientacao1",
                    label_visibility="collapsed"
                )
            
            if st.button("Próximo", use_container_width=True):
                if carta1:
                    valida, id_carta, carta = validar_carta(carta1)
                    if valida:
                        st.session_state.cartas = [{
                            'carta': carta,
                            'id': id_carta,
                            'orientacao': orientacao1,
                            'posicao': 'PASSADO'
                        }]
                        st.session_state.etapa = 'carta2'
                        st.rerun()
                    else:
                        st.error("Carta não encontrada")
                else:
                    st.warning("Digite o nome da carta")
        
        # ETAPA 3: SEGUNDA CARTA
        elif st.session_state.etapa == 'carta2':
            st.markdown("**2ª Carta - PRESENTE**")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                carta2 = st.text_input(
                    "Nome da carta",
                    placeholder="Ex: A Casa",
                    key="carta2_input",
                    label_visibility="collapsed"
                )
            with col2:
                orientacao2 = st.selectbox(
                    "",
                    ["normal", "invertida"],
                    key="orientacao2",
                    label_visibility="collapsed"
                )
            
            if st.button("Próximo", use_container_width=True):
                if carta2:
                    valida, id_carta, carta = validar_carta(carta2)
                    if valida:
                        st.session_state.cartas.append({
                            'carta': carta,
                            'id': id_carta,
                            'orientacao': orientacao2,
                            'posicao': 'PRESENTE'
                        })
                        st.session_state.etapa = 'carta3'
                        st.rerun()
                    else:
                        st.error("Carta não encontrada")
                else:
                    st.warning("Digite o nome da carta")
        
        # ETAPA 4: TERCEIRA CARTA
        elif st.session_state.etapa == 'carta3':
            st.markdown("**3ª Carta - FUTURO**")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                carta3 = st.text_input(
                    "Nome da carta",
                    placeholder="Ex: O Sol",
                    key="carta3_input",
                    label_visibility="collapsed"
                )
            with col2:
                orientacao3 = st.selectbox(
                    "",
                    ["normal", "invertida"],
                    key="orientacao3",
                    label_visibility="collapsed"
                )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Voltar", use_container_width=True):
                    st.session_state.etapa = 'carta2'
                    st.rerun()
            with col2:
                if st.button("🔮 Interpretar", use_container_width=True, type="primary"):
                    if carta3:
                        valida, id_carta, carta = validar_carta(carta3)
                        if valida:
                            st.session_state.cartas.append({
                                'carta': carta,
                                'id': id_carta,
                                'orientacao': orientacao3,
                                'posicao': 'FUTURO'
                            })
                            
                            with st.spinner("🔮 Interpretando..."):
                                resultado = interpretar_tiragem(
                                    st.session_state.cartas,
                                    st.session_state.pergunta
                                )
                                st.session_state.resultado = resultado
                                st.session_state.etapa = 'resultado'
                                st.rerun()
                        else:
                            st.error("Carta não encontrada")
                    else:
                        st.warning("Digite o nome da carta")
        
        # ETAPA 5: RESULTADO
        elif st.session_state.etapa == 'resultado':
            if st.session_state.resultado:
                st.markdown(f'<div class="resultado">{st.session_state.resultado}</div>', unsafe_allow_html=True)
            
            if st.button("🔄 Nova Consulta", use_container_width=True):
                for key in ['etapa', 'pergunta', 'cartas', 'resultado', 'orientacoes']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
