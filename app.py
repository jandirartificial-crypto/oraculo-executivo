import streamlit as st
import google.generativeai as genai
from datetime import datetime

# ============================================
# CONFIGURAÇÃO INICIAL - MÍNIMA ABSOLUTA
# ============================================
st.set_page_config(
    page_title="Baralho Cigano",
    page_icon="🃏",
    layout="centered"
)

# Configurar API do Gemini
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception as e:
    st.error("🔑 Erro na configuração da API.")
    st.stop()

# ============================================
# CSS - AJUSTADO PARA TEXTOS LONGOS
# ============================================
st.markdown("""
    <style>
        /* Reset total */
        .stApp { background-color: #FFFFFF; }
        .block-container { max-width: 700px; padding-top: 1rem; }
        
        /* Botão preto */
        .stButton button {
            background: #000000 !important;
            color: white !important;
            border: none !important;
            border-radius: 50px !important;
            padding: 10px 30px !important;
            width: 100%;
            font-weight: 500;
        }
        
        /* Campo de texto limpo */
        .stTextInput input {
            border-radius: 12px !important;
            border: 1px solid #DEE2E6 !important;
            padding: 12px !important;
        }
        
        /* Área de pergunta */
        .stTextArea textarea {
            border-radius: 16px !important;
            border: 2px solid #E9ECEF !important;
            padding: 20px !important;
            font-size: 18px !important;
            resize: none;
        }
        
        /* Esconder elementos padrão */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Resultado - adaptado para textos longos */
        .resultado {
            font-size: 18px;
            line-height: 1.8;
            color: #212529;
            text-align: left;
            padding: 40px 30px;
            background: #F8F9FA;
            border-radius: 24px;
            margin: 30px 0;
            box-shadow: 0 4px 12px rgba(0,0,0,0.03);
            font-family: 'Georgia', serif;
        }
        
        /* Estilo para o conselho do mentor */
        .conselho {
            font-size: 19px;
            line-height: 1.9;
            color: #1a1a1a;
        }
        
        .conselho p {
            margin-bottom: 25px;
        }
        
        .conselho strong {
            color: #000000;
            font-weight: 700;
        }
        
        .conselho em {
            color: #495057;
            font-style: italic;
        }
        
        .conselho .forcas {
            background: #e8f5e9;
            padding: 20px;
            border-radius: 16px;
            margin: 20px 0;
            border-left: 6px solid #2e7d32;
        }
        
        .conselho .limitacoes {
            background: #ffebee;
            padding: 20px;
            border-radius: 16px;
            margin: 20px 0;
            border-left: 6px solid #c62828;
        }
        
        .conselho .acoes {
            background: #e3f2fd;
            padding: 20px;
            border-radius: 16px;
            margin: 20px 0;
            border-left: 6px solid #1565c0;
        }
        
        .conselho .caminhos {
            background: #fff3e0;
            padding: 20px;
            border-radius: 16px;
            margin: 20px 0;
            border-left: 6px solid #ef6c00;
        }
        
        hr {
            margin: 30px 0;
            border: none;
            border-top: 2px solid #DEE2E6;
        }
        
        /* Título invisível */
        h1 {
            display: none !important;
        }
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
# FUNÇÃO DE INTERPRETAÇÃO - FOCO NO CONSELHO DO MENTOR
# ============================================
def interpretar_tiragem(cartas, pergunta_usuario):
    """Gera um conselho humanizado e completo baseado nas cartas."""
    try:
        modelo = genai.GenerativeModel('gemini-pro')
        
        # Preparar dados das cartas
        cartas_descricao = []
        for carta_info in cartas:
            carta = carta_info['carta']
            orientacao = carta_info['orientacao']
            significado = carta['significado_invertido'] if orientacao == 'invertida' else carta['significado_normal']
            
            cartas_descricao.append(
                f"{carta_info['posicao']}: {carta['nome']} ({orientacao})"
            )
        
        prompt = f"""
Você é um mentor espiritual sábio e acolhedor, especialista em Baralho Cigano. Sua missão é oferecer um conselho profundo, humanizado e prático para o consulente, baseado nas cartas que ele tirou.

Cartas: {cartas_descricao[0]}, {cartas_descricao[1]}, {cartas_descricao[2]}
Pergunta do consulente: {pergunta_usuario if pergunta_usuario else 'a vida'}

Escreva um **CONSELHO DO MENTOR** completo seguindo esta estrutura:

1. **Acolhimento inicial** (2-3 frases): Receba o consulente com calor humano, validando sua jornada e sua pergunta.

2. **O que as cartas revelam sobre você** (3-4 parágrafos):
   - Suas FORÇAS: quais qualidades, potenciais e recursos internos estão disponíveis para você agora.
   - Suas LIMITAÇÕES: quais padrões, medos ou bloqueios podem estar dificultando seu caminho (fale com cuidado e sem julgamento).

3. **Caminhos possíveis** (3-4 parágrafos):
   - Descreva 2-3 direções que você pode seguir a partir deste momento.
   - Para cada caminho, aponte o que ele exige de você e o que pode trazer.
   - Não faça escolhas pelo consulente, apenas ilumine as possibilidades.

4. **Ações práticas para agora** (5-7 itens):
   - Sugestões concretas, acionáveis e imediatas.
   - Podem ser pequenas mudanças de hábito, exercícios de autoconhecimento, atitudes diárias.

5. **Encerramento com sabedoria** (3-4 frases):
   - Uma mensagem final de confiança, esperança e empoderamento.

IMPORTANTE:
- Use linguagem acolhedora, como se estivesse falando diretamente com o consulente.
- Conecte TUDO à pergunta que ele fez.
- Seja específico, evite clichês vazios.
- Traga exemplos concretos de como ele pode aplicar o conselho na vida real.
- Lembre-se: você é um mentor, não um adivinho. Seu papel é iluminar, não determinar.
- Escreva em português fluente e natural.
"""
        
        response = modelo.generate_content(prompt)
        
        if response and response.text:
            return response.text
        else:
            return gerar_conselho_fallback(cartas, pergunta_usuario)
            
    except Exception as e:
        return gerar_conselho_fallback(cartas, pergunta_usuario)

def gerar_conselho_fallback(cartas, pergunta):
    """Fallback com conselho humanizado."""
    
    conselho = f"""
Querido(a) consulente,

Sinto uma energia muito especial ao redor da sua pergunta. Você está em um momento de busca sincera, e isso já demonstra uma coragem imensa. Quero que saiba que estou aqui para caminhar ao seu lado nesta reflexão, com todo o respeito pela sua história.

**O que as cartas revelam sobre você**

Suas forças são maiores do que você imagina. Existe em você uma capacidade de se reinventar que talvez ainda não tenha sido completamente acessada. As cartas mostram que você já passou por situações desafiadoras antes e que carrega consigo aprendizados valiosos — mesmo que, às vezes, eles fiquem escondidos sob o cansaço ou a dúvida. Sua intuição é um farol poderoso, mesmo quando as águas estão turvas.

Ao mesmo tempo, as cartas também apontam para algumas limitações que merecem sua atenção. Talvez exista um padrão de se cobrar demais, de querer respostas imediatas para perguntas que ainda estão amadurecendo. Ou quem sabe um medo de confiar no fluxo da vida, de soltar o controle e permitir que o novo chegue. Não se culpe por isso — essas são camadas de proteção que você construiu ao longo do caminho, e agora podemos olhar para elas com compaixão.

**Caminhos possíveis**

Olhando para o momento que você vive, enxergo pelo menos duas direções que podem se abrir:

Um caminho é o da **escuta interior mais profunda**. Isso significa desacelerar, criar espaços de silêncio na rotina, observar seus sentimentos sem julgamento. Esse caminho exige paciência, mas pode trazer clarezas que nenhuma resposta externa seria capaz de dar.

Outro caminho é o da **ação consciente**. Pequenos movimentos práticos, mesmo imperfeitos, que tiram você do lugar e geram aprendizado real. Esse caminho exige coragem para errar, mas pode trazer descobertas que só acontecem quando a gente se coloca em movimento.

Talvez exista ainda um terceiro caminho, que é justamente **aprender a sustentar a pergunta sem precisar respondê-la agora**. Algumas questões da vida não têm resposta imediata — e tudo bem. Elas nos acompanham, nos transformam, e um dia fazem sentido.

**Ações práticas para agora**

1. Reserve 10 minutos por dia para escrever livremente sobre o que sente, sem compromisso com "fazer sentido".
2. Escolha uma pequena ação que você vem adiando e faça hoje, mesmo que imperfeita.
3. Observe seus diálogos internos: quando você se critica, tente se falar com a mesma gentileza que usaria com um amigo querido.
4. Conecte-se com a natureza, mesmo que por poucos minutos — sinta o chão, o ar, o presente.
5. Pergunte-se: "O que eu realmente preciso agora?" e ouça a primeira resposta que vier, sem filtrar.
6. Se possível, converse com alguém de confiança sobre o que está sentindo — o simples ato de compartilhar já alivia.
7. Confie mais no seu corpo: ele sente antes da mente entender.

**Para encerrar**

Querido(a), lembre-se: você não está sozinho(a) nesta jornada. As perguntas que traz são legítimas, e as respostas virão no tempo certo — não necessariamente no tempo que você espera, mas no tempo que sua alma precisa para amadurecê-las. Confie no processo, confie em você. O caminho se faz ao caminhar, e cada passo, mesmo os mais hesitantes, já é uma conquista.

Com todo o carinho e respeito pela sua história,

Seu mentor.
"""
    return conselho

# ============================================
# INTERFACE - MÍNIMA ABSOLUTA
# ============================================
def main():
    # Sem título, sem ícone, apenas o fluxo
    
    # Inicialização do estado
    if 'etapa' not in st.session_state:
        st.session_state.etapa = 'pergunta'
    if 'pergunta' not in st.session_state:
        st.session_state.pergunta = ""
    if 'cartas' not in st.session_state:
        st.session_state.cartas = []
    if 'resultado' not in st.session_state:
        st.session_state.resultado = None
    
    # Container central
    with st.container():
        
        # ETAPA 1: APENAS PERGUNTA
        if st.session_state.etapa == 'pergunta':
            pergunta = st.text_area(
                " ",
                placeholder="Qual sua pergunta?",
                height=100,
                key="pergunta_input",
                label_visibility="collapsed"
            )
            
            if pergunta:
                st.session_state.pergunta = pergunta
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Próximo", use_container_width=True):
                if st.session_state.pergunta:
                    st.session_state.etapa = 'carta1'
                    st.rerun()
                else:
                    st.warning("Digite sua pergunta")
        
        # ETAPA 2: PRIMEIRA CARTA - SEM SELECT
        elif st.session_state.etapa == 'carta1':
            st.markdown("**1ª carta — passado**")
            
            carta1 = st.text_input(
                " ",
                placeholder="Ex: O Cavaleiro",
                key="carta1_input",
                label_visibility="collapsed"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Próximo", use_container_width=True):
                if carta1:
                    valida, id_carta, carta = validar_carta(carta1)
                    if valida:
                        st.session_state.cartas = [{
                            'carta': carta,
                            'id': id_carta,
                            'orientacao': 'normal',
                            'posicao': 'PASSADO'
                        }]
                        st.session_state.etapa = 'carta2'
                        st.rerun()
                    else:
                        st.error("Carta não encontrada")
                else:
                    st.warning("Digite o nome da carta")
        
        # ETAPA 3: SEGUNDA CARTA - SEM SELECT
        elif st.session_state.etapa == 'carta2':
            st.markdown("**2ª carta — presente**")
            
            carta2 = st.text_input(
                " ",
                placeholder="Ex: A Casa",
                key="carta2_input",
                label_visibility="collapsed"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Próximo", use_container_width=True):
                if carta2:
                    valida, id_carta, carta = validar_carta(carta2)
                    if valida:
                        st.session_state.cartas.append({
                            'carta': carta,
                            'id': id_carta,
                            'orientacao': 'normal',
                            'posicao': 'PRESENTE'
                        })
                        st.session_state.etapa = 'carta3'
                        st.rerun()
                    else:
                        st.error("Carta não encontrada")
                else:
                    st.warning("Digite o nome da carta")
        
        # ETAPA 4: TERCEIRA CARTA - SEM SELECT
        elif st.session_state.etapa == 'carta3':
            st.markdown("**3ª carta — futuro**")
            
            carta3 = st.text_input(
                " ",
                placeholder="Ex: O Sol",
                key="carta3_input",
                label_visibility="collapsed"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("←", use_container_width=True):
                    st.session_state.etapa = 'carta2'
                    st.rerun()
            with col2:
                if st.button("Receber conselho", use_container_width=True, type="primary"):
                    if carta3:
                        valida, id_carta, carta = validar_carta(carta3)
                        if valida:
                            st.session_state.cartas.append({
                                'carta': carta,
                                'id': id_carta,
                                'orientacao': 'normal',
                                'posicao': 'FUTURO'
                            })
                            
                            with st.spinner("Ouvindo sua história..."):
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
        
        # ETAPA 5: RESULTADO - CONSELHO DO MENTOR
        elif st.session_state.etapa == 'resultado':
            if st.session_state.resultado:
                st.markdown(f'<div class="resultado conselho">{st.session_state.resultado}</div>', unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Nova consulta", use_container_width=True):
                for key in ['etapa', 'pergunta', 'cartas', 'resultado']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

if __name__ == "__main__":
    main()
