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
        
        /* Progresso das requisições */
        .progresso-requisicoes {
            background: #F8F9FA;
            border-radius: 12px;
            padding: 20px;
            margin: 20px 0;
            text-align: center;
            border: 1px solid #DEE2E6;
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
    
    <!-- JavaScript para IndexedDB -->
    <script>
        // Abrir banco de dados
        function abrirBD() {
            return new Promise((resolve, reject) => {
                const request = indexedDB.open('BaralhoCiganoDB', 1);
                
                request.onupgradeneeded = (event) => {
                    const db = event.target.result;
                    if (!db.objectStoreNames.contains('respostas')) {
                        db.createObjectStore('respostas', { keyPath: 'id' });
                    }
                };
                
                request.onsuccess = (event) => resolve(event.target.result);
                request.onerror = (event) => reject(event.target.error);
            });
        }
        
        // Salvar resposta
        window.salvarResposta = async (id, texto) => {
            try {
                const db = await abrirBD();
                const transaction = db.transaction(['respostas'], 'readwrite');
                const store = transaction.objectStore('respostas');
                
                return new Promise((resolve, reject) => {
                    const request = store.put({ id: id, texto: texto, timestamp: Date.now() });
                    request.onsuccess = () => resolve(true);
                    request.onerror = () => reject(false);
                });
            } catch (e) {
                console.error('Erro ao salvar:', e);
                return false;
            }
        };
        
        // Carregar resposta
        window.carregarResposta = async (id) => {
            try {
                const db = await abrirBD();
                const transaction = db.transaction(['respostas'], 'readonly');
                const store = transaction.objectStore('respostas');
                
                return new Promise((resolve, reject) => {
                    const request = store.get(id);
                    request.onsuccess = () => resolve(request.result ? request.result.texto : null);
                    request.onerror = () => reject(null);
                });
            } catch (e) {
                console.error('Erro ao carregar:', e);
                return null;
            }
        };
        
        // Limpar respostas antigas (mais de 1 dia)
        window.limparRespostasAntigas = async () => {
            try {
                const db = await abrirBD();
                const transaction = db.transaction(['respostas'], 'readwrite');
                const store = transaction.objectStore('respostas');
                const umDiaAtras = Date.now() - (24 * 60 * 60 * 1000);
                
                const request = store.openCursor();
                request.onsuccess = (event) => {
                    const cursor = event.target.result;
                    if (cursor) {
                        if (cursor.value.timestamp < umDiaAtras) {
                            cursor.delete();
                        }
                        cursor.continue();
                    }
                };
            } catch (e) {
                console.error('Erro ao limpar:', e);
            }
        };
        
        // Executar limpeza ao carregar
        window.limparRespostasAntigas();
    </script>
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
# FUNÇÕES PARA REQUISIÇÕES SEQUENCIAIS
# ============================================
def gerar_parte_1(cartas, pergunta_usuario, posicoes):
    """Gera a primeira parte: Introdução + Suas Cartas + O que se passa em você + O que se passa nela"""
    
    # Preparar dados das cartas
    cartas_descricao = []
    for i, carta_info in enumerate(cartas):
        carta = carta_info['carta']
        orientacao = carta_info['orientacao']
        cartas_descricao.append(
            f"{i+1}. {posicoes[i]}: {carta['nome']} ({orientacao})"
        )
    
    cartas_texto = "\n".join(cartas_descricao)
    
    prompt = f"""
Você é um mentor espiritual sábio e acolhedor, especialista em Baralho Cigano.

## CONTEXTO DA CONSULTA:
Pergunta do consulente: {pergunta_usuario if pergunta_usuario else "O que está acontecendo no meu relacionamento?"}

## AS CARTAS TIRADAS:
{cartas_texto}

## INSTRUÇÕES:
Escreva as seguintes seções da resposta, com EXTREMA PROFUNDIDADE e detalhamento:

### CARTA AO CONSULENTE
(Um parágrafo longo e acolhedor, contextualizando a dor e a jornada do consulente)

### O QUE SE PASSA NA SUA MENTE E NO SEU CORAÇÃO
(Interpretação DETALHADA das cartas 1, 2 e 3. Para CADA carta: 3-4 parágrafos com interpretação simbólica, significado comportamental, e sempre termine com "O que isso significa na prática:" e uma aplicação direta.)

### O QUE SE PASSA NA MENTE E NO CORAÇÃO DELA
(Interpretação DETALHADA das cartas 4, 5 e 6. Mesma estrutura acima, com 3-4 parágrafos por carta.)

Sua resposta deve ser LONGAMENTE DETALHADA, com pelo menos 1500 palavras.
"""
    
    modelo = genai.GenerativeModel('gemini-pro')
    response = modelo.generate_content(prompt)
    return response.text if response and response.text else ""

def gerar_parte_2(cartas, pergunta_usuario, posicoes):
    """Gera a segunda parte: Desfecho + Diálogo entre cartas + O que a ciência diz"""
    
    # Preparar dados das cartas
    cartas_descricao = []
    for i, carta_info in enumerate(cartas):
        carta = carta_info['carta']
        orientacao = carta_info['orientacao']
        cartas_descricao.append(
            f"{i+1}. {posicoes[i]}: {carta['nome']} ({orientacao})"
        )
    
    cartas_texto = "\n".join(cartas_descricao)
    
    prompt = f"""
Você é um mentor espiritual sábio e acolhedor, especialista em Baralho Cigano.

## CONTEXTO DA CONSULTA:
Pergunta do consulente: {pergunta_usuario if pergunta_usuario else "O que está acontecendo no meu relacionamento?"}

## AS CARTAS TIRADAS:
{cartas_texto}

## INSTRUÇÕES:
Escreva as seguintes seções da resposta, com EXTREMA PROFUNDIDADE e detalhamento:

### PARA ONDE TUDO ISSO ESTÁ LEVANDO
(Interpretação da carta 7 - o desfecho. Pelo menos 4 parágrafos, mostrando tendências e possibilidades. Inclua "O que isso significa na prática:")

### O DIÁLOGO SILENCIOSO ENTRE AS CARTAS
(Análise profunda das interações entre as cartas. Mínimo de 6 parágrafos. Mostre: o que está em sincronia, o que está em desencontro, o que cada um está projetando no outro, como as energias se complementam ou se chocam.)

### O QUE A CIÊNCIA DIZ SOBRE O QUE VOCÊ ESTÁ VIVENDO
(6-8 fatos científicos diretos sobre relacionamentos, neurociência do amor, estresse, desejo, comunicação. Cada fato com um parágrafo explicativo e aplicado à situação.)

Sua resposta deve ser LONGAMENTE DETALHADA, com pelo menos 1500 palavras.
"""
    
    modelo = genai.GenerativeModel('gemini-pro')
    response = modelo.generate_content(prompt)
    return response.text if response and response.text else ""

def gerar_parte_3(cartas, pergunta_usuario, posicoes):
    """Gera a terceira parte: Filosofia + Ilusões + Ações + Palavras Finais"""
    
    # Preparar dados das cartas
    cartas_descricao = []
    for i, carta_info in enumerate(cartas):
        carta = carta_info['carta']
        orientacao = carta_info['orientacao']
        cartas_descricao.append(
            f"{i+1}. {posicoes[i]}: {carta['nome']} ({orientacao})"
        )
    
    cartas_texto = "\n".join(cartas_descricao)
    
    prompt = f"""
Você é um mentor espiritual sábio e acolhedor, especialista em Baralho Cigano.

## CONTEXTO DA CONSULTA:
Pergunta do consulente: {pergunta_usuario if pergunta_usuario else "O que está acontecendo no meu relacionamento?"}

## AS CARTAS TIRADAS:
{cartas_texto}

## INSTRUÇÕES:
Escreva as seguintes seções da resposta, com EXTREMA PROFUNDIDADE e detalhamento:

### O QUE A FILOSOFIA ENSINA SOBRE O SEU MOMENTO
(5 escolas filosóficas: Estoicismo, Budismo, Sikhismo, Existencialismo, Taoísmo. Para CADA uma: um parágrafo longo explicando o princípio e aplicando diretamente à situação do consulente.)

### AS ILUSÕES QUE VOCÊ PODE ESTAR ALIMENTANDO
(6-8 ilusões comuns em relacionamentos. Para CADA: "**Ilusão:** [frase entre aspas]" seguido de 2-3 parágrafos desmontando a ilusão com exemplos práticos.)

### O QUE VOCÊ PODE FAZER AGORA – AÇÕES CONCRETAS
(10-12 ações práticas, numeradas. Para CADA: um parágrafo explicativo detalhado sobre como implementar, exemplos do dia a dia, o que esperar.)

### PALAVRAS FINAIS
(Um encerramento poético e empoderador de 5-6 parágrafos, retomando as cartas, oferecendo esperança, e lembrando que a escolha é do consulente. Incluir uma "Nota para o consulente" no final.)

Sua resposta deve ser LONGAMENTE DETALHADA, com pelo menos 1800 palavras.
"""
    
    modelo = genai.GenerativeModel('gemini-pro')
    response = modelo.generate_content(prompt)
    return response.text if response and response.text else ""

def salvar_no_indexeddb(chave, valor):
    """Salva dados no IndexedDB via JavaScript"""
    js_code = f"""
    <script>
        (async function() {{
            await window.salvarResposta('{chave}', {json.dumps(valor)});
        }})();
    </script>
    """
    st.components.v1.html(js_code, height=0)

def carregar_do_indexeddb(chave):
    """Carrega dados do IndexedDB via JavaScript (requer rerun)"""
    js_code = f"""
    <script>
        (async function() {{
            const valor = await window.carregarResposta('{chave}');
            if (valor) {{
                // Enviar para o Streamlit via sessionStorage
                sessionStorage.setItem('{chave}', valor);
                window.location.reload();
            }}
        }})();
    </script>
    """
    st.components.v1.html(js_code, height=0)
    
    # Tentar recuperar do sessionStorage
    valor = st.session_state.get(f"_storage_{chave}")
    if valor:
        return valor
    
    # Tentar via JavaScript
    valor_js = st.session_state.get(f"_js_{chave}")
    if valor_js:
        return valor_js
    
    return None

# ============================================
# FUNÇÃO PARA DIVIDIR RESPOSTA EM SEÇÕES
# ============================================
def dividir_resposta_em_secoes(texto_completo):
    """
    Divide a resposta completa em seções baseadas nos títulos ###
    """
    if not texto_completo:
        return []
    
    # Padrão para encontrar títulos ###
    padrao = r'### (.+?)(?=### |\Z)'
    matches = re.findall(padrao, texto_completo, re.DOTALL)
    
    if not matches:
        # Tentar com ## se não encontrar ###
        padrao = r'## (.+?)(?=## |\Z)'
        matches = re.findall(padrao, texto_completo, re.DOTALL)
    
    if not matches:
        # Se não encontrar seções, retorna o texto inteiro como uma única seção
        return [{"titulo": "Leitura Completa", "conteudo": texto_completo}]
    
    secoes = []
    for match in matches:
        linhas = match.strip().split('\n', 1)
        titulo = linhas[0].replace('##', '').replace('###', '').strip()
        conteudo = linhas[1] if len(linhas) > 1 else ""
        secoes.append({"titulo": titulo, "conteudo": conteudo})
    
    return secoes

# ============================================
# INTERFACE - MÉTODO AFRODITE COM 3 REQUISIÇÕES
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
    if 'partes' not in st.session_state:
        st.session_state.partes = {}
    if 'secoes' not in st.session_state:
        st.session_state.secoes = []
    if 'pagina_atual' not in st.session_state:
        st.session_state.pagina_atual = 0
    if 'carta_atual' not in st.session_state:
        st.session_state.carta_atual = 1
    if 'requisicao_atual' not in st.session_state:
        st.session_state.requisicao_atual = 0
    
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
        elif st.session_state.etapa.startswith('carta') and st.session_state.etapa != 'carta_completa':
            carta_num = int(st.session_state.etapa.replace('carta', ''))
            
            # Posições das cartas
            posicoes_interface = [
                "1ª carta — Pensamentos e Intenções (você)",
                "2ª carta — Sentimentos (você)",
                "3ª carta — Desejo sexual (você)",
                "4ª carta — Pensamentos e Intenções (ela)",
                "5ª carta — Sentimentos (ela)",
                "6ª carta — Desejo sexual (ela)",
                "7ª carta — O desfecho"
            ]
            
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
                                        'posicao': posicoes_interface[carta_num-1],
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
                    if st.button("Finalizar", use_container_width=True, type="primary"):
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
                                    'posicao': posicoes_interface[6],
                                    'posicao_num': 7
                                })
                                
                                # Ordenar por posição
                                st.session_state.cartas.sort(key=lambda x: x['posicao_num'])
                                
                                st.session_state.etapa = 'gerando'
                                st.session_state.requisicao_atual = 0
                                st.session_state.partes = {}
                                st.rerun()
                            else:
                                st.error("Carta não encontrada")
                        else:
                            st.warning("Digite o nome da carta")
        
        # ETAPA DE GERAÇÃO COM 3 REQUISIÇÕES
        elif st.session_state.etapa == 'gerando':
            
            # Mostrar progresso
            with st.container():
                st.markdown("<div class='progresso-requisicoes'>", unsafe_allow_html=True)
                st.markdown("### 🔮 Conectando com as energias...")
                
                # Barra de progresso visual
                if st.session_state.requisicao_atual == 0:
                    st.markdown("**⏳ Preparando primeira parte da leitura...**")
                    st.progress(0.33)
                elif st.session_state.requisicao_atual == 1:
                    st.markdown("**⏳ Aprofundando a interpretação...**")
                    st.progress(0.66)
                elif st.session_state.requisicao_atual == 2:
                    st.markdown("**⏳ Finalizando com sabedoria e ações práticas...**")
                    st.progress(0.99)
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Executar requisições sequenciais
            if st.session_state.requisicao_atual == 0 and 'parte1' not in st.session_state.partes:
                with st.spinner("Parte 1 de 3: Analisando sentimentos..."):
                    parte1 = gerar_parte_1(st.session_state.cartas, st.session_state.pergunta, posicoes)
                    st.session_state.partes['parte1'] = parte1
                    st.session_state.requisicao_atual = 1
                    time.sleep(1)  # Pausa para não sobrecarregar a API
                    st.rerun()
            
            elif st.session_state.requisicao_atual == 1 and 'parte2' not in st.session_state.partes:
                with st.spinner("Parte 2 de 3: Explorando desfecho e ciência..."):
                    parte2 = gerar_parte_2(st.session_state.cartas, st.session_state.pergunta, posicoes)
                    st.session_state.partes['parte2'] = parte2
                    st.session_state.requisicao_atual = 2
                    time.sleep(1)
                    st.rerun()
            
            elif st.session_state.requisicao_atual == 2 and 'parte3' not in st.session_state.partes:
                with st.spinner("Parte 3 de 3: Ações práticas e sabedoria final..."):
                    parte3 = gerar_parte_3(st.session_state.cartas, st.session_state.pergunta, posicoes)
                    st.session_state.partes['parte3'] = parte3
                    
                    # Combinar todas as partes
                    resposta_completa = f"""
# 🔮 O LIVRO DA SUA RELAÇÃO

{st.session_state.partes['parte1']}

{st.session_state.partes['parte2']}

{st.session_state.partes['parte3']}
"""
                    
                    # Dividir em seções
                    st.session_state.secoes = dividir_resposta_em_secoes(resposta_completa)
                    
                    # Salvar no IndexedDB
                    try:
                        salvar_no_indexeddb('resposta_completa', resposta_completa)
                    except:
                        pass
                    
                    st.session_state.etapa = 'resultado'
                    st.session_state.pagina_atual = 0
                    st.rerun()
        
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
                        for key in ['etapa', 'pergunta', 'cartas', 'partes', 'secoes', 'pagina_atual', 'carta_atual', 'requisicao_atual']:
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
