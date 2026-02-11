import streamlit as st
import google.generativeai as genai
from datetime import datetime

# ============================================
# CONFIGURAÇÃO INICIAL E SEGREDOS
# ============================================
st.set_page_config(
    page_title="🔮 Baralho Cigano - Consulta Online",
    page_icon="🃏",
    layout="centered",
    initial_sidebar_state="auto"
)

# Configurar API do Gemini (via Streamlit Secrets)
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception as e:
    st.error("🔑 Erro na configuração da API. Verifique sua chave no Streamlit Secrets.")
    st.stop()

# ============================================
# CSS PERSONALIZADO
# ============================================
st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #1a1e24 0%, #2d3439 100%);
        }
        
        .carta-card {
            background: linear-gradient(145deg, #2c3e50, #1e2a36);
            border: 2px solid #4a5568;
            border-radius: 15px;
            padding: 20px 10px;
            margin: 10px 0;
            text-align: center;
            box-shadow: 0 10px 20px rgba(0,0,0,0.3);
            transition: transform 0.2s;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            min-height: 250px;
        }
        
        .carta-card:hover {
            transform: translateY(-5px);
            border-color: #9f7aea;
        }
        
        .carta-invertida {
            background: linear-gradient(145deg, #8b4513, #5d2e1b);
            border-color: #ff6b6b;
        }
        
        .carta-simbolo {
            font-size: 64px;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .carta-nome {
            font-size: 20px;
            font-weight: bold;
            color: white;
            margin-bottom: 5px;
            text-shadow: 1px 1px 2px black;
        }
        
        .carta-posicao {
            font-size: 14px;
            color: #e0e0e0;
            margin-bottom: 10px;
            font-style: italic;
            background: rgba(0,0,0,0.2);
            padding: 4px 8px;
            border-radius: 20px;
            display: inline-block;
            margin-left: auto;
            margin-right: auto;
        }
        
        .carta-orientacao {
            margin-top: 8px;
            font-size: 11px;
            color: #90a4ae;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        
        .interpretacao-box {
            background: rgba(0,0,0,0.2);
            border-left: 5px solid #9f7aea;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            font-size: 18px;
            line-height: 1.6;
            color: #e0e0e0;
        }
        
        .stButton button {
            background: linear-gradient(135deg, #9f7aea, #6b46c1);
            color: white;
            font-weight: bold;
            border: none;
            border-radius: 50px;
            padding: 10px 25px;
            transition: all 0.3s;
        }
        
        .stButton button:hover {
            background: linear-gradient(135deg, #b794f4, #805ad5);
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(159, 122, 234, 0.4);
        }
        
        .instrucoes-box {
            background: rgba(159, 122, 234, 0.1);
            border: 1px solid #9f7aea;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            color: #e0e0e0;
        }
    </style>
""", unsafe_allow_html=True)

# ============================================
# BASE DE CONHECIMENTO - 36 CARTAS DO BARALHO CIGANO
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
# FUNÇÕES PARA VALIDAÇÃO E BUSCA DE CARTAS
# ============================================
def buscar_carta_por_nome(nome_busca):
    """Busca uma carta pelo nome (case insensitive)"""
    nome_busca = nome_busca.strip().lower()
    
    # Mapeamento de variações comuns
    variacoes = {
        "cavaleiro": "O Cavaleiro",
        "cavalo": "O Cavaleiro",
        "trevo": "O Trevo",
        "navio": "O Navio",
        "barco": "O Navio",
        "casa": "A Casa",
        "arvore": "A Árvore",
        "nuvens": "As Nuvens",
        "nuvem": "As Nuvens",
        "serpente": "A Serpente",
        "cobra": "A Serpente",
        "caixao": "O Caixão",
        "buque": "O Buquê",
        "flores": "O Buquê",
        "foice": "A Foice",
        "chicote": "O Chicote",
        "passaros": "Os Pássaros",
        "passaro": "Os Pássaros",
        "crianca": "A Criança",
        "raposa": "A Raposa",
        "urso": "O Urso",
        "estrelas": "As Estrelas",
        "cegonha": "A Cegonha",
        "cachorro": "O Cachorro",
        "cao": "O Cachorro",
        "torre": "A Torre",
        "jardim": "O Jardim",
        "montanha": "A Montanha",
        "caminho": "O Caminho",
        "rato": "O Rato",
        "coracao": "O Coração",
        "alianca": "A Aliança",
        "livro": "O Livro",
        "carta": "A Carta",
        "homem": "O Homem",
        "mulher": "A Mulher",
        "lirios": "Os Lírios",
        "sol": "O Sol",
        "lua": "A Lua",
        "chave": "A Chave",
        "peixe": "O Peixe",
        "ancora": "A Âncora",
        "cruz": "A Cruz"
    }
    
    # Verificar se é uma variação
    if nome_busca in variacoes:
        nome_correto = variacoes[nome_busca]
        for id, carta in BARALHO_CIGANO.items():
            if carta["nome"].lower() == nome_correto.lower():
                return id, carta
    
    # Busca exata
    for id, carta in BARALHO_CIGANO.items():
        if carta["nome"].lower() == nome_busca:
            return id, carta
    
    # Busca parcial
    for id, carta in BARALHO_CIGANO.items():
        if nome_busca in carta["nome"].lower():
            return id, carta
    
    return None, None

def validar_carta(nome_carta):
    """Valida se a carta existe e retorna os dados"""
    id, carta = buscar_carta_por_nome(nome_carta)
    if carta:
        return True, id, carta
    return False, None, None

# ============================================
# FUNÇÃO PARA EXIBIR CARTAS
# ============================================
def criar_card_carta(carta, posicao, orientacao):
    """Cria um card HTML para exibir a carta"""
    
    classe_carta = "carta-card"
    if orientacao == 'invertida':
        classe_carta += " carta-invertida"
    
    simbolo_orientacao = " 🔄" if orientacao == 'invertida' else ""
    
    significado = carta['significado_invertido'] if orientacao == 'invertida' else carta['significado_normal']
    significado_resumo = significado[:80] + "..." if len(significado) > 80 else significado
    
    html_card = f"""
    <div class="{classe_carta}">
        <div class="carta-simbolo">{carta['simbolo']}</div>
        <div class="carta-nome">{carta['nome']}{simbolo_orientacao}</div>
        <div class="carta-posicao">📍 {posicao}</div>
        <div style="font-size: 13px; color: #d0d0d0; padding: 0 10px;">
            {significado_resumo}
        </div>
        <div class="carta-palavras">{carta['palavras_chave']}</div>
        <div class="carta-orientacao">{orientacao.upper()}</div>
    </div>
    """
    return html_card

# ============================================
# FUNÇÃO PRINCIPAL DO GEMINI
# ============================================
def interpretar_tiragem(cartas, pergunta_usuario):
    """Envia a tiragem para o Gemini e retorna a interpretação"""
    try:
        modelo = genai.GenerativeModel('gemini-pro')
        
        # Construir descrição das cartas
        cartas_descricao = []
        for carta_info in cartas:
            carta = carta_info['carta']
            cartas_descricao.append(
                f"{carta_info['posicao']}: {carta['nome']} ({carta_info['orientacao']}) - {carta['palavras_chave']}"
            )
        
        prompt = f"""Você é uma cartomante especialista em Baralho Cigano (Lenormand).

O consulente fez uma tiragem física de 3 cartas com seu próprio baralho.

PERGUNTA DO CONSULENTE: {pergunta_usuario if pergunta_usuario else "Consulta geral"}

CARTAS TIRADAS (na ordem: Passado, Presente, Futuro):
{chr(10).join(cartas_descricao)}

Faça uma leitura empática, positiva e detalhada destas cartas. 
Conecte os significados entre si, mostrando a evolução do Passado para o Presente e para o Futuro.
Use linguagem acolhedora e pessoal.
MÍNIMO DE 10 LINHAS DE INTERPRETAÇÃO."""
        
        generation_config = {
            "temperature": 0.8,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 1024,
        }
        
        response = modelo.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        if response and response.text:
            return response.text
        else:
            return gerar_fallback(cartas)
            
    except Exception as e:
        return gerar_fallback(cartas)

def gerar_fallback(cartas):
    """Gera uma interpretação de fallback quando a API falha"""
    nomes_cartas = [f"{c['carta']['nome']} ({c['orientacao']})" for c in cartas]
    
    return f"""🔮 **Sua Tiragem de Baralho Cigano**

✨ **Cartas reveladas:**
• Passado: {cartas[0]['carta']['nome']} ({cartas[0]['orientacao']})
• Presente: {cartas[1]['carta']['nome']} ({cartas[1]['orientacao']})
• Futuro: {cartas[2]['carta']['nome']} ({cartas[2]['orientacao']})

💫 **Mensagem das cartas:**

Sua tiragem mostra uma jornada de evolução e aprendizado. 
As cartas que você tirou fisicamente carregam sua energia única e pessoal.

**Passado - {cartas[0]['carta']['nome']}:** 
{cartas[0]['carta']['significado_invertido'] if cartas[0]['orientacao'] == 'invertida' else cartas[0]['carta']['significado_normal']}

**Presente - {cartas[1]['carta']['nome']}:** 
{cartas[1]['carta']['significado_invertido'] if cartas[1]['orientacao'] == 'invertida' else cartas[1]['carta']['significado_normal']}

**Futuro - {cartas[2]['carta']['nome']}:** 
{cartas[2]['carta']['significado_invertido'] if cartas[2]['orientacao'] == 'invertida' else cartas[2]['carta']['significado_normal']}

🌟 Confie na sabedoria das cartas e na sua intuição. O Baralho Cigano é um espelho da sua alma.

🙏 Lembre-se: você tem o poder de criar seu próprio destino."""

# ============================================
# INTERFACE PRINCIPAL
# ============================================
def main():
    st.title("🔮 Baralho Cigano Online")
    st.markdown("---")
    
    # Caixa de instruções
    st.markdown("""
    <div class="instrucoes-box">
        <h4>🎴 Como usar:</h4>
        <ol>
            <li>Pegue seu baralho físico de Baralho Cigano (36 cartas)</li>
            <li>Embaralhe e faça sua pergunta mentalmente</li>
            <li>Tire 3 cartas fisicamente na ordem: <strong>PASSADO, PRESENTE, FUTURO</strong></li>
            <li>Insira o nome das cartas abaixo e escolha se estão normais ou invertidas</li>
            <li>Clique em "INTERPRETAR CARTAS" para receber sua leitura</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    # Inicializar session state
    if 'cartas_adicionadas' not in st.session_state:
        st.session_state.cartas_adicionadas = []
    if 'interpretacao' not in st.session_state:
        st.session_state.interpretacao = None
    if 'pergunta' not in st.session_state:
        st.session_state.pergunta = ""
    
    # Sidebar - Instruções rápidas
    with st.sidebar:
        st.header("🎴 Suas Cartas")
        st.markdown("---")
        
        # Lista de cartas adicionadas
        if st.session_state.cartas_adicionadas:
            st.subheader("📋 Cartas selecionadas:")
            for i, carta_info in enumerate(st.session_state.cartas_adicionadas):
                orientacao_simbolo = "🔄" if carta_info['orientacao'] == 'invertida' else "⬆️"
                st.write(f"{i+1}. {carta_info['carta']['nome']} {orientacao_simbolo}")
                st.write(f"   📍 {carta_info['posicao']}")
                st.markdown("---")
        
        # Botão para limpar tudo
        if st.button("🗑️ Nova Tiragem", use_container_width=True):
            st.session_state.cartas_adicionadas = []
            st.session_state.interpretacao = None
            st.session_state.pergunta = ""
            st.rerun()
    
    # Área principal - Entrada das cartas
    st.subheader("🃏 Insira suas 3 cartas na ordem tirada")
    
    # Pergunta do consulente
    pergunta = st.text_area(
        "💭 Qual sua pergunta ou intenção para esta consulta?",
        value=st.session_state.pergunta,
        placeholder="Ex: Como está minha vida amorosa? O que vem pela frente no trabalho?",
        height=80,
        key="pergunta_input"
    )
    st.session_state.pergunta = pergunta
    
    # Criar 3 linhas para entrada das cartas
    posicoes = ["PASSADO", "PRESENTE", "FUTURO"]
    
    for i, posicao in enumerate(posicoes):
        st.markdown(f"### {i+1}ª Carta - {posicao}")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            nome_carta = st.text_input(
                f"Nome da carta",
                placeholder="Ex: O Cavaleiro, A Casa, O Sol...",
                key=f"carta_nome_{i}",
                value=st.session_state.get(f"carta_nome_{i}_value", "")
            )
        
        with col2:
            orientacao = st.selectbox(
                "Orientação",
                ["normal", "invertida"],
                key=f"carta_orientacao_{i}",
                index=0
            )
        
        with col3:
            if st.button(f"✅ Adicionar {posicao}", key=f"btn_adicionar_{i}"):
                if nome_carta:
                    valida, id_carta, carta = validar_carta(nome_carta)
                    
                    if valida:
                        # Verificar se já não adicionou esta posição
                        posicao_ja_adicionada = False
                        for c in st.session_state.cartas_adicionadas:
                            if c['posicao'] == posicao:
                                posicao_ja_adicionada = True
                                break
                        
                        if not posicao_ja_adicionada:
                            # Adicionar carta
                            st.session_state.cartas_adicionadas.append({
                                'carta': carta,
                                'id': id_carta,
                                'orientacao': orientacao,
                                'posicao': posicao
                            })
                            # Ordenar por posição
                            ordem_posicoes = {"PASSADO": 0, "PRESENTE": 1, "FUTURO": 2}
                            st.session_state.cartas_adicionadas.sort(key=lambda x: ordem_posicoes[x['posicao']])
                            
                            st.session_state[f"carta_nome_{i}_value"] = ""
                            st.success(f"✅ {carta['nome']} adicionada ao {posicao}!")
                            st.rerun()
                        else:
                            st.warning(f"⚠️ Você já adicionou uma carta para {posicao}")
                    else:
                        # Sugerir cartas similares
                        st.error(f"❌ Carta '{nome_carta}' não encontrada!")
                        
                        # Buscar sugestões
                        sugestoes = []
                        for id_c, carta_c in BARALHO_CIGANO.items():
                            if nome_carta.lower() in carta_c['nome'].lower()[:len(nome_carta)]:
                                sugestoes.append(carta_c['nome'])
                        
                        if sugestoes:
                            st.info(f"💡 Você quis dizer: {', '.join(sugestoes[:3])}?")
                else:
                    st.warning("⚠️ Digite o nome da carta")
        
        st.markdown("---")
    
    # Verificar se todas as 3 cartas foram adicionadas
    if len(st.session_state.cartas_adicionadas) == 3:
        st.success("✅ Todas as 3 cartas foram adicionadas com sucesso!")
        
        # Exibir as cartas adicionadas
        st.subheader("🃏 Suas Cartas")
        cols = st.columns(3)
        
        for idx, (col, carta_info) in enumerate(zip(cols, st.session_state.cartas_adicionadas)):
            with col:
                html_card = criar_card_carta(
                    carta_info['carta'],
                    carta_info['posicao'],
                    carta_info['orientacao']
                )
                st.markdown(html_card, unsafe_allow_html=True)
        
        # Botão para interpretação
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("🔮 **INTERPRETAR CARTAS**", use_container_width=True, type="primary"):
                with st.spinner("🔮 Consultando os mistérios do Baralho Cigano..."):
                    interpretacao = interpretar_tiragem(
                        st.session_state.cartas_adicionadas,
                        st.session_state.pergunta
                    )
                    st.session_state.interpretacao = interpretacao
                    st.rerun()
    
    elif len(st.session_state.cartas_adicionadas) > 0:
        st.info(f"📌 Você adicionou {len(st.session_state.cartas_adicionadas)} de 3 cartas. Complete a tiragem.")
    
    # Exibir interpretação
    if st.session_state.interpretacao:
        st.markdown("---")
        st.subheader("🔮 Mensagem do Baralho Cigano")
        
        with st.container():
            st.markdown('<div class="interpretacao-box">', unsafe_allow_html=True)
            st.markdown(st.session_state.interpretacao)
            st.markdown('</div>', unsafe_allow_html=True)
            st.caption("🙏 Lembre-se: As cartas são um guia, não uma verdade absoluta. O livre arbítrio sempre prevalece.")
        
        # Botão para nova consulta
        if st.button("🔄 Nova Tiragem", key="nova_consulta_fim"):
            st.session_state.cartas_adicionadas = []
            st.session_state.interpretacao = None
            st.session_state.pergunta = ""
            st.rerun()
    
    # Rodapé
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #a0a0a0; padding: 20px;'>
            <small>
            🔮 Baralho Cigano Tradicional • 36 Lâminas • Interpretação com IA Gemini<br>
            ⚡ Use seu baralho físico, insira as cartas tiradas<br>
            ✨ Cada consulta é única e pessoal
            </small>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
