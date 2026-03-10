import streamlit as st
import google.generativeai as genai
from datetime import datetime
import json
import re

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
# CSS - COM ESTILO PARA PAGINAÇÃO
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
            margin-top: 0;
            margin-bottom: 20px;
            text-align: left;
            border-bottom: 2px solid #000000;
            padding-bottom: 10px;
        }
        
        .resultado h2 {
            font-size: 24px;
            font-weight: 600;
            color: #000000;
            margin-top: 0;
            margin-bottom: 20px;
        }
        
        .resultado h3 {
            font-size: 20px;
            font-weight: 600;
            color: #000000;
            margin-top: 0;
            margin-bottom: 10px;
        }
        
        .resultado p {
            margin-bottom: 20px;
        }
        
        /* Paginação */
        .pagination-info {
            text-align: center;
            color: #6C757D;
            font-size: 14px;
            margin: 20px 0;
            padding: 10px;
            border-top: 1px solid #DEE2E6;
            border-bottom: 1px solid #DEE2E6;
        }
        
        /* Botões de navegação */
        .nav-buttons {
            display: flex;
            justify-content: space-between;
            margin: 20px 0;
        }
        
        /* Título principal */
        h1 {
            display: block !important;
            color: #000000 !important;
            font-weight: 700 !important;
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
# FUNÇÃO PARA DIVIDIR RESPOSTA EM SEÇÕES
# ============================================
def dividir_resposta_em_secoes(texto_completo):
    """
    Divide a resposta completa em seções baseadas nos títulos ##
    """
    if not texto_completo:
        return []
    
    # Padrão para encontrar títulos ##
    padrao = r'(## .+?)(?=## |\Z)'
    matches = re.findall(padrao, texto_completo, re.DOTALL)
    
    if not matches:
        # Se não encontrar seções, retorna o texto inteiro como uma única seção
        return [{"titulo": "Leitura Completa", "conteudo": texto_completo}]
    
    secoes = []
    for match in matches:
        linhas = match.strip().split('\n', 1)
        titulo = linhas[0].replace('##', '').strip()
        conteudo = linhas[1] if len(linhas) > 1 else ""
        secoes.append({"titulo": titulo, "conteudo": conteudo})
    
    return secoes

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
        cartas_completo = []
        for i, carta_info in enumerate(cartas):
            carta = carta_info['carta']
            orientacao = carta_info['orientacao']
            
            cartas_completo.append({
                'posicao': i+1,
                'nome': carta['nome'],
                'orientacao': orientacao,
                'significado': carta['significado_invertido'] if orientacao == 'invertida' else carta['significado_normal']
            })
        
        # Criar descrição detalhada para o prompt
        cartas_descricao = []
        for c in cartas_completo:
            cartas_descricao.append(
                f"{c['posicao']}. {posicoes[c['posicao']-1]}: {c['nome']} ({c['orientacao']})"
            )
        
        cartas_texto = "\n".join(cartas_descricao)
        
        # Prompt com o estilo EXATO da resposta aprovada
        prompt = f"""
Você é um mentor espiritual sábio e acolhedor, especialista em Baralho Cigano. Sua missão é oferecer um conselho profundo, humanizado e prático para o consulente, baseado na tiragem de Afrodite (7 cartas para análise de relacionamento).

## CONTEXTO DA CONSULTA:
Pergunta do consulente: {pergunta_usuario if pergunta_usuario else "O que está acontecendo no meu relacionamento?"}

## AS CARTAS TIRADAS:
{cartas_texto}

## INSTRUÇÕES CRÍTICAS - SIGA EXATAMENTE ESTE ESTILO:

Escreva uma resposta com a seguinte estrutura e tom. Use a resposta abaixo como REFERÊNCIA DE ESTILO - deve ser igual em profundidade, tom acolhedor e estrutura.

### ESTRUTURA OBRIGATÓRIA:

## CARTA AO CONSULENTE
(Um parágrafo acolhedor que contextualiza a dor/pergunta do consulente, validando sua jornada.)

## O QUE SE PASSA NA SUA MENTE E NO SEU CORAÇÃO
(Interpretação das cartas 1, 2 e 3. Para CADA carta: **Carta X – [Nome]**: [2-3 parágrafos interpretando a carta, sempre terminando com "O que isso significa na prática:" e uma frase direta.])

## O QUE SE PASSA NA MENTE E NO CORAÇÃO DELA
(Interpretação das cartas 4, 5 e 6 - mesma estrutura acima.)

## PARA ONDE TUDO ISSO ESTÁ LEVANDO
(Interpretação da carta 7, com "O que isso significa na prática:")

## O DIÁLOGO SILENCIOSO ENTRE AS CARTAS
(Análise das interações entre as cartas, com frases como "Seu Coração (amor) encontra as Estrelas dela (esperança)." Mostre o que está em sincronia e o que está em desencontro. Pelo menos 4 parágrafos.)

## O QUE A CIÊNCIA DIZ SOBRE O QUE VOCÊ ESTÁ VIVENDO
(4-5 fatos científicos diretos, cada um com um parágrafo curto. Use "Sobre [tema]:" para introduzir cada um.)

## O QUE A FILOSOFIA ENSINA SOBRE O SEU MOMENTO
(Estoicismo, Budismo, Sikhismo, Existencialismo - um parágrafo para cada escola, aplicado diretamente à situação do consulente. Use o nome da escola como subtítulo.)

## AS ILUSÕES QUE VOCÊ PODE ESTAR ALIMENTANDO
(4-5 ilusões comuns, cada uma com o formato: "**Ilusão [número]:** [Frase entre aspas]" seguido de um parágrafo curto desmontando a ilusão.)

## O QUE VOCÊ PODE FAZER AGORA – AÇÕES CONCRETAS
(8-10 ações práticas, numeradas, cada uma com um parágrafo explicativo. As ações devem ser específicas e imediatas.)

## PALAVRAS FINAIS
(Um encerramento poético e empoderador de 3-4 parágrafos, retomando as cartas e oferecendo esperança e direção. Incluir "Nota para o consulente" no final.)

### DIRETRIZES DE TOM:

- Use linguagem profundamente humana e acolhedora.
- As interpretações devem ser ricas, com pelo menos 3-4 frases por carta.
- Conecte TUDO à pergunta e situação específica do consulente.
- Seja direto, mas nunca cruel.
- Use frases como "O que isso significa na prática:" para trazer a interpretação para o terreno da vida real.
- O texto deve ter QUALIDADE DE LIVRO - pode ser transformado em PDF.
- NÃO seja acadêmico demais - a ciência e filosofia devem ser pontuais e aplicadas.
- Termine sempre com uma mensagem de empoderamento.
- **A resposta deve ser LONGAMENTE DETALHADA, com pelo menos 4000 palavras. Não economize na profundidade.**

Agora, escreva a resposta completa seguindo exatamente esta estrutura e tom.
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
## CARTA AO CONSULENTE

Prezado, a pergunta que você traz é sobre amor, sobre conexão, sobre o que ainda existe entre duas pessoas que um dia se escolheram. Não estamos diante de uma simples briga de casal – estamos diante de um relacionamento que adoeceu e precisa de diagnóstico antes do tratamento. Nas próximas páginas, você encontrará não apenas o significado das cartas, mas um mapa para entender o que realmente está acontecendo – e o que você pode fazer a respeito.

Leia com calma. Algumas verdades vão doer. Mas a dor que cura é diferente da dor que paralisa.

## O QUE SE PASSA NA SUA MENTE E NO SEU CORAÇÃO

**Carta 1 – {nomes[0]}: Seus pensamentos e intenções**
Esta carta revela o estado da sua mente neste momento. Seus pensamentos estão acelerados ou tranquilos? Direcionados para ação ou para reflexão? Observe o que esta carta diz sobre como você está processando a situação.

**Carta 2 – {nomes[1]}: Seus sentimentos por ela**
Aqui está a verdade do seu coração. O que você realmente sente por ela, para além das mágoas e dos desgastes. Esse sentimento é a base sobre a qual qualquer reconstrução pode acontecer.

**Carta 3 – {nomes[2]}: Seu desejo sexual por ela**
O desejo fala de atração, de libido, de vontade de se aproximar fisicamente. Esta carta mostra se esse canal ainda está aberto ou se ele foi fechado pela rotina e pelos conflitos.

## O QUE SE PASSA NA MENTE E NO CORAÇÃO DELA

**Carta 4 – {nomes[3]}: Pensamentos e intenções dela**
A mente dela pode estar clara ou confusa, aberta ou defensiva. Esta carta revela como ela está processando a relação internamente.

**Carta 5 – {nomes[4]}: Sentimentos dela por você**
Apesar das aparências, o que ela realmente sente? Esta carta mostra se o amor ainda existe ou se já foi substituído por indiferença ou ressentimento.

**Carta 6 – {nomes[5]}: Desejo sexual dela por você**
O desejo feminino é complexo e muitas vezes reativo à segurança emocional. Esta carta indica se ela ainda sente atração ou se esse canal foi temporariamente interrompido.

## PARA ONDE TUDO ISSO ESTÁ LEVANDO

**Carta 7 – {nomes[6]}: O desfecho**
Esta carta não é uma sentença, mas uma tendência. Mostra para onde a relação está caminhando SE nada mudar. É um aviso, não um destino.

## O DIÁLOGO SILENCIOSO ENTRE AS CARTAS

Observe a dança entre o que você sente e o que ela sente, entre o que você deseja e o que ela deseja. Existe sincronia ou assincronia? Vocês estão no mesmo comprimento de onda ou em frequências opostas?

## O QUE A CIÊNCIA DIZ SOBRE O QUE VOCÊ ESTÁ VIVENDO

- **Sobre o estresse crônico**: Casais em conflito constante têm níveis elevados de cortisol, o que afeta a comunicação e o desejo.
- **Sobre o desejo feminino**: Estudos mostram que a atração sexual na mulher está diretamente ligada à sensação de segurança emocional.
- **Sobre a comunicação**: O cérebro processa críticas como ameaça física, ativando as mesmas áreas de defesa.
- **Sobre a esperança**: A expectativa de melhora ativa os mesmos circuitos de recompensa que a melhora real.

## O QUE A FILOSOFIA ENSINA SOBRE O SEU MOMENTO

**Estoicismo**: Foque no que depende de você – suas ações, suas escolhas, sua forma de reagir. O resto, inclusive os sentimentos dela, não está sob seu controle.

**Budismo**: Tudo é impermanente. Esta crise vai passar. A questão é o que restará depois. O apego a como as coisas "deveriam ser" é a raiz do sofrimento.

**Sikhismo**: Aja com excelência, mas sem se apegar ao resultado. Você pode dar o melhor de si para reconstruir a relação, mas sem se prender ao resultado.

**Existencialismo**: Você é livre para escolher. As cartas mostram tendências, não destinos. A responsabilidade pela decisão é sua.

## AS ILUSÕES QUE VOCÊ PODE ESTAR ALIMENTANDO

1. **"Se eu explicar direito, ela vai entender."** Não, não vai. Quando alguém está na defensiva, explicações soam como justificativas, não como diálogo.

2. **"Se ela me amasse, me desejaria."** Não é assim que funciona. Amor e desejo são circuitos diferentes no cérebro.

3. **"Preciso resolver isso rápido."** Não, não precisa. Relações desgastadas por anos não se curam em dias.

4. **"O problema é só [circunstância externa]."** As circunstâncias agravam, mas raramente são a causa raiz.

## O QUE VOCÊ PODE FAZER AGORA – AÇÕES CONCRETAS

1. **Desacelere**: Estabeleça um período de 30 dias sem conversas pesadas sobre a relação. Apenas observe, acolha, esteja presente.

2. **Crie segurança**: Consistência, previsibilidade e escuta ativa. Segurança se cria com ações, não com palavras.

3. **Mude a forma de se comunicar**: Use a estrutura "Quando você... eu sinto... porque preciso... você topa...?"

4. **Crie rituais mínimos de conexão**: 10 minutos por dia lado a lado, sem obrigação de conversar.

5. **Respeite o tempo dela, mas também o seu**: Observe se ela está se movendo em sua direção. Se depois de 60 dias não houver mudança, você terá sua resposta.

6. **Cuide de você primeiro**: Sua energia e autoestima afetam diretamente a relação. Busque fontes de renda, atividades que te fortaleçam, rede de apoio.

7. **Estabeleça um marco**: 60 dias para reavaliar se houve mudança.

## PALAVRAS FINAIS

O livro que você acabou de ler não é um oráculo – é um espelho. As cartas não criaram sua realidade, apenas a revelaram.

Você ainda sente. Ela ainda tem esperança. Isso é mais do que muitos casais têm quando chegam onde vocês chegaram.

Mas amor sem ação é só sentimento. Esperança sem mudança é só ilusão.

A Âncora no final não é uma sentença – é uma escolha. Você pode continuar parado, imóvel, pesado. Ou pode usar o peso dela para se estabilizar enquanto decide para onde navegar.

O que você escolher será certo. Não porque as cartas disseram, mas porque **você** escolheu.

Com respeito pela sua história e pela coragem de buscar respostas,

*Seu mentor.*

📌 **Nota para o consulente:** Este texto é seu. Guarde, releia, compartilhe com quem precisa. As respostas que você busca já estão dentro de você – as cartas só ajudaram a organizá-las.
"""
    return conselho

# ============================================
# INTERFACE - MÉTODO AFRODITE COM PAGINAÇÃO
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
    if 'resultado_completo' not in st.session_state:
        st.session_state.resultado_completo = None
    if 'secoes' not in st.session_state:
        st.session_state.secoes = []
    if 'pagina_atual' not in st.session_state:
        st.session_state.pagina_atual = 0
    if 'carta_atual' not in st.session_state:
        st.session_state.carta_atual = 1
    
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
        elif st.session_state.etapa.startswith('carta'):
            carta_num = int(st.session_state.etapa.replace('carta', ''))
            
            # Posições das cartas
            posicoes = [
                "1ª carta — Pensamentos e Intenções (você)",
                "2ª carta — Sentimentos (você)",
                "3ª carta — Desejo sexual (você)",
                "4ª carta — Pensamentos e Intenções (ela)",
                "5ª carta — Sentimentos (ela)",
                "6ª carta — Desejo sexual (ela)",
                "7ª carta — O desfecho"
            ]
            
            st.markdown(f"**{posicoes[carta_num-1]}**")
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
                                # Verificar se já existe carta nesta posição
                                carta_existente = False
                                for c in st.session_state.cartas:
                                    if c.get('posicao_num') == carta_num:
                                        carta_existente = True
                                        break
                                
                                if not carta_existente:
                                    # Remover carta antiga se existir
                                    st.session_state.cartas = [c for c in st.session_state.cartas if c.get('posicao_num') != carta_num]
                                    
                                    # Adicionar nova carta
                                    st.session_state.cartas.append({
                                        'carta': carta,
                                        'id': id_carta,
                                        'orientacao': 'normal',
                                        'posicao': posicoes[carta_num-1],
                                        'posicao_num': carta_num
                                    })
                                    
                                    # Ordenar por posição
                                    st.session_state.cartas.sort(key=lambda x: x['posicao_num'])
                                    
                                    st.session_state.etapa = f'carta{carta_num+1}'
                                    st.rerun()
                                else:
                                    st.warning("Esta carta já foi adicionada")
                            else:
                                st.error("Carta não encontrada")
                        else:
                            st.warning("Digite o nome da carta")
                
                else:  # Última carta (7)
                    if st.button("Finalizar e interpretar", use_container_width=True, type="primary"):
                        if carta_input:
                            valida, id_carta, carta = validar_carta(carta_input)
                            if valida:
                                # Remover carta antiga se existir
                                st.session_state.cartas = [c for c in st.session_state.cartas if c.get('posicao_num') != 7]
                                
                                # Adicionar última carta
                                st.session_state.cartas.append({
                                    'carta': carta,
                                    'id': id_carta,
                                    'orientacao': 'normal',
                                    'posicao': posicoes[6],
                                    'posicao_num': 7
                                })
                                
                                # Ordenar por posição
                                st.session_state.cartas.sort(key=lambda x: x['posicao_num'])
                                
                                with st.spinner("🔮 Interpretando sua história..."):
                                    resultado = interpretar_tiragem_afrodite(
                                        st.session_state.cartas,
                                        st.session_state.pergunta
                                    )
                                    
                                    # Armazenar resultado completo e dividir em seções
                                    st.session_state.resultado_completo = resultado
                                    st.session_state.secoes = dividir_resposta_em_secoes(resultado)
                                    st.session_state.pagina_atual = 0
                                    st.session_state.etapa = 'resultado'
                                    st.rerun()
                            else:
                                st.error("Carta não encontrada")
                        else:
                            st.warning("Digite o nome da carta")
        
        # ETAPA 9: RESULTADO COM PAGINAÇÃO
        elif st.session_state.etapa == 'resultado':
            if st.session_state.secoes:
                secao_atual = st.session_state.secoes[st.session_state.pagina_atual]
                
                # Mostrar título da seção
                st.markdown(f"<h2 style='text-align: center;'>{secao_atual['titulo']}</h2>", unsafe_allow_html=True)
                
                # Mostrar conteúdo da seção
                st.markdown(f'<div class="resultado">{secao_atual["conteudo"]}</div>', unsafe_allow_html=True)
                
                # Informação de paginação
                st.markdown(f"""
                <div class="pagination-info">
                    Seção {st.session_state.pagina_atual + 1} de {len(st.session_state.secoes)}
                </div>
                """, unsafe_allow_html=True)
                
                # Botões de navegação
                col1, col2, col3 = st.columns([1, 1, 1])
                
                with col1:
                    if st.session_state.pagina_atual > 0:
                        if st.button("← Anterior", use_container_width=True):
                            st.session_state.pagina_atual -= 1
                            st.rerun()
                
                with col2:
                    if st.button("Nova consulta", use_container_width=True):
                        for key in ['etapa', 'pergunta', 'cartas', 'resultado_completo', 'secoes', 'pagina_atual', 'carta_atual']:
                            if key in st.session_state:
                                del st.session_state[key]
                        st.rerun()
                
                with col3:
                    if st.session_state.pagina_atual < len(st.session_state.secoes) - 1:
                        if st.button("Próximo →", use_container_width=True):
                            st.session_state.pagina_atual += 1
                            st.rerun()
            else:
                st.markdown('<div class="resultado">Carregando interpretação...</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
