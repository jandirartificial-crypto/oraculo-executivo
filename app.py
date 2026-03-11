import streamlit as st
import google.generativeai as genai
from datetime import datetime
import json
import re
import time

# ============================================
# CONFIGURAÇÃO INICIAL
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
# CSS
# ============================================
st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF; }
        .block-container { max-width: 800px; padding-top: 1rem; }
        
        .stButton button {
            background: #000000 !important;
            color: white !important;
            border: none !important;
            border-radius: 50px !important;
            padding: 10px 30px !important;
            width: 100%;
            font-weight: 500;
        }
        
        .stTextInput input {
            border-radius: 12px !important;
            border: 1px solid #DEE2E6 !important;
            padding: 12px !important;
        }
        
        .stTextArea textarea {
            border-radius: 16px !important;
            border: 2px solid #E9ECEF !important;
            padding: 20px !important;
            font-size: 18px !important;
            resize: none;
        }
        
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
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
        
        .resultado h2 {
            font-size: 24px;
            font-weight: 600;
            color: #000000;
            margin-top: 40px;
            margin-bottom: 20px;
            text-align: left;
            border-bottom: 2px solid #000000;
            padding-bottom: 10px;
        }
        
        .resultado h3 {
            font-size: 20px;
            font-weight: 600;
            color: #000000;
            margin-top: 25px;
            margin-bottom: 10px;
        }
        
        .resultado p {
            margin-bottom: 20px;
        }
        
        .progresso-cartas {
            text-align: center;
            color: #6C757D;
            font-size: 14px;
            margin-bottom: 20px;
            letter-spacing: 1px;
        }
        
        .instrucao-chat {
            background: #F8F9FA;
            border-radius: 12px;
            padding: 15px;
            margin: 20px 0;
            text-align: center;
            border: 1px dashed #000000;
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
# CLASSE DE CHAT PARA MANTER CONTEXTO
# ============================================
class MentorChat:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')
        self.chat = None
        self.historico = []
        
    def iniciar_conversa(self, cartas, pergunta):
        """Inicia a conversa com o contexto completo"""
        
        # Posições da tiragem Afrodite
        posicoes = [
            "Pensamentos e Intenções do consulente",
            "Sentimentos do consulente pela companheira",
            "Atração sexual, desejos e libido do consulente por ela",
            "Pensamentos e Intenções da companheira",
            "Sentimentos da companheira pelo consulente",
            "Atração sexual, desejos e libido dela por ele",
            "O desfecho: O que resultará dessa relação"
        ]
        
        # Preparar dados das cartas
        cartas_descricao = []
        for i, carta_info in enumerate(cartas):
            carta = carta_info['carta']
            orientacao = carta_info['orientacao']
            cartas_descricao.append(
                f"{i+1}. {posicoes[i]}: {carta['nome']} ({orientacao})"
            )
        
        cartas_texto = "\n".join(cartas_descricao)
        
        # Prompt inicial com a estrutura aprovada
        prompt_inicial = f"""
Você é um mentor espiritual sábio e acolhedor, especialista em Baralho Cigano. Você está iniciando uma conversa profunda com um consulente que busca orientação sobre seu relacionamento.

## CONTEXTO COMPLETO DA CONSULTA:
Pergunta do consulente: {pergunta if pergunta else "O que está acontecendo no meu relacionamento?"}

## AS CARTAS TIRADAS (MÉTODO AFRODITE):
{cartas_texto}

## INSTRUÇÕES PARA A RESPOSTA:

Escreva a PRIMEIRA PARTE da sua orientação, contendo APENAS estes tópicos:

## O QUE SE PASSA NA SUA MENTE E NO SEU CORAÇÃO
(Interpretação DETALHADA das cartas 1, 2 e 3)

Para CADA carta:
**Carta [Número] – [Nome da Carta]: [Posição]**
- 3-4 parágrafos com interpretação profunda
- Inclua o significado espiritual relacionado à situação atual do consulente
- Termine com "O que isso significa na prática:" e uma aplicação direta

## O QUE SE PASSA NA MENTE E NO CORAÇÃO DELA
(Interpretação DETALHADA das cartas 4, 5 e 6 - mesma estrutura acima)

## PARA ONDE TUDO ISSO ESTÁ LEVANDO
(Interpretação da carta 7 - o desfecho)
- Pelo menos 4 parágrafos
- Mostre tendências e possibilidades
- Inclua o significado espiritual do desfecho
- Termine com "O que isso significa na prática:"

IMPORTANTE:
- Esta é apenas a PARTE 1. Você vai parar aqui e aguardar o consulente pedir para continuar.
- Use linguagem acolhedora e acessível
- Conecte TUDO à pergunta específica do consulente
- Seja direto, mas nunca cruel
- A verdade pode doer, mas deve vir com acolhimento

Seu tom deve ser de um mentor que caminha junto, não de um oráculo distante.
"""
        
        self.chat = self.model.start_chat(history=[])
        response = self.chat.send_message(prompt_inicial)
        self.historico.append({"role": "mentor", "content": response.text})
        return response.text
    
    def continuar_parte_2(self):
        """Gera a segunda parte mantendo o contexto"""
        prompt = """
Ótimo. Agora, continuando a mesma conversa, escreva a SEGUNDA PARTE da sua orientação, contendo APENAS estes tópicos:

## O QUE A CIÊNCIA DIZ SOBRE O QUE VOCÊ ESTÁ VIVENDO
(6-8 fatos científicos diretos sobre relacionamentos)
- Para CADA fato: um parágrafo explicativo aplicado à situação do consulente
- Use linguagem acessível, não acadêmica
- Exemplos: estresse crônico, desejo feminino, comunicação, hormônios, etc.

## O QUE A FILOSOFIA ENSINA SOBRE O SEU MOMENTO
(Reflexões sobre sabedoria ancestral aplicada à sua vida)

IMPORTANTE: Ao falar sobre Estoicismo, Budismo, Sikhismo, Existencialismo:
- NÃO use os nomes das escolas como títulos
- NÃO assuma que o consulente conhece ou concorda com estas doutrinas
- Apresente APENAS a SABEDORIA prática contida nelas, de forma genérica
- Exemplo: em vez de "O Estoicismo ensina...", use "Uma sabedoria antiga nos lembra que existem coisas que dependem de nós e coisas que não dependem..."
- Exemplo: em vez de "O Budismo diz...", use "Há um ensinamento profundo sobre a impermanência de todas as coisas..."

Cada reflexão deve ter 2-3 parágrafos aplicados diretamente à situação do consulente.

Lembre-se de manter o MESMO TOM acolhedor e profundo da primeira parte, e conectar com o que já foi dito.
"""
        response = self.chat.send_message(prompt)
        self.historico.append({"role": "mentor", "content": response.text})
        return response.text
    
    def continuar_parte_3(self):
        """Gera a terceira parte mantendo o contexto"""
        prompt = """
Agora, a TERCEIRA E ÚLTIMA PARTE da sua orientação, contendo APENAS estes tópicos:

## AS ILUSÕES QUE VOCÊ PODE ESTAR ALIMENTANDO
(6-8 ilusões comuns em relacionamentos)
- Para CADA: "**Ilusão:** [frase entre aspas]" seguido de 2-3 parágrafos
- Desmonte a ilusão com exemplos práticos e aplicados à situação
- Mostre o que é realidade vs o que é projeção

## O QUE VOCÊ PODE FAZER AGORA – AÇÕES CONCRETAS
(10-12 ações práticas, numeradas)
- Para CADA: um parágrafo explicativo detalhado
- Como implementar no dia a dia
- Exemplos específicos
- O que esperar ao colocar em prática

## PALAVRAS FINAIS
(Um encerramento poderoso de 4-5 parágrafos)
- Retome as cartas e a jornada
- Ofereça esperança e direção
- Reforce que a escolha é do consulente
- Inclua uma mensagem espiritual de acolhimento

Finalize com uma nota de que o mentor está disponível para novas reflexões, mas que agora a jornada é do consulente.

Lembre-se de manter o tom acolhedor e prático de toda a conversa.
"""
        response = self.chat.send_message(prompt)
        self.historico.append({"role": "mentor", "content": response.text})
        return response.text

# ============================================
# INTERFACE PRINCIPAL
# ============================================
def main():
    st.markdown("<h1 style='display: block; text-align: center; font-size: 24px; margin-bottom: 10px;'>🔮 BARALHO CIGANO</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6C757D; margin-bottom: 30px;'>Método: Afrodite • 7 cartas para relacionamentos</p>", unsafe_allow_html=True)
    
    # Inicialização do estado
    if 'etapa' not in st.session_state:
        st.session_state.etapa = 'pergunta'
    if 'pergunta' not in st.session_state:
        st.session_state.pergunta = ""
    if 'cartas' not in st.session_state:
        st.session_state.cartas = []
    if 'chat' not in st.session_state:
        st.session_state.chat = None
    if 'partes_recebidas' not in st.session_state:
        st.session_state.partes_recebidas = []
    if 'carta_atual' not in st.session_state:
        st.session_state.carta_atual = 1
    
    # Posições para interface
    posicoes_interface = [
        "1ª carta — Pensamentos e Intenções (você)",
        "2ª carta — Sentimentos (você)",
        "3ª carta — Desejo sexual (você)",
        "4ª carta — Pensamentos e Intenções (ela)",
        "5ª carta — Sentimentos (ela)",
        "6ª carta — Desejo sexual (ela)",
        "7ª carta — O desfecho"
    ]
    
    # Container central
    with st.container():
        
        # ETAPA 1: APENAS PERGUNTA
        if st.session_state.etapa == 'pergunta':
            pergunta = st.text_area(
                " ",
                placeholder="Qual sua pergunta sobre o relacionamento?",
                height=100,
                key="pergunta_input",
                label_visibility="collapsed"
            )
            
            if pergunta:
                st.session_state.pergunta = pergunta
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Começar tiragem", use_container_width=True):
                if st.session_state.pergunta:
                    st.session_state.etapa = 'carta1'
                    st.rerun()
                else:
                    st.warning("Digite sua pergunta")
        
        # ETAPAS 2 a 8: SETE CARTAS
        elif st.session_state.etapa.startswith('carta') and st.session_state.etapa != 'conversa':
            carta_num = int(st.session_state.etapa.replace('carta', ''))
            
            st.markdown(f"**{posicoes_interface[carta_num-1]}**")
            st.markdown(f"<div class='progresso-cartas'>Carta {carta_num} de 7</div>", unsafe_allow_html=True)
            
            carta_input = st.text_input(
                " ",
                placeholder="Ex: O Cavaleiro",
                key=f"carta{carta_num}_input",
                label_visibility="collapsed"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if carta_num > 1:
                    if st.button("← Voltar", use_container_width=True):
                        st.session_state.etapa = f'carta{carta_num-1}'
                        st.rerun()
            
            with col2:
                if carta_num < 7:
                    if st.button("Próximo", use_container_width=True):
                        if carta_input:
                            valida, id_carta, carta = validar_carta(carta_input)
                            if valida:
                                st.session_state.cartas = [c for c in st.session_state.cartas if c.get('posicao_num') != carta_num]
                                st.session_state.cartas.append({
                                    'carta': carta,
                                    'id': id_carta,
                                    'orientacao': 'normal',
                                    'posicao': posicoes_interface[carta_num-1],
                                    'posicao_num': carta_num
                                })
                                st.session_state.cartas.sort(key=lambda x: x['posicao_num'])
                                st.session_state.etapa = f'carta{carta_num+1}'
                                st.rerun()
                            else:
                                st.error("Carta não encontrada")
                        else:
                            st.warning("Digite o nome da carta")
                
                else:  # Última carta (7)
                    if st.button("Iniciar Leitura", use_container_width=True, type="primary"):
                        if carta_input:
                            valida, id_carta, carta = validar_carta(carta_input)
                            if valida:
                                st.session_state.cartas = [c for c in st.session_state.cartas if c.get('posicao_num') != 7]
                                st.session_state.cartas.append({
                                    'carta': carta,
                                    'id': id_carta,
                                    'orientacao': 'normal',
                                    'posicao': posicoes_interface[6],
                                    'posicao_num': 7
                                })
                                st.session_state.cartas.sort(key=lambda x: x['posicao_num'])
                                
                                with st.spinner("🎭 Iniciando conversa com seu mentor..."):
                                    chat = MentorChat()
                                    primeira_parte = chat.iniciar_conversa(st.session_state.cartas, st.session_state.pergunta)
                                    st.session_state.chat = chat
                                    st.session_state.partes_recebidas = [primeira_parte]
                                    st.session_state.etapa = 'conversa'
                                    st.rerun()
                            else:
                                st.error("Carta não encontrada")
                        else:
                            st.warning("Digite o nome da carta")
        
        # ETAPA 9: CONVERSA CONTÍNUA COM O MENTOR
        elif st.session_state.etapa == 'conversa':
            
            # Mostrar todas as partes já recebidas
            if st.session_state.partes_recebidas:
                for i, parte in enumerate(st.session_state.partes_recebidas):
                    st.markdown(f'<div class="resultado">{parte}</div>', unsafe_allow_html=True)
                    if i < len(st.session_state.partes_recebidas) - 1:
                        st.markdown("<hr>", unsafe_allow_html=True)
            
            # Verificar se já temos todas as 3 partes
            if len(st.session_state.partes_recebidas) < 3:
                
                # Instrução para continuar
                st.markdown("""
                <div class="instrucao-chat">
                    <p>✨ O mentor fez uma pausa para que você absorva estas palavras.</p>
                    <p>Quando estiver pronto para continuar, clique no botão abaixo.</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Botão para próxima parte
                if st.button("Continuar leitura →", use_container_width=True, type="primary"):
                    with st.spinner("O mentor está refletindo mais profundamente..."):
                        
                        if len(st.session_state.partes_recebidas) == 1:
                            # Segunda parte
                            nova_parte = st.session_state.chat.continuar_parte_2()
                        else:
                            # Terceira parte
                            nova_parte = st.session_state.chat.continuar_parte_3()
                        
                        st.session_state.partes_recebidas.append(nova_parte)
                        st.rerun()
            
            else:
                # Todas as partes foram recebidas - oferecer nova consulta
                st.markdown("---")
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("🔄 Nova consulta", use_container_width=True):
                        for key in ['etapa', 'pergunta', 'cartas', 'chat', 'partes_recebidas', 'carta_atual']:
                            if key in st.session_state:
                                del st.session_state[key]
                        st.rerun()

if __name__ == "__main__":
    main()
