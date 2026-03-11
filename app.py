import streamlit as st
import google.generativeai as genai
from datetime import datetime

# ============================================
# CONFIGURAÇÃO INICIAL
# ============================================
st.set_page_config(
    page_title="Baralho Cigano - Método Afrodite",
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
# CSS - DESIGN LIMPO
# ============================================
st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF; }
        .block-container { max-width: 700px; padding-top: 2rem; }
        
        .stButton button {
            background: #000000 !important;
            color: white !important;
            border: none !important;
            border-radius: 50px !important;
            padding: 10px 30px !important;
            width: 100%;
            font-weight: 500;
        }
        
        .stSelectbox div {
            border-radius: 12px !important;
            border: 1px solid #DEE2E6 !important;
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
        
        .instrucao-chat {
            background: #F8F9FA;
            border-radius: 12px;
            padding: 15px;
            margin: 20px 0;
            text-align: center;
            border: 1px dashed #000000;
        }
        
        h1 {
            color: #000000 !important;
            font-weight: 700 !important;
            text-align: center;
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
# LISTA DE NOMES PARA SELECT
# ============================================
LISTA_CARTAS = [""] + [carta["nome"] for carta in BARALHO_CIGANO.values()]

# Posições da tiragem Afrodite
POSICOES_AFRODITE = [
    "1ª carta — Pensamentos e Intenções (você)",
    "2ª carta — Sentimentos (você)",
    "3ª carta — Desejo sexual (você)",
    "4ª carta — Pensamentos e Intenções (ela)",
    "5ª carta — Sentimentos (ela)",
    "6ª carta — Desejo sexual (ela)",
    "7ª carta — O desfecho"
]

# ============================================
# FUNÇÃO DE INTERPRETAÇÃO - MÉTODO AFRODITE
# ============================================
def interpretar_tiragem_afrodite(cartas, pergunta_usuario):
    """Gera uma interpretação completa para as 7 cartas do método Afrodite"""
    try:
        modelo = genai.GenerativeModel('gemini-1.5-flash')
        
        # Preparar dados das cartas
        cartas_descricao = []
        for i, carta_info in enumerate(cartas):
            carta_nome = carta_info['carta']['nome'] if isinstance(carta_info['carta'], dict) else carta_info['carta']
            # Buscar a carta completa
            carta_completa = None
            for c in BARALHO_CIGANO.values():
                if c["nome"] == carta_nome:
                    carta_completa = c
                    break
            
            if carta_completa:
                significado = carta_completa['significado_normal']  # sempre normal
                cartas_descricao.append(
                    f"{i+1}. {POSICOES_AFRODITE[i]}: {carta_nome}"
                )
        
        cartas_texto = "\n".join(cartas_descricao)
        
        prompt = f"""
Você é um mentor espiritual sábio e acolhedor, especialista em Baralho Cigano. Um consulente busca orientação sobre seu relacionamento através do método Afrodite (7 cartas).

## PERGUNTA DO CONSULENTE:
{pergunta_usuario if pergunta_usuario else "O que está acontecendo no meu relacionamento?"}

## CARTAS TIRADAS:
{cartas_texto}

## INSTRUÇÕES:

Escreva uma interpretação completa seguindo APENAS esta estrutura:

## O QUE SE PASSA NA SUA MENTE E NO SEU CORAÇÃO
(Interpretação das cartas 1, 2 e 3)

Para CADA carta:
**Carta [Número] – [Nome da Carta]**
- 2-3 parágrafos com interpretação profunda
- Inclua o significado espiritual relacionado à situação
- Termine com "O que isso significa na prática:" e uma aplicação direta

## O QUE SE PASSA NA MENTE E NO CORAÇÃO DELA
(Interpretação das cartas 4, 5 e 6 - mesma estrutura acima)

## PARA ONDE TUDO ISSO ESTÁ LEVANDO
(Interpretação da carta 7 - o desfecho)
- 3-4 parágrafos mostrando tendências e possibilidades
- Termine com "O que isso significa na prática:"

## O QUE A CIÊNCIA DIZ SOBRE O QUE VOCÊ ESTÁ VIVENDO
(4-6 fatos científicos sobre relacionamentos aplicados à situação)

## SABEDORIA ANCESTRAL PARA O SEU MOMENTO
(Reflexões sobre sabedoria ancestral aplicada à sua vida - use linguagem genérica, sem nomes de escolas filosóficas)

## ILUSÕES QUE VOCÊ PODE ESTAR ALIMENTANDO
(4-6 ilusões comuns, cada uma com explicação)

## AÇÕES QUE VOCÊ PODE TOMAR AGORA
(8-10 ações práticas, numeradas, com explicação)

## PALAVRAS FINAIS
(Um encerramento acolhedor de 3-4 parágrafos)

IMPORTANTE:
- Use linguagem acolhedora e acessível
- Conecte TUDO à pergunta do consulente
- Seja direto, mas nunca cruel
- A verdade pode doer, mas deve vir com acolhimento
"""
        
        response = modelo.generate_content(prompt)
        
        if response and response.text:
            return response.text
        else:
            return gerar_fallback_afrodite(cartas, pergunta_usuario)
            
    except Exception as e:
        return gerar_fallback_afrodite(cartas, pergunta_usuario)

def gerar_fallback_afrodite(cartas, pergunta):
    """Fallback para quando a API falha"""
    
    nomes = [c['carta']['nome'] if isinstance(c['carta'], dict) else c['carta'] for c in cartas]
    
    return f"""
## O QUE SE PASSA NA SUA MENTE E NO SEU CORAÇÃO

**Carta 1 – {nomes[0]}**
Esta carta revela o estado da sua mente neste momento. Você está processando a situação com intensidade, buscando respostas e direção. O que isso significa na prática: seus pensamentos estão acelerados, mas isso pode ser um chamado para desacelerar e observar.

**Carta 2 – {nomes[1]}**
Aqui está a verdade do seu coração. Seus sentimentos são genuínos, mesmo com todas as dificuldades. O que isso significa na prática: o amor ainda existe, mas precisa ser nutrido de forma diferente.

**Carta 3 – {nomes[2]}**
Seu desejo e energia vital estão presentes, mas talvez bloqueados por mágoas ou desconfiança. O que isso significa na prática: a intimidade precisa ser reconstruída com paciência.

## O QUE SE PASSA NA MENTE E NO CORAÇÃO DELA

**Carta 4 – {nomes[3]}**
A mente dela pode estar em modo de defesa, processando mágoas antigas. O que isso significa na prática: ela precisa se sentir segura antes de qualquer aproximação.

**Carta 5 – {nomes[4]}**
Os sentimentos dela por você ainda existem, mas podem estar encobertos por camadas de dor. O que isso significa na prática: há esperança, mas é preciso criar condições para que ela se sinta à vontade.

**Carta 6 – {nomes[5]}**
O desejo dela pode estar adormecido, esperando um ambiente mais seguro para despertar. O que isso significa na prática: não force a intimidade, construa conexão primeiro.

## PARA ONDE TUDO ISSO ESTÁ LEVANDO

**Carta 7 – {nomes[6]}**
O desfecho aponta para a necessidade de movimento consciente. O que isso significa na prática: o resultado depende das escolhas que vocês fizerem a partir de agora.

## AÇÕES QUE VOCÊ PODE TOMAR AGORA

1. **Desacelere**: Estabeleça um período sem conversas pesadas sobre a relação.
2. **Observe sem reagir**: Apenas note os padrões sem tentar corrigir.
3. **Crie segurança**: Seja consistente e previsível em suas ações.
4. **Pratique escuta ativa**: Ouça sem rebater ou justificar.
5. **Estabeleça rituais mínimos**: Momentos curtos de presença sem pressão.
6. **Cuide de si mesmo**: Sua energia afeta diretamente a relação.
7. **Defina um marco**: Estabeleça um prazo para reavaliar a situação.

## PALAVRAS FINAIS

O que as cartas revelam é um convite à consciência. Não há respostas prontas, mas há caminhos que podem ser construídos. A escolha é sua, e isso é libertador.
"""

# ============================================
# INTERFACE PRINCIPAL
# ============================================
def main():
    st.markdown("<h1>🔮 BARALHO CIGANO</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6C757D; margin-bottom: 30px;'>Método: Afrodite • 7 cartas para relacionamentos</p>", unsafe_allow_html=True)
    
    # Inicialização do estado
    if 'etapa' not in st.session_state:
        st.session_state.etapa = 'pergunta'
    if 'pergunta' not in st.session_state:
        st.session_state.pergunta = ""
    if 'cartas_selecionadas' not in st.session_state:
        st.session_state.cartas_selecionadas = [""] * 7
    if 'resultado' not in st.session_state:
        st.session_state.resultado = None
    
    # Container central
    with st.container():
        
        # ETAPA 1: PERGUNTA
        if st.session_state.etapa == 'pergunta':
            pergunta = st.text_area(
                " ",
                placeholder="Qual sua pergunta sobre o relacionamento?",
                height=120,
                key="pergunta_input",
                label_visibility="collapsed"
            )
            
            if pergunta:
                st.session_state.pergunta = pergunta
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Continuar", use_container_width=True):
                if st.session_state.pergunta:
                    st.session_state.etapa = 'cartas'
                    st.rerun()
                else:
                    st.warning("Digite sua pergunta")
        
        # ETAPA 2: SELEÇÃO DAS 7 CARTAS
        elif st.session_state.etapa == 'cartas':
            st.markdown("### Selecione as 7 cartas da sua tiragem")
            
            # Criar selects para cada posição
            cartas_atualizadas = []
            todas_validas = True
            
            for i, posicao in enumerate(POSICOES_AFRODITE):
                st.markdown(f"**{posicao}**")
                
                # Select para a carta
                carta_selecionada = st.selectbox(
                    f"Carta {i+1}",
                    options=LISTA_CARTAS,
                    key=f"carta_{i}",
                    index=LISTA_CARTAS.index(st.session_state.cartas_selecionadas[i]) if st.session_state.cartas_selecionadas[i] in LISTA_CARTAS else 0,
                    label_visibility="collapsed"
                )
                
                cartas_atualizadas.append(carta_selecionada)
                
                if not carta_selecionada:
                    todas_validas = False
                
                st.markdown("---")
            
            # Atualizar session state
            st.session_state.cartas_selecionadas = cartas_atualizadas
            
            # Botões de navegação
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Voltar", use_container_width=True):
                    st.session_state.etapa = 'pergunta'
                    st.rerun()
            
            with col2:
                if st.button("Interpretar", use_container_width=True, type="primary"):
                    if todas_validas:
                        with st.spinner("🔮 Interpretando sua história..."):
                            # Preparar cartas para interpretação
                            cartas_para_interpretar = []
                            for i, nome_carta in enumerate(st.session_state.cartas_selecionadas):
                                # Encontrar a carta completa
                                carta_completa = None
                                for c in BARALHO_CIGANO.values():
                                    if c["nome"] == nome_carta:
                                        carta_completa = c
                                        break
                                
                                if carta_completa:
                                    cartas_para_interpretar.append({
                                        'carta': carta_completa,
                                        'posicao': POSICOES_AFRODITE[i]
                                    })
                            
                            resultado = interpretar_tiragem_afrodite(
                                cartas_para_interpretar,
                                st.session_state.pergunta
                            )
                            st.session_state.resultado = resultado
                            st.session_state.etapa = 'resultado'
                            st.rerun()
                    else:
                        st.warning("Selecione todas as 7 cartas")
        
        # ETAPA 3: RESULTADO
        elif st.session_state.etapa == 'resultado':
            if st.session_state.resultado:
                st.markdown(f'<div class="resultado">{st.session_state.resultado}</div>', unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Nova pergunta", use_container_width=True):
                    for key in ['etapa', 'pergunta', 'cartas_selecionadas', 'resultado']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()
            with col2:
                if st.button("🔄 Nova tiragem", use_container_width=True):
                    st.session_state.cartas_selecionadas = [""] * 7
                    st.session_state.resultado = None
                    st.session_state.etapa = 'cartas'
                    st.rerun()

if __name__ == "__main__":
    main()
