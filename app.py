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
        .block-container { max-width: 800px; padding-top: 1rem; }
        
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
        
        /* Estilo para títulos dentro do resultado */
        .resultado h1 {
            display: block;
            font-size: 28px;
            font-weight: 700;
            color: #000000;
            margin-top: 40px;
            margin-bottom: 20px;
            text-align: left;
            border-bottom: 2px solid #000000;
            padding-bottom: 10px;
        }
        
        .resultado h2 {
            font-size: 22px;
            font-weight: 600;
            color: #000000;
            margin-top: 30px;
            margin-bottom: 15px;
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
        
        .resultado hr {
            margin: 30px 0;
            border: none;
            border-top: 2px solid #DEE2E6;
        }
        
        /* Título invisível */
        h1 {
            display: none !important;
        }
        
        /* Indicador de progresso para 7 cartas */
        .progresso-cartas {
            text-align: center;
            color: #6C757D;
            font-size: 14px;
            margin-bottom: 20px;
            letter-spacing: 1px;
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
# FUNÇÃO DE INTERPRETAÇÃO - MÉTODO AFRODITE (7 CARTAS)
# ============================================
def interpretar_tiragem_afrodite(cartas, pergunta_usuario):
    """Gera uma interpretação profunda para a tiragem de Afrodite (7 cartas)."""
    try:
        modelo = genai.GenerativeModel('gemini-pro')
        
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
        
        # Preparar dados das cartas com suas posições
        cartas_descricao = []
        for i, carta_info in enumerate(cartas):
            carta = carta_info['carta']
            orientacao = carta_info['orientacao']
            significado = carta['significado_invertido'] if orientacao == 'invertida' else carta['significado_normal']
            
            cartas_descricao.append(
                f"{i+1}. {posicoes[i]}: {carta['nome']} ({orientacao})"
            )
        
        # Criar lista detalhada para o prompt
        cartas_detalhadas = "\n".join(cartas_descricao)
        
        prompt = f"""
Você é um mentor espiritual sábio e acolhedor, especialista em Baralho Cigano. Sua missão é oferecer um conselho profundo, humanizado e prático para o consulente, baseado na tiragem de Afrodite (7 cartas para análise de relacionamento).

## A PERGUNTA DO CONSULENTE:
{pergunta_usuario if pergunta_usuario else "O que está acontecendo no meu relacionamento?"}

## AS CARTAS TIRADAS:
{cartas_detalhadas}

## INSTRUÇÕES PARA A RESPOSTA:

Escreva uma resposta no formato de um **LIVRO**, com títulos principais que organizam o texto em seções. A linguagem deve ser acolhedora, direta e profunda, como um mentor que fala com clareza e sabedoria.

### ESTRUTURA OBRIGATÓRIA:

# 🔮 O LIVRO DA SUA RELAÇÃO
*Um subtítulo acolhedor*

## ✉️ CARTA AO CONSULENTE
(Um parágrafo de abertura acolhendo a pessoa e validando sua jornada)

## 🃏 AS SETE CARTAS QUE REVELAM SUA HISTÓRIA
(Apresente as posições da tiragem de Afrodite em formato de tabela ou lista clara)

## 💭 O QUE SE PASSA NA SUA MENTE E NO SEU CORAÇÃO
(Interpretação das cartas 1, 2 e 3 - focando em pensamentos, sentimentos e desejos do consulente)

## 🐍 O QUE SE PASSA NA MENTE E NO CORAÇÃO DELA
(Interpretação das cartas 4, 5 e 6 - focando nos pensamentos, sentimentos e desejos da companheira)

## ⚓ PARA ONDE TUDO ISSO ESTÁ LEVANDO
(Interpretação da carta 7 - o desfecho natural se nada mudar)

## 🔗 O DIÁLOGO SILENCIOSO ENTRE AS CARTAS
(Análise das interações entre as cartas - o que elas revelam quando conversam entre si)

## 🧠 O QUE A CIÊNCIA DIZ SOBRE O QUE VOCÊ ESTÁ VIVENDO
(3-4 fatos científicos diretos relacionados à situação, sem explicações longas)

## 🏛️ O QUE A FILOSOFIA ENSINA SOBRE O SEU MOMENTO
(Estoicismo, Budismo, Existencialismo - um parágrafo para cada, aplicado diretamente ao caso)

## 💔 AS ILUSÕES QUE VOCÊ PODE ESTAR ALIMENTANDO
(3-4 crenças limitantes ou ilusões comuns em relacionamentos, desmontadas com clareza)

## ✅ O QUE VOCÊ PODE FAZER AGORA – AÇÕES CONCRETAS
(7-10 ações práticas, específicas e imediatas)

## 🌅 PALAVRAS FINAIS
(Um encerramento poético e empoderador)

### DIRETRIZES DE TOM:

- Use linguagem acolhedora, mas direta - como um mentor que não esconde a verdade.
- Foque no presente e futuro, usando o passado apenas como referência para aprendizado.
- As cartas devem ser interpretadas pelo aspecto comportamental, de pensamentos, sentimentos e energia.
- Inclua ciência (neurociência, psicologia) como fatos pontuais, não como aulas.
- Inclua filosofia (estoicismo, budismo, existencialismo) aplicada diretamente à situação.
- Desmonte ilusões que o consulente pode estar alimentando.
- Termine com ações práticas e um acolhimento final.
- O texto deve ter qualidade de livro, podendo ser transformado em PDF.
"""
        
        response = modelo.generate_content(prompt)
        
        if response and response.text:
            return response.text
        else:
            return gerar_conselho_fallback_afrodite(cartas, pergunta_usuario)
            
    except Exception as e:
        return gerar_conselho_fallback_afrodite(cartas, pergunta_usuario)

def gerar_conselho_fallback_afrodite(cartas, pergunta):
    """Fallback para a tiragem Afrodite."""
    
    if len(cartas) < 7:
        return "Não foi possível gerar a interpretação completa. Por favor, tente novamente."
    
    # Extrair nomes das cartas
    nomes = [carta_info['carta']['nome'] for carta_info in cartas]
    
    conselho = f"""
# 🔮 O LIVRO DA SUA RELAÇÃO
*Um mergulho profundo no que suas cartas revelam*

## ✉️ CARTA AO CONSULENTE

Prezado, a pergunta que você traz é sobre amor, sobre conexão, sobre o que ainda existe entre duas pessoas que um dia se escolheram. Não estamos diante de uma simples briga de casal – estamos diante de um relacionamento que adoeceu e precisa de diagnóstico antes do tratamento. Nas próximas páginas, você encontrará não apenas o significado das cartas, mas um mapa para entender o que realmente está acontecendo – e o que você pode fazer a respeito.

## 🃏 AS SETE CARTAS QUE REVELAM SUA HISTÓRIA

| Carta | Posição | Nome |
|-------|---------|------|
| 1 | Pensamentos e Intenções do consulente | {nomes[0]} |
| 2 | Sentimentos do consulente pela companheira | {nomes[1]} |
| 3 | Atração sexual, desejos e libido do consulente | {nomes[2]} |
| 4 | Pensamentos e Intenções da companheira | {nomes[3]} |
| 5 | Sentimentos da companheira pelo consulente | {nomes[4]} |
| 6 | Atração sexual, desejos e libido dela | {nomes[5]} |
| 7 | O desfecho da relação | {nomes[6]} |

## 💭 O QUE SE PASSA NA SUA MENTE E NO SEU CORAÇÃO

**Carta 1 – {nomes[0]}: Seus pensamentos e intenções**
Esta carta revela o estado da sua mente neste momento. Seus pensamentos estão acelerados ou tranquilos? Direcionados para ação ou para reflexão? Observe o que esta carta diz sobre como você está processando a situação.

**Carta 2 – {nomes[1]}: Seus sentimentos por ela**
Aqui está a verdade do seu coração. O que você realmente sente por ela, para além das mágoas e dos desgastes. Esse sentimento é a base sobre a qual qualquer reconstrução pode acontecer.

**Carta 3 – {nomes[2]}: Seu desejo sexual por ela**
O desejo fala de atração, de libido, de vontade de se aproximar fisicamente. Esta carta mostra se esse canal ainda está aberto ou se ele foi fechado pela rotina e pelos conflitos.

## 🐍 O QUE SE PASSA NA MENTE E NO CORAÇÃO DELA

**Carta 4 – {nomes[3]}: Pensamentos e intenções dela**
A mente dela pode estar clara ou confusa, aberta ou defensiva. Esta carta revela como ela está processando a relação internamente.

**Carta 5 – {nomes[4]}: Sentimentos dela por você**
Apesar das aparências, o que ela realmente sente? Esta carta mostra se o amor ainda existe ou se já foi substituído por indiferença ou ressentimento.

**Carta 6 – {nomes[5]}: Desejo sexual dela por você**
O desejo feminino é complexo e muitas vezes reativo à segurança emocional. Esta carta indica se ela ainda sente atração ou se esse canal foi temporariamente interrompido.

## ⚓ PARA ONDE TUDO ISSO ESTÁ LEVANDO

**Carta 7 – {nomes[6]}: O desfecho**
Esta carta não é uma sentença, mas uma tendência. Mostra para onde a relação está caminhando SE nada mudar. É um aviso, não um destino.

## 🔗 O DIÁLOGO SILENCIOSO ENTRE AS CARTAS

Observe a dança entre o que você sente e o que ela sente, entre o que você deseja e o que ela deseja. Existe sincronia ou assincronia? Vocês estão no mesmo comprimento de onda ou em frequências opostas?

## 🧠 O QUE A CIÊNCIA DIZ SOBRE O QUE VOCÊ ESTÁ VIVENDO

- **Estresse crônico**: Casais em conflito constante têm níveis elevados de cortisol, o que afeta a comunicação e o desejo.
- **Desejo feminino**: Estudos mostram que a atração sexual na mulher está diretamente ligada à sensação de segurança emocional.
- **Comunicação**: O cérebro processa críticas como ameaça física, ativando as mesmas áreas de defesa.

## 🏛️ O QUE A FILOSOFIA ENSINA SOBRE O SEU MOMENTO

**Estoicismo**: Foque no que depende de você – suas ações, suas escolhas, sua forma de reagir. O resto, inclusive os sentimentos dela, não está sob seu controle.

**Budismo**: Tudo é impermanente. Esta crise vai passar. A questão é o que restará depois. O apego a como as coisas "deveriam ser" é a raiz do sofrimento.

**Existencialismo**: Você é livre para escolher. As cartas mostram tendências, não destinos. A responsabilidade pela decisão é sua.

## 💔 AS ILUSÕES QUE VOCÊ PODE ESTAR ALIMENTANDO

1. **"Se eu explicar direito, ela vai entender."** Não, não vai. Quando alguém está na defensiva, explicações soam como justificativas.

2. **"Se ela me amasse, me desejaria."** Amor e desejo são circuitos diferentes. Ela pode amar e ainda assim não desejar agora.

3. **"Preciso resolver isso rápido."** Relações desgastadas por anos não se curam em dias.

4. **"O problema é só [circunstância externa]."** As circunstâncias agravam, mas raramente são a causa raiz.

## ✅ O QUE VOCÊ PODE FAZER AGORA – AÇÕES CONCRETAS

1. **Desacelere**: Estabeleça 30 dias sem conversas pesadas sobre a relação.
2. **Crie segurança**: Consistência, previsibilidade e escuta ativa.
3. **Use comunicação não-violenta**: "Quando você... eu sinto... porque preciso... você topa...?"
4. **Rituais mínimos**: 10 minutos por dia lado a lado, sem obrigação de conversar.
5. **Cuide de si**: Sua energia e autoestima afetam diretamente a relação.
6. **Observe sem reagir**: Apenas note os padrões dela sem tentar corrigir.
7. **Estabeleça um marco**: 60 dias para reavaliar se houve mudança.

## 🌅 PALAVRAS FINAIS

O livro que você acabou de ler não é um oráculo – é um espelho. As cartas não criaram sua realidade, apenas a revelaram. O que você escolher fazer com essa informação é com você. Mas saiba que, tendo chegado até aqui, você já deu o primeiro passo: o da coragem de olhar para a verdade.

Com respeito pela sua história,

*Seu mentor.*
"""
    return conselho

# ============================================
# INTERFACE - MÉTODO AFRODITE (7 CARTAS)
# ============================================
def main():
    # Título
    st.markdown("<h1 style='display: block; text-align: center; font-size: 24px; margin-bottom: 10px;'>🔮 BARALHO CIGANO</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6C757D; margin-bottom: 30px;'>Método: Afrodite • 7 cartas para relacionamentos</p>", unsafe_allow_html=True)
    
    # Inicialização do estado
    if 'etapa' not in st.session_state:
        st.session_state.etapa = 'pergunta'
    if 'pergunta' not in st.session_state:
        st.session_state.pergunta = ""
    if 'cartas' not in st.session_state:
        st.session_state.cartas = []
    if 'resultado' not in st.session_state:
        st.session_state.resultado = None
    if 'carta_atual' not in st.session_state:
        st.session_state.c
