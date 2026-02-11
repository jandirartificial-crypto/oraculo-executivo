import streamlit as st
import google.generativeai as genai
import random
from datetime import datetime
import time

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
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)

# ============================================
# CSS PERSONALIZADO PARA ESTABILIDADE
# ============================================
st.markdown("""
    <style>
        /* Reset e estabilização */
        .stApp {
            background: linear-gradient(135deg, #1a1e24 0%, #2d3439 100%);
        }
        
        /* Cards das cartas - design profissional */
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
            min-height: 280px;
        }
        
        .carta-card:hover {
            transform: translateY(-5px);
            border-color: #9f7aea;
            box-shadow: 0 15px 30px rgba(159, 122, 234, 0.2);
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
        
        .carta-palavras {
            font-size: 12px;
            color: #b0b0b0;
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid rgba(255,255,255,0.1);
        }
        
        .carta-orientacao {
            margin-top: 8px;
            font-size: 11px;
            color: #90a4ae;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        
        /* Estilo para interpretação */
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
        
        /* Botões personalizados */
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
# TIRAGENS PRÉ-DEFINIDAS
# ============================================
TIPOS_TIRAGEM = {
    "3 Cartas (Passado, Presente, Futuro)": {
        "descricao": "Visão geral da jornada do consulente",
        "num_cartas": 3,
        "posicoes": ["Passado", "Presente", "Futuro"]
    },
    "5 Cartas (Cruz Cigana)": {
        "descricao": "Análise completa: situação, obstáculo, conselho, resultado, síntese",
        "num_cartas": 5,
        "posicoes": ["Situação Atual", "Obstáculo", "Conselho", "Resultado", "Síntese"]
    },
    "7 Cartas (Estrela)": {
        "descricao": "Tiragem espiritual: corpo, mente, espírito, emoções, trabalho, amor, dinheiro",
        "num_cartas": 7,
        "posicoes": ["Corpo/Saúde", "Mente/Emoções", "Espírito", "Amor", "Trabalho", "Dinheiro", "Família"]
    }
}

# ============================================
# FUNÇÃO PARA EXIBIR CARTAS SEM IMAGENS
# ============================================
def criar_card_carta(carta):
    """Cria um card HTML para exibir a carta sem usar imagens"""
    
    # Determinar classe CSS baseada na orientação
    classe_carta = "carta-card"
    if carta['orientacao'] == 'invertida':
        classe_carta += " carta-invertida"
    
    # Símbolo de orientação
    simbolo_orientacao = " 🔄" if carta['orientacao'] == 'invertida' else ""
    
    # Significado resumido para exibição
    significado = carta['significado_invertido'] if carta['orientacao'] == 'invertida' else carta['significado_normal']
    significado_resumo = significado[:80] + "..." if len(significado) > 80 else significado
    
    html_card = f"""
    <div class="{classe_carta}">
        <div class="carta-simbolo">{carta['simbolo']}</div>
        <div class="carta-nome">{carta['nome']}{simbolo_orientacao}</div>
        <div class="carta-posicao">📍 {carta['posicao']}</div>
        <div style="font-size: 13px; color: #d0d0d0; padding: 0 10px;">
            {significado_resumo}
        </div>
        <div class="carta-palavras">{carta['palavras_chave']}</div>
        <div class="carta-orientacao">{carta['orientacao'].upper()}</div>
    </div>
    """
    return html_card

def sortear_cartas(tipo_tiragem):
    """
    Sorteia as cartas de acordo com o tipo de tiragem
    """
    config = TIPOS_TIRAGEM[tipo_tiragem]
    indices_sorteados = random.sample(list(BARALHO_CIGANO.keys()), config["num_cartas"])
    
    cartas_selecionadas = []
    for i, idx in enumerate(indices_sorteados):
        orientacao = random.choice(["normal", "invertida"])
        carta = BARALHO_CIGANO[idx].copy()
        carta["id"] = idx
        carta["orientacao"] = orientacao
        carta["posicao"] = config["posicoes"][i]
        cartas_selecionadas.append(carta)
    
    return cartas_selecionadas

# ============================================
# FUNÇÃO PRINCIPAL DO GEMINI
# ============================================
def interpretar_tiragem(cartas, pergunta_usuario, historico=""):
    """
    Envia a tiragem para o Gemini e retorna a interpretação
    """
    modelo = genai.GenerativeModel('models/gemini-1.5-flash')
    
    # Construir o prompt detalhado
    prompt = f"""
VOCÊ É UMA ESPECIALISTA EM BARALHO CIGANO (LENORMAND) COM MAIS DE 30 ANOS DE EXPERIÊNCIA.

## SOBRE O CONSULENTE:
Pergunta/Intenção: {pergunta_usuario if pergunta_usuario else "Consulta geral - sem pergunta específica"}

## CARTAS SORTEADAS:
"""
    
    for carta in cartas:
        significado = carta['significado_invertido'] if carta['orientacao'] == 'invertida' else carta['significado_normal']
        prompt += f"""
📍 {carta['posicao']}
Carta: {carta['nome']} {carta['simbolo']}
Orientação: {carta['orientacao'].upper()}
Significado Base: {significado}
Palavras-chave: {carta['palavras_chave']}
"""

    prompt += f"""
## REGRAS DE OURO PARA INTERPRETAÇÃO:
1️⃣ FALE COM EMPATIA - Use linguagem acolhedora e jamais assuste o consulente
2️⃣ SEJA ESPECÍFICA - Relacione as cartas entre si, não interprete isoladamente
3️⃣ SEMPRE FOQUE NO POSITIVO - Mesmo cartas "difíceis" tem lições
4️⃣ NÃO USE TERMOS TÉCNICOS - Explique como se estivesse sentada à mesa com o consulente
5️⃣ RESPEITE O BARALHO CIGANO - Use a simbologia tradicional Lenormand, não confunda com Tarot

## INSTRUÇÃO ESPECÍFICA:
Faça uma leitura FLUIDA e NATURAL. Não liste as cartas uma por uma como se fosse um dicionário. Conte uma história que conecte as posições e os significados.

## HISTÓRICO DA CONVERSA (para manter contexto):
{historico if historico else "Primeira consulta do cliente."}

## SUA INTERPRETAÇÃO (mínimo 10 linhas):
"""
    
    # Gerar resposta
    response = modelo.generate_content(prompt)
    return response.text

# ============================================
# INTERFACE PRINCIPAL STREAMLIT
# ============================================
def main():
    st.title("🔮 Baralho Cigano Online")
    st.markdown("---")
    
    # Inicializar session state
    if 'cartas_sorteadas' not in st.session_state:
        st.session_state.cartas_sorteadas = None
    if 'interpretacao' not in st.session_state:
        st.session_state.interpretacao = None
    if 'historico' not in st.session_state:
        st.session_state.historico = []
    
    # Sidebar - Configurações
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        # Escolha do tipo de tiragem
        tipo_tiragem = st.selectbox(
            "Escolha o tipo de tiragem:",
            list(TIPOS_TIRAGEM.keys()),
            key="tipo_tiragem_selector"
        )
        
        st.markdown("---")
        st.subheader("📊 Sobre as cartas")
        st.info(f"Total: 36 lâminas do Baralho Cigano tradicional")
        
        # Botão de nova consulta
        if st.button("🔄 Nova Consulta", key="nova_consulta"):
            for key in ['cartas_sorteadas', 'interpretacao', 'pergunta_atual']:
                if key in st.session_state:
                    st.session_state[key] = None
            st.session_state.historico = []
            st.rerun()
    
    # Área principal
    col1, col2 = st.columns([2, 1])
    
    with col1:
        pergunta = st.text_area(
            "💭 Qual sua pergunta ou intenção para esta consulta?",
            placeholder="Ex: Como está minha vida amorosa? O que vem pela frente no trabalho?",
            height=100,
            key="pergunta_input"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🃏 **TIRAR CARTAS**", use_container_width=True, type="primary", key="tirar_cartas"):
            with st.spinner("🎴 Embaralhando e cortando o baralho..."):
                time.sleep(0.5)  # Pequena pausa para feedback visual
                st.session_state.cartas_sorteadas = sortear_cartas(tipo_tiragem)
                st.session_state.interpretacao = None
                st.session_state.pergunta_atual = pergunta
                st.rerun()
    
    # Exibir cartas sorteadas
    if st.session_state.cartas_sorteadas:
        st.markdown("---")
        st.subheader("🃏 Suas Cartas")
        
        # Layout em grid para as cartas
        cols = st.columns(len(st.session_state.cartas_sorteadas))
        
        for idx, (col, carta) in enumerate(zip(cols, st.session_state.cartas_sorteadas)):
            with col:
                # Usar card HTML em vez de imagem
                html_card = criar_card_carta(carta)
                st.markdown(html_card, unsafe_allow_html=True)
        
        # Botão para interpretação
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("🔮 **INTERPRETAR CARTAS**", use_container_width=True, key="interpretar"):
                with st.spinner("🔮 Consultando os mistérios do Baralho Cigano..."):
                    # Construir histórico
                    historico_texto = ""
                    if st.session_state.historico:
                        historico_texto = "\n".join(st.session_state.historico[-3:])
                    
                    # Interpretar
                    interpretacao = interpretar_tiragem(
                        st.session_state.cartas_sorteadas,
                        st.session_state.get('pergunta_atual', ''),
                        historico_texto
                    )
                    
                    st.session_state.interpretacao = interpretacao
                    
                    # Salvar no histórico
                    resumo = f"Tiragem {datetime.now().strftime('%d/%m/%y %H:%M')}: {[c['nome'] for c in st.session_state.cartas_sorteadas]}"
                    st.session_state.historico.append(resumo)
                    st.rerun()
    
    # Exibir interpretação
    if st.session_state.interpretacao:
        st.markdown("---")
        st.subheader("🔮 Mensagem do Baralho Cigano")
        
        with st.container():
            st.markdown('<div class="interpretacao-box">', unsafe_allow_html=True)
            st.markdown(st.session_state.interpretacao)
            st.markdown('</div>', unsafe_allow_html=True)
            st.caption("🙏 Lembre-se: As cartas são um guia, não uma verdade absoluta. O livre arbítrio sempre prevalece.")
        
        # Feedback
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👍 Útil", key="feedback_util"):
                st.success("✨ Obrigado pelo feedback! Sua energia ajuda a fortalecer nossa conexão.")
        with col2:
            if st.button("🔄 Nova consulta", key="nova_consulta_pos"):
                for key in ['cartas_sorteadas', 'interpretacao', 'pergunta_atual']:
                    st.session_state[key] = None
                st.rerun()
    
    # Rodapé
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #a0a0a0; padding: 20px;'>
            <small>
            🔮 Baralho Cigano Tradicional • 36 Lâminas • Interpretação com IA Gemini<br>
            ⚡ Desenvolvido com respeito à tradição cigana e tecnologia de ponta<br>
            ✨ Cada consulta é única e pessoal
            </small>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
