import streamlit as st
import google.generativeai as genai
from datetime import datetime
import json

# ============================================
# CONFIGURAÇÃO INICIAL - DESIGN PREMIUM
# ============================================
st.set_page_config(
    page_title="🔮 Baralho Cigano - Análise Profunda",
    page_icon="🃏",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Configurar API do Gemini
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception as e:
    st.error("🔑 Erro na configuração da API. Verifique sua chave no Streamlit Secrets.")
    st.stop()

# ============================================
# CSS DESIGN PREMIUM - BRANCO/PRETO
# ============================================
st.markdown("""
    <style>
        /* MAIN APP - FUNDO BRANCO */
        .stApp {
            background-color: #FFFFFF;
        }
        
        /* SIDEBAR - FUNDO PRETO */
        section[data-testid="stSidebar"] {
            background-color: #000000 !important;
        }
        
        section[data-testid="stSidebar"] * {
            color: #FFFFFF !important;
        }
        
        section[data-testid="stSidebar"] .stSelectbox label,
        section[data-testid="stSidebar"] .stSelectbox div,
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] h4 {
            color: #FFFFFF !important;
        }
        
        /* CARDS DAS CARTAS - ELEGANTES */
        .carta-card {
            background: linear-gradient(145deg, #F8F9FA, #E9ECEF);
            border: 1px solid #DEE2E6;
            border-radius: 12px;
            padding: 20px 10px;
            margin: 10px 0;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            transition: all 0.3s;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            min-height: 280px;
        }
        
        .carta-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            border-color: #495057;
        }
        
        .carta-invertida {
            background: linear-gradient(145deg, #2B2B2B, #1A1A1A);
            border-color: #6C757D;
        }
        
        .carta-invertida .carta-nome,
        .carta-invertida .carta-posicao,
        .carta-invertida .carta-palavras,
        .carta-invertida .carta-orientacao,
        .carta-invertida div {
            color: #FFFFFF !important;
        }
        
        .carta-simbolo {
            font-size: 64px;
            margin-bottom: 10px;
            color: #212529;
        }
        
        .carta-invertida .carta-simbolo {
            color: #FFD700;
        }
        
        .carta-nome {
            font-size: 20px;
            font-weight: 700;
            color: #212529;
            margin-bottom: 5px;
        }
        
        .carta-posicao {
            font-size: 14px;
            color: #6C757D;
            margin-bottom: 10px;
            font-style: italic;
            font-weight: 500;
        }
        
        .carta-palavras {
            font-size: 12px;
            color: #495057;
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid #DEE2E6;
            font-weight: 500;
        }
        
        .carta-orientacao {
            margin-top: 8px;
            font-size: 11px;
            color: #6C757D;
            text-transform: uppercase;
            letter-spacing: 2px;
            font-weight: 600;
        }
        
        /* BOX DE INTERPRETAÇÃO - PROFISSIONAL */
        .interpretacao-box {
            background: #F8F9FA;
            border-left: 8px solid #000000;
            padding: 30px;
            border-radius: 0 12px 12px 0;
            margin: 20px 0;
            font-size: 18px;
            line-height: 1.8;
            color: #212529;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }
        
        /* INSTRUÇÕES */
        .instrucoes-box {
            background: #F8F9FA;
            border: 1px solid #DEE2E6;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 30px;
            color: #212529;
        }
        
        .instrucoes-box h4 {
            color: #000000;
            font-weight: 700;
            margin-bottom: 15px;
        }
        
        /* BOTÕES */
        .stButton button {
            background: #000000 !important;
            color: white !important;
            font-weight: 600 !important;
            border: none !important;
            border-radius: 50px !important;
            padding: 10px 25px !important;
            transition: all 0.3s !important;
            border: 1px solid #000000 !important;
        }
        
        .stButton button:hover {
            background: #FFFFFF !important;
            color: #000000 !important;
            border: 1px solid #000000 !important;
            transform: scale(1.02);
        }
        
        /* INPUTS E SELECTS */
        .stTextInput input, .stSelectbox div {
            border-radius: 8px !important;
            border: 1px solid #DEE2E6 !important;
        }
        
        .stTextInput input:focus {
            border-color: #000000 !important;
            box-shadow: 0 0 0 1px #000000 !important;
        }
        
        /* TÍTULOS */
        h1, h2, h3 {
            color: #000000 !important;
            font-weight: 700 !important;
        }
        
        /* RODAPÉ */
        .rodape {
            text-align: center;
            color: #6C757D;
            padding: 30px 20px;
            border-top: 1px solid #DEE2E6;
            margin-top: 40px;
        }
        
        /* PROGRESSO */
        .progresso-card {
            background: #F8F9FA;
            border-radius: 12px;
            padding: 15px;
            margin: 10px 0;
            text-align: center;
            border: 1px solid #DEE2E6;
        }
        
        .progresso-numero {
            font-size: 36px;
            font-weight: 800;
            color: #000000;
        }
    </style>
""", unsafe_allow_html=True)

# ============================================
# BASE DE CONHECIMENTO - 36 CARTAS + JUNG
# ============================================
BARALHO_CIGANO = {
    1: {
        "nome": "O Cavaleiro", 
        "simbolo": "♞", 
        "palavras_chave": "Notícias, movimento, chegada, mensageiro",
        "arquetipo_jung": "O Mensageiro - Hermes, Mercúrio, transição entre mundos",
        "sombra": "Pressa, ansiedade, notícias indesejadas",
        "anima_animus": "Figura masculina dinâmica, parceiro em movimento",
        "significado_normal": "Notícias chegando, visitas, movimento rápido. Indica mensagens importantes a caminho. Representa o arquétipo do mensageiro que traz transformação.",
        "significado_invertido": "Atrasos, notícias adiadas, visitas indesejadas. A sombra da pressa - momentos de pausa necessária."
    },
    2: {
        "nome": "O Trevo", 
        "simbolo": "🍀", 
        "palavras_chave": "Sorte, esperança, brevidade, sincronicidade",
        "arquetipo_jung": "Sincronicidade - eventos significativos, acaso com propósito",
        "sombra": "Sorte atrasada, expectativas irreais",
        "anima_animus": "Esperança, fé no invisível",
        "significado_normal": "Pequena sorte, oportunidades passageiras. Momento de esperança e otimismo. Jung via nestes eventos a sincronicidade - conexões significativas além da causalidade.",
        "significado_invertido": "Sorte atrasada, pequenas frustrações. A sombra da esperança - cuidado com expectativas irreais."
    },
    3: {
        "nome": "O Navio", 
        "simbolo": "⛵", 
        "palavras_chave": "Viagem, comércio, distância, jornada",
        "arquetipo_jung": "A Jornada - processo de individuação, travessia",
        "sombra": "Jornada interrompida, medo do desconhecido",
        "anima_animus": "Expansão da consciência, horizontes",
        "significado_normal": "Viagens, negócios à distância, mudanças. Expansão de horizontes. A jornada do herói em busca de si mesmo.",
        "significado_invertido": "Viagem adiada, problemas no transporte. Resistência à transformação."
    },
    4: {
        "nome": "A Casa", 
        "simbolo": "🏠", 
        "palavras_chave": "Lar, família, estabilidade, self",
        "arquetipo_jung": "O Self - totalidade, centro da psique",
        "sombra": "Insegurança doméstica, desarmonia",
        "anima_animus": "Segurança interior, lar emocional",
        "significado_normal": "Segurança doméstica, harmonia familiar. Representa o Self - nossa morada interior, centro do ser.",
        "significado_invertido": "Problemas em casa, desarmonia familiar. A sombra do lar - necessidade de reconstrução."
    },
    5: {
        "nome": "A Árvore", 
        "simbolo": "🌳", 
        "palavras_chave": "Saúde, crescimento, ancestralidade",
        "arquetipo_jung": "A Grande Mãe - nutriz, raízes, ancestralidade",
        "sombra": "Estagnação, bloqueio energético",
        "anima_animus": "Conexão com raízes, crescimento interior",
        "significado_normal": "Boa saúde, crescimento pessoal. A Árvore da Vida - conexão com ancestrais e o inconsciente coletivo.",
        "significado_invertido": "Problemas de saúde, estagnação. Bloqueios no fluxo vital."
    },
    6: {
        "nome": "As Nuvens", 
        "simbolo": "☁️", 
        "palavras_chave": "Confusão, dúvida, incerteza",
        "arquetipo_jung": "A Névoa - inconsciente, mistério, transição",
        "sombra": "Confusão mental, ilusão",
        "anima_animus": "Intuição enevoada, busca por clareza",
        "significado_normal": "Período de confusão, falta de clareza. A névoa do inconsciente que antecede a iluminação.",
        "significado_invertido": "Esclarecimento, névoa se dissipando. A verdade emergindo das sombras."
    },
    7: {
        "nome": "A Serpente", 
        "simbolo": "🐍", 
        "palavras_chave": "Traição, sabedoria, tentação",
        "arquetipo_jung": "A Sombra - aspectos reprimidos, sabedoria instintiva",
        "sombra": "Falsidade, manipulação",
        "anima_animus": "Sabedoria feminina, intuição",
        "significado_normal": "Cuidado com pessoas falsas. Sabedoria feminina, intuição aguçada. A serpente como símbolo de transformação e cura.",
        "significado_invertido": "Perigo afastado, falsidade descoberta. Integração da sombra."
    },
    8: {
        "nome": "O Caixão", 
        "simbolo": "⚰️", 
        "palavras_chave": "Fim, transformação, renascimento",
        "arquetipo_jung": "Morte/Renascimento - transformação, individuação",
        "sombra": "Medo da morte, apego ao velho",
        "anima_animus": "Libertação, transcendência",
        "significado_normal": "Fim de ciclo, transformação profunda. A morte simbólica necessária para o renascimento.",
        "significado_invertido": "Renascimento, superação. O pior já passou."
    },
    9: {
        "nome": "O Buquê", 
        "simbolo": "💐", 
        "palavras_chave": "Felicidade, convite, beleza",
        "arquetipo_jung": "A Flor - self realizado, beleza interior",
        "sombra": "Felicidade superficial",
        "anima_animus": "Reconhecimento, afeto",
        "significado_normal": "Alegria, presentes, convites. Reconhecimento e momentos felizes. A flor da individuação.",
        "significado_invertido": "Felicidade adiada. Pequenas decepções."
    },
    10: {
        "nome": "A Foice", 
        "simbolo": "🔪", 
        "palavras_chave": "Corte, decisão, separação",
        "arquetipo_jung": "O Ceifador - discernimento, cortes necessários",
        "sombra": "Separação dolorosa, violência",
        "anima_animus": "Decisão, clareza",
        "significado_normal": "Decisões rápidas, cortes necessários. Separação ou mudança brusca.",
        "significado_invertido": "Decisão adiada, perigo evitado."
    },
    11: {
        "nome": "O Chicote", 
        "simbolo": "🪢", 
        "palavras_chave": "Conflito, discussão, tensão",
        "arquetipo_jung": "Confronto - integração da sombra projetada",
        "sombra": "Violência, agressividade",
        "anima_animus": "Diálogo necessário",
        "significado_normal": "Discussões, conflitos, tensões. Necessidade de diálogo claro.",
        "significado_invertido": "Trégua, resolução de conflitos."
    },
    12: {
        "nome": "Os Pássaros", 
        "simbolo": "🐦", 
        "palavras_chave": "Conversas, ansiedade, contato",
        "arquetipo_jung": "Mensageiros - comunicação entre consciente/inconsciente",
        "sombra": "Fofocas, ansiedade social",
        "anima_animus": "Conexão, diálogo",
        "significado_normal": "Boas conversas, contatos sociais. Notícias através de pessoas.",
        "significado_invertido": "Fofocas, ansiedade, conversas desagradáveis."
    },
    13: {
        "nome": "A Criança", 
        "simbolo": "👶", 
        "palavras_chave": "Novo começo, inocência, confiança",
        "arquetipo_jung": "A Criança Divina - potencial, futuro, renascimento",
        "sombra": "Imaturidade, infantilidade",
        "anima_animus": "Inocência, confiança",
        "significado_normal": "Novos projetos, gravidez, confiança. A criança interior que precisa ser nutrida.",
        "significado_invertido": "Imaturidade, atraso em projetos. Cuidado com ingenuidade."
    },
    14: {
        "nome": "A Raposa", 
        "simbolo": "🦊", 
        "palavras_chave": "Esperteza, desconfiança, trabalho",
        "arquetipo_jung": "O Trickster - astúcia, travessura, adaptação",
        "sombra": "Manipulação, engano",
        "anima_animus": "Inteligência prática",
        "significado_normal": "Pessoa astuta, inteligente. O Trickster que traz ensinamentos através da esperteza.",
        "significado_invertido": "Engano descoberto, pessoa confiável. Integração do Trickster."
    },
    15: {
        "nome": "O Urso", 
        "simbolo": "🐻", 
        "palavras_chave": "Força, poder, proteção",
        "arquetipo_jung": "O Guardião - força bruta, poder ancestral",
        "sombra": "Abuso de poder, possessividade",
        "anima_animus": "Proteção materna/paterna",
        "significado_normal": "Autoridade, proteção materna, força interior. O poder que protege.",
        "significado_invertido": "Abuso de poder, ciúmes, pessoa possessiva. A sombra da autoridade."
    },
    16: {
        "nome": "As Estrelas", 
        "simbolo": "⭐", 
        "palavras_chave": "Espiritualidade, esperança, destino",
        "arquetipo_jung": "O Self - totalidade, guia interior",
        "sombra": "Desesperança, bloqueio espiritual",
        "anima_animus": "Conexão divina",
        "significado_normal": "Boa sorte espiritual, realização de desejos. As estrelas como mapa da alma.",
        "significado_invertido": "Desesperança, bloqueio espiritual. Momento de fé."
    },
    17: {
        "nome": "A Cegonha", 
        "simbolo": "🕊️", 
        "palavras_chave": "Mudança, parto, evolução",
        "arquetipo_jung": "Transformação - novos começos, fertilidade",
        "sombra": "Mudança indesejada",
        "anima_animus": "Criatividade, nascimento",
        "significado_normal": "Mudança positiva, nascimento, evolução na vida. O novo que chega.",
        "significado_invertido": "Mudança difícil, resistência a transformações."
    },
    18: {
        "nome": "O Cachorro", 
        "simbolo": "🐕", 
        "palavras_chave": "Amizade, lealdade, confiança",
        "arquetipo_jung": "O Amigo Fiel - lealdade, instinto domesticado",
        "sombra": "Lealdade cega, dependência",
        "anima_animus": "Confiança, parceria",
        "significado_normal": "Amigo verdadeiro, parceria fiel, amor incondicional.",
        "significado_invertido": "Amizade falsa, deslealdade, confiança quebrada."
    },
    19: {
        "nome": "A Torre", 
        "simbolo": "🏰", 
        "palavras_chave": "Solidão, autoridade, isolamento",
        "arquetipo_jung": "O Eremita - introspecção, sabedoria interior",
        "sombra": "Aprisionamento, arrogância",
        "anima_animus": "Autoconhecimento",
        "significado_normal": "Instituições, orgulho, posição social. A torre como espaço de sabedoria na solidão.",
        "significado_invertido": "Aprisionamento, arrogância, isolamento forçado."
    },
    20: {
        "nome": "O Jardim", 
        "simbolo": "🌺", 
        "palavras_chave": "Socialização, eventos, admiração",
        "arquetipo_jung": "O Paraíso - coletividade, pertencimento",
        "sombra": "Futilidade social",
        "anima_animus": "Conexão comunitária",
        "significado_normal": "Eventos sociais, networking, admiração pública. O self em relação.",
        "significado_invertido": "Fofocas, eventos cancelados, vida social negativa."
    },
    21: {
        "nome": "A Montanha", 
        "simbolo": "⛰️", 
        "palavras_chave": "Obstáculo, desafio, bloqueio",
        "arquetipo_jung": "A Montanha - desafio, transcendência",
        "sombra": "Impedimento, frustração",
        "anima_animus": "Superação, força",
        "significado_normal": "Desafios a superar, obstáculos temporários. A montanha como jornada de individuação.",
        "significado_invertido": "Obstáculo superado, caminho livre. Vitória."
    },
    22: {
        "nome": "O Caminho", 
        "simbolo": "🛤️", 
        "palavras_chave": "Escolha, decisão, opções",
        "arquetipo_jung": "A Encruzilhada - escolhas, livre arbítrio",
        "sombra": "Indecisão, caminho errado",
        "anima_animus": "Direção, propósito",
        "significado_normal": "Escolhas a fazer, encruzilhada. O livre arbítrio e a responsabilidade das escolhas.",
        "significado_invertido": "Indecisão, caminho errado. Momento de parar."
    },
    23: {
        "nome": "O Rato", 
        "simbolo": "🐀", 
        "palavras_chave": "Perda, roubo, desgaste",
        "arquetipo_jung": "A Sombra - aspectos que nos corroem",
        "sombra": "Autossabotagem, perda",
        "anima_animus": "Desapego, renovação",
        "significado_normal": "Pequenas perdas, desgaste, algo se esvaindo. A sombra que consome energia.",
        "significado_invertido": "Perda recuperada, problema resolvido. Alívio."
    },
    24: {
        "nome": "O Coração", 
        "simbolo": "❤️", 
        "palavras_chave": "Amor, paixão, emoção",
        "arquetipo_jung": "Eros - amor, conexão, anima/animus",
        "sombra": "Dependência emocional, ciúmes",
        "anima_animus": "Amor verdadeiro, união",
        "significado_normal": "Amor verdadeiro, romance, felicidade no amor. A integração da anima/animus.",
        "significado_invertido": "Desamor, coração partido. Feridas do arquétipo do amor."
    },
    25: {
        "nome": "A Aliança", 
        "simbolo": "💍", 
        "palavras_chave": "Compromisso, casamento, parceria",
        "arquetipo_jung": "A Conjunção - união dos opostos, totalidade",
        "sombra": "Compromisso vazio",
        "anima_animus": "União sagrada",
        "significado_normal": "Casamento, sociedade, contratos. A conjunção alquímica dos opostos.",
        "significado_invertido": "Compromisso quebrado, divórcio. Sombra da união."
    },
    26: {
        "nome": "O Livro", 
        "simbolo": "📚", 
        "palavras_chave": "Segredo, conhecimento, estudo",
        "arquetipo_jung": "O Sábio - conhecimento, sabedoria interior",
        "sombra": "Saber superficial, dogmatismo",
        "anima_animus": "Busca pela verdade",
        "significado_normal": "Aprendizado, segredos revelados. O livro da vida, conhecimento interior.",
        "significado_invertido": "Segredo mantido, ignorância. Mistério não resolvido."
    },
    27: {
        "nome": "A Carta", 
        "simbolo": "✉️", 
        "palavras_chave": "Mensagem, comunicação, documento",
        "arquetipo_jung": "O Mensageiro - comunicação do inconsciente",
        "sombra": "Má comunicação",
        "anima_animus": "Diálogo, expressão",
        "significado_normal": "Notícias formais, documentos. Mensagens do inconsciente.",
        "significado_invertido": "Mensagem não entregue. Comunicação falha."
    },
    28: {
        "nome": "O Homem", 
        "simbolo": "👨", 
        "palavras_chave": "Masculino, ação, figura paterna",
        "arquetipo_jung": "Animus - princípio masculino interior",
        "sombra": "Masculino tóxico, passividade",
        "anima_animus": "Ação, iniciativa",
        "significado_normal": "Figura masculina, parceiro. O animus integrado na psique feminina.",
        "significado_invertido": "Homem ausente, masculino tóxico. Sombra do animus."
    },
    29: {
        "nome": "A Mulher", 
        "simbolo": "👩", 
        "palavras_chave": "Feminino, intuição, figura materna",
        "arquetipo_jung": "Anima - princípio feminino interior",
        "sombra": "Feminino reprimido, possessividade",
        "anima_animus": "Intuição, acolhimento",
        "significado_normal": "Figura feminina, parceira. A anima integrada na psique masculina.",
        "significado_invertido": "Mulher ausente, feminino bloqueado. Sombra da anima."
    },
    30: {
        "nome": "Os Lírios", 
        "simbolo": "⚜️", 
        "palavras_chave": "Virtude, paz, harmonia",
        "arquetipo_jung": "A Pureza - self realizado, transcendência",
        "sombra": "Falsa pureza, hipocrisia",
        "anima_animus": "Harmonia interior",
        "significado_normal": "Paz interior, harmonia familiar. A pureza do self realizado.",
        "significado_invertido": "Conflito familiar, desarmonia. Sombra da virtude."
    },
    31: {
        "nome": "O Sol", 
        "simbolo": "☀️", 
        "palavras_chave": "Sucesso, energia, felicidade",
        "arquetipo_jung": "O Self Iluminado - consciência, totalidade",
        "sombra": "Ego inflado, arrogância",
        "anima_animus": "Realização, alegria",
        "significado_normal": "Sucesso garantido, felicidade plena. O self iluminado pela consciência.",
        "significado_invertido": "Sucesso temporário, energia baixa. Eclipse do self."
    },
    32: {
        "nome": "A Lua", 
        "simbolo": "🌙", 
        "palavras_chave": "Intuição, emoção, ciclo",
        "arquetipo_jung": "A Grande Mãe - inconsciente, mistério",
        "sombra": "Confusão emocional, medos",
        "anima_animus": "Intuição, receptividade",
        "significado_normal": "Intuição aguçada, emoções. A luz do inconsciente.",
        "significado_invertido": "Confusão emocional, intuição falha. A sombra da lua."
    },
    33: {
        "nome": "A Chave", 
        "simbolo": "🔑", 
        "palavras_chave": "Solução, destino, abertura",
        "arquetipo_jung": "A Solução - chave para o inconsciente",
        "sombra": "Oportunidade perdida",
        "anima_animus": "Resolução, acesso",
        "significado_normal": "Solução encontrada, portas abertas. A chave para o self.",
        "significado_invertido": "Oportunidade perdida. Solução escondida."
    },
    34: {
        "nome": "O Peixe", 
        "simbolo": "🐟", 
        "palavras_chave": "Dinheiro, abundância, prosperidade",
        "arquetipo_jung": "Abundância - nutrição, prosperidade",
        "sombra": "Avareza, escassez",
        "anima_animus": "Fartura, provisão",
        "significado_normal": "Ganhos financeiros, prosperidade. O peixe como símbolo de abundância.",
        "significado_invertido": "Dificuldade financeira. Bloqueio da prosperidade."
    },
    35: {
        "nome": "A Âncora", 
        "simbolo": "⚓", 
        "palavras_chave": "Estabilidade, segurança, permanência",
        "arquetipo_jung": "O Centro - segurança, grounding",
        "sombra": "Estagnação, imobilidade",
        "anima_animus": "Firmeza, estabilidade",
        "significado_normal": "Segurança no trabalho, relacionamento estável. A âncora do self.",
        "significado_invertido": "Instabilidade, insegurança. Necessidade de mudança."
    },
    36: {
        "nome": "A Cruz", 
        "simbolo": "✝️", 
        "palavras_chave": "Fardo, destino, espiritualidade",
        "arquetipo_jung": "Sacrifício - transcendência, individuação",
        "sombra": "Vitimização, martírio",
        "anima_animus": "Fé, propósito",
        "significado_normal": "Fardo a carregar, destino. A cruz como caminho de individuação.",
        "significado_invertido": "Alívio, fardo retirado. Superação da provação."
    }
}

# ============================================
# FUNÇÃO DE MIGRAÇÃO - GARANTE CAMPOS JUNGUIANOS
# ============================================
def migrar_cartas_para_formato_jung():
    """
    Garante que TODAS as cartas tenham os campos junguianos
    Corrige o KeyError 'arquetipo_jung' (nota: está escrito 'arquetipo' sem acento no código)
    """
    campos_obrigatorios = {
        'arquetipo_jung': 'Arquétipo Ancestral',
        'sombra': 'Sombra a ser integrada',
        'anima_animus': 'Integração dos opostos'
    }
    
    for id_carta, carta in BARALHO_CIGANO.items():
        for campo, valor_padrao in campos_obrigatorios.items():
            if campo not in carta:
                carta[campo] = valor_padrao
                print(f"⚠️ Campo '{campo}' adicionado à carta {carta['nome']}")
    
    return BARALHO_CIGANO

# APLICAR MIGRAÇÃO IMEDIATAMENTE
BARALHO_CIGANO = migrar_cartas_para_formato_jung()

# ============================================
# FUNÇÕES DE BUSCA E VALIDAÇÃO
# ============================================
def buscar_carta_por_nome(nome_busca):
    """Busca inteligente de cartas"""
    nome_busca = nome_busca.strip().lower()
    
    variacoes = {
        "cavaleiro": "O Cavaleiro", "cavalo": "O Cavaleiro",
        "trevo": "O Trevo",
        "navio": "O Navio", "barco": "O Navio",
        "casa": "A Casa",
        "arvore": "A Árvore", "árvore": "A Árvore",
        "nuvens": "As Nuvens", "nuvem": "As Nuvens",
        "serpente": "A Serpente", "cobra": "A Serpente",
        "caixao": "O Caixão", "caixão": "O Caixão",
        "buque": "O Buquê", "buquê": "O Buquê", "flores": "O Buquê",
        "foice": "A Foice",
        "chicote": "O Chicote",
        "passaros": "Os Pássaros", "pássaros": "Os Pássaros", "passaro": "Os Pássaros",
        "crianca": "A Criança", "criança": "A Criança",
        "raposa": "A Raposa",
        "urso": "O Urso",
        "estrelas": "As Estrelas",
        "cegonha": "A Cegonha",
        "cachorro": "O Cachorro", "cao": "O Cachorro", "cão": "O Cachorro",
        "torre": "A Torre",
        "jardim": "O Jardim",
        "montanha": "A Montanha",
        "caminho": "O Caminho",
        "rato": "O Rato",
        "coracao": "O Coração", "coração": "O Coração",
        "alianca": "A Aliança", "aliança": "A Aliança",
        "livro": "O Livro",
        "carta": "A Carta",
        "homem": "O Homem",
        "mulher": "A Mulher",
        "lirios": "Os Lírios", "lírios": "Os Lírios",
        "sol": "O Sol",
        "lua": "A Lua",
        "chave": "A Chave",
        "peixe": "O Peixe",
        "ancora": "A Âncora", "âncora": "A Âncora",
        "cruz": "A Cruz"
    }
    
    if nome_busca in variacoes:
        nome_correto = variacoes[nome_busca]
        for id, carta in BARALHO_CIGANO.items():
            if carta["nome"].lower() == nome_correto.lower():
                return id, carta
    
    for id, carta in BARALHO_CIGANO.items():
        if carta["nome"].lower() == nome_busca:
            return id, carta
    
    for id, carta in BARALHO_CIGANO.items():
        if nome_busca in carta["nome"].lower():
            return id, carta
    
    return None, None

def validar_carta(nome_carta):
    id, carta = buscar_carta_por_nome(nome_carta)
    if carta:
        return True, id, carta
    return False, None, None

def criar_card_carta(carta, posicao, orientacao):
    """Card elegante para as cartas"""
    classe_carta = "carta-card"
    if orientacao == 'invertida':
        classe_carta += " carta-invertida"
    
    simbolo_orientacao = " 🔄" if orientacao == 'invertida' else ""
    
    html_card = f"""
    <div class="{classe_carta}">
        <div class="carta-simbolo">{carta['simbolo']}</div>
        <div class="carta-nome">{carta['nome']}{simbolo_orientacao}</div>
        <div class="carta-posicao">📍 {posicao}</div>
        <div class="carta-palavras">{carta['palavras_chave']}</div>
        <div class="carta-orientacao">{orientacao.upper()}</div>
    </div>
    """
    return html_card

def obter_arquetipo_seguro(carta_info):
    """
    Função segura para obter o arquétipo da carta
    Previne KeyError em qualquer situação
    """
    try:
        # Tentar obter da carta no session_state
        if 'carta' in carta_info and carta_info['carta']:
            carta = carta_info['carta']
            if 'arquetipo_jung' in carta and carta['arquetipo_jung']:
                return carta['arquetipo_jung'].split(' - ')[0]
        
        # Tentar obter pelo ID
        if 'id' in carta_info and carta_info['id'] in BARALHO_CIGANO:
            carta_original = BARALHO_CIGANO[carta_info['id']]
            if 'arquetipo_jung' in carta_original and carta_original['arquetipo_jung']:
                return carta_original['arquetipo_jung'].split(' - ')[0]
        
        # Tentar obter pelo nome
        if 'carta' in carta_info and 'nome' in carta_info['carta']:
            nome_carta = carta_info['carta']['nome']
            for cid, cdata in BARALHO_CIGANO.items():
                if cdata['nome'] == nome_carta and 'arquetipo_jung' in cdata:
                    return cdata['arquetipo_jung'].split(' - ')[0]
        
    except Exception:
        pass
    
    return "Sabedoria Ancestral"

def atualizar_cartas_session_state():
    """
    Atualiza todas as cartas no session_state com os dados mais recentes do BARALHO_CIGANO
    """
    if 'cartas_adicionadas' in st.session_state and st.session_state.cartas_adicionadas:
        cartas_atualizadas = []
        for carta_info in st.session_state.cartas_adicionadas:
            if 'id' in carta_info and carta_info['id'] in BARALHO_CIGANO:
                # Substituir pela carta atualizada do dicionário global
                nova_carta_info = {
                    'carta': BARALHO_CIGANO[carta_info['id']].copy(),
                    'id': carta_info['id'],
                    'orientacao': carta_info['orientacao'],
                    'posicao': carta_info['posicao']
                }
                cartas_atualizadas.append(nova_carta_info)
            else:
                cartas_atualizadas.append(carta_info)
        
        st.session_state.cartas_adicionadas = cartas_atualizadas
        return True
    return False

# ============================================
# FUNÇÃO DE INTERPRETAÇÃO PROFUNDA COM GEMINI + JUNG
# ============================================
def interpretar_tiragem(cartas, pergunta_usuario):
    """Interpretação profunda com contexto da pergunta, pesquisa Google e análise Junguiana"""
    try:
        modelo = genai.GenerativeModel('gemini-1.5-pro-latest')
        
        # Preparar dados das cartas com análise junguiana
        cartas_jung = []
        for carta_info in cartas:
            carta = carta_info['carta']
            orientacao = carta_info['orientacao']
            
            # Garantir que todos os campos existem
            arquetipo = carta.get('arquetipo_jung', 'Arquétipo Ancestral')
            sombra = carta.get('sombra', 'Sombra a ser integrada')
            anima_animus = carta.get('anima_animus', 'Integração dos opostos')
            
            cartas_jung.append({
                'posicao': carta_info['posicao'],
                'nome': carta['nome'],
                'simbolo': carta['simbolo'],
                'orientacao': orientacao,
                'significado': carta['significado_invertido'] if orientacao == 'invertida' else carta['significado_normal'],
                'arquetipo_jung': arquetipo,
                'sombra': sombra,
                'anima_animus': anima_animus,
                'palavras_chave': carta['palavras_chave']
            })
        
        # PROMPT PROFISSIONAL COM PESQUISA GOOGLE + ANÁLISE JUNGUIANA
        prompt = f"""VOCÊ É UM MESTRE EM BARALHO CIGANO (LENORMAND), PSICÓLOGO ANALÍTICO JUNGUIANO E PESQUISADOR.

## CONTEXTO DA CONSULTA:
{pergunta_usuario if pergunta_usuario else "Consulta geral de autoconhecimento"}

## CARTAS TIRADAS FISICAMENTE PELO CONSULENTE:
"""
        for carta in cartas_jung:
            prompt += f"""
📍 {carta['posicao']}: {carta['nome']} ({carta['orientacao'].upper()})
• Simbologia: {carta['simbolo']} - {carta['palavras_chave']}
• Significado Tradicional: {carta['significado']}
• Arquétipo de Jung: {carta['arquetipo_jung']}
• Aspectos da Sombra: {carta['sombra']}
• Integração Anima/Animus: {carta['anima_animus']}
"""

        prompt += f"""
## INSTRUÇÕES ESPECÍFICAS:

1️⃣ **PESQUISA GOOGLE ATIVA**
- Busque ativamente conhecimento sobre: {pergunta_usuario if pergunta_usuario else "autoconhecimento e desenvolvimento pessoal"}
- Pesquise sobre os arquétipos junguianos relacionados às cartas
- Traga referências de especialistas em Baralho Cigano
- Contextualize com sabedoria ancestral cigana

2️⃣ **ANÁLISE JUNGUIANA PROFUNDA**
- Identifique como os arquétipos se manifestam na vida do consulente
- Analise o processo de individuação revelado pelas cartas
- Traga a sombra que precisa ser integrada
- Mostre como a anima/animus está se expressando
- Relacione com sincronicidade e inconsciente coletivo

3️⃣ **CONEXÃO COM A PERGUNTA**
- Responda DIRETAMENTE à pergunta do consulente
- Use a pergunta como fio condutor de toda a interpretação
- Cada carta deve ser interpretada à luz da questão trazida
- Se não houver pergunta, foque em autoconhecimento

4️⃣ **LEITURA INTEGRADA DAS CARTAS**
- NÃO interprete as cartas isoladamente
- Conte uma história que conecte Passado → Presente → Futuro
- Mostre a EVOLUÇÃO da situação
- Crie uma narrativa coesa e transformadora

5️⃣ **LINGUAGEM E ESTRUTURA**
- Use linguagem acolhedora, sábia e acessível
- Estruture em parágrafos fluidos (não use bullet points)
- Mínimo de 20 linhas de interpretação profunda
- Termine com uma mensagem de empoderamento

## SUA INTERPRETAÇÃO PROFISSIONAL:
"""
        
        generation_config = {
            "temperature": 0.9,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 2048,
        }
        
        response = modelo.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        if response and response.text:
            return response.text
        else:
            return gerar_fallback_profissional(cartas_jung, pergunta_usuario)
            
    except Exception as e:
        return gerar_fallback_profissional(cartas_jung if 'cartas_jung' in locals() else [], pergunta_usuario)

def gerar_fallback_profissional(cartas, pergunta):
    """Fallback elegante quando API falha"""
    
    if not cartas or len(cartas) < 3:
        return "🔮 Sua tiragem está pronta para ser interpretada. Por favor, tente novamente em instantes."
    
    texto = f"""🔮 **ANÁLISE PROFUNDA DO BARALHO CIGANO**

🎴 **Sua Tiragem Revela:**

**Passado - {cartas[0]['nome']} ({cartas[0]['orientacao'].upper()})**
{cartas[0]['significado']}

**Arquétipo de Jung:** {cartas[0].get('arquetipo_jung', 'Arquétipo Ancestral')}
Este arquétipo emerge do inconsciente coletivo trazendo uma sabedoria ancestral para sua jornada.

**Presente - {cartas[1]['nome']} ({cartas[1]['orientacao'].upper()})**
{cartas[1]['significado']}

**Aspectos da Sombra:** {cartas[1].get('sombra', 'Sombra a ser integrada')}
A sombra não é sua inimiga, mas sim a guardiã de seu potencial não reconhecido.

**Futuro - {cartas[2]['nome']} ({cartas[2]['orientacao'].upper()})**
{cartas[2]['significado']}

**Integração Anima/Animus:** {cartas[2].get('anima_animus', 'Integração dos opostos')}
A totalidade psíquica se revela na dança entre os opostos complementares.

💫 **SÍNTESE JUNGUIANA**

O Baralho Cigano, assim como os sonhos para Jung, é uma ponte entre seu consciente e inconsciente. As cartas que você tirou fisicamente carregam sua energia única e neste momento revelam:

A jornada do **{cartas[0]['nome']}** para o **{cartas[1]['nome']}** e então para o **{cartas[2]['nome']}** conta a história de {pergunta if pergunta else "sua evolução pessoal"}.

O inconsciente coletivo, através destes símbolos arquetípicos, sussurra: você está no caminho da individuação. Cada carta é um espelho de sua psique em movimento.

🌟 **MENSAGEM DE SABEDORIA**

Como diria Jung: "Quem olha para fora sonha; quem olha para dentro desperta." Suas cartas são um convite ao despertar. Confie no processo de transformação que já está em curso.

🙏 Que a sabedoria ancestral do Baralho Cigano ilumine seu caminho."""
    
    return texto

# ============================================
# INTERFACE PRINCIPAL
# ============================================
def main():
    st.title("🔮 Baralho Cigano • Análise Junguiana")
    st.markdown("---")
    
    # ============================================
    # CORREÇÃO DE MIGRAÇÃO - LIMPA SESSION STATE PROBLEMÁTICO
    # ============================================
    if 'cartas_adicionadas' in st.session_state:
        # Verificar se as cartas têm os campos junguianos
        if st.session_state.cartas_adicionadas:
            primeira_carta = st.session_state.cartas_adicionadas[0]
            if 'carta' in primeira_carta:
                if 'arquetipo_jung' not in primeira_carta['carta']:
                    # Session state corrompido - limpar completamente
                    st.session_state.cartas_adicionadas = []
                    st.session_state.interpretacao = None
                    st.warning("🔄 Sistema atualizado! Por favor, insira novamente suas cartas.", icon="🃏")
    
    # Atualizar cartas existentes com os dados mais recentes
    atualizar_cartas_session_state()
    
    # Instruções elegantes
    st.markdown("""
    <div class="instrucoes-box">
        <h4>🎴 RITUAL DE CONSULTA</h4>
        <p style="font-size: 16px; line-height: 1.8;">
        1️⃣ Pegue seu baralho físico de 36 cartas<br>
        2️⃣ Embaralhe enquanto formula sua pergunta interiormente<br>
        3️⃣ Tire 3 cartas fisicamente na ordem: PASSADO • PRESENTE • FUTURO<br>
        4️⃣ Insira os nomes das cartas e suas orientações<br>
        5️⃣ Receba uma análise profunda com Psicologia Junguiana
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Inicializar session state
    if 'cartas_adicionadas' not in st.session_state:
        st.session_state.cartas_adicionadas = []
    if 'interpretacao' not in st.session_state:
        st.session_state.interpretacao = None
    if 'pergunta' not in st.session_state:
        st.session_state.pergunta = ""
    
    # SIDEBAR - FUNDO PRETO
    with st.sidebar:
        st.markdown("<h2 style='color: white;'>🎴 SUAS CARTAS</h2>", unsafe_allow_html=True)
        st.markdown("---")
        
        # Progresso
        if st.session_state.cartas_adicionadas:
            st.markdown(f"""
            <div class="progresso-card" style="background: #1A1A1A; border-color: #333;">
                <div style="color: white; font-size: 14px;">CARTAS INSERIDAS</div>
                <div class="progresso-numero" style="color: #FFD700;">{len(st.session_state.cartas_adicionadas)}/3</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("<h3 style='color: white;'>📋 Tiragem Atual:</h3>", unsafe_allow_html=True)
            
            for i, carta_info in enumerate(st.session_state.cartas_adicionadas):
                orientacao_simbolo = "🔄" if carta_info['orientacao'] == 'invertida' else "⬆️"
                cor = "#FFD700" if carta_info['orientacao'] == 'invertida' else "white"
                nome_carta = carta_info['carta']['nome'] if 'carta' in carta_info and 'nome' in carta_info['carta'] else "Carta"
                st.markdown(f"""
                <div style='margin: 10px 0; padding: 10px; background: #1A1A1A; border-radius: 8px;'>
                    <span style='color: {cor}; font-weight: bold;'>{i+1}. {nome_carta} {orientacao_simbolo}</span><br>
                    <span style='color: #AAA; font-size: 12px;'>📍 {carta_info['posicao']}</span>
                </div>
                """, unsafe_allow_html=True)
        
        # Botão nova tiragem
        if st.button("🔄 NOVA TIRAGEM", use_container_width=True):
            st.session_state.cartas_adicionadas = []
            st.session_state.interpretacao = None
            st.session_state.pergunta = ""
            st.rerun()
        
        st.markdown("---")
        st.markdown("""
        <div style='color: #AAA; font-size: 12px; padding: 15px 0;'>
            <span style='color: #FFD700;'>Carl Gustav Jung</span><br>
            "Até que você torne consciente o inconsciente, ele dirigirá sua vida e você chamará isso de destino."
        </div>
        """, unsafe_allow_html=True)
    
    # ÁREA PRINCIPAL - FUNDO BRANCO
    col1, col2 = st.columns([2, 1])
    
    with col1:
        pergunta = st.text_area(
            "💭 **SUA PERGUNTA**",
            value=st.session_state.pergunta,
            placeholder="Ex: Como posso me realizar profissionalmente? O que meu coração busca no amor? Qual o próximo passo na minha jornada?",
            height=100
        )
        st.session_state.pergunta = pergunta
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if pergunta:
            st.markdown("""
            <div style='background: #F8F9FA; padding: 15px; border-radius: 8px; border-left: 4px solid #000;'>
                <span style='font-weight: 700;'>🎯 FOCO DA ANÁLISE</span><br>
                <span style='color: #495057;'>Sua pergunta guiará a interpretação junguiana</span>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("<h3>🃏 INSIRA SUAS 3 CARTAS NA ORDEM TIRADA</h3>", unsafe_allow_html=True)
    
    # Input das 3 cartas
    posicoes = ["PASSADO", "PRESENTE", "FUTURO"]
    
    for i, posicao in enumerate(posicoes):
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            nome_carta = st.text_input(
                f"{i+1}ª Carta - {posicao}",
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
            if st.button(f"✅ ADICIONAR", key=f"btn_adicionar_{i}"):
                if nome_carta:
                    valida, id_carta, carta = validar_carta(nome_carta)
                    
                    if valida:
                        posicao_existente = False
                        for c in st.session_state.cartas_adicionadas:
                            if c['posicao'] == posicao:
                                posicao_existente = True
                                break
                        
                        if not posicao_existente:
                            st.session_state.cartas_adicionadas.append({
                                'carta': carta.copy(),  # Usar copy() para evitar referências
                                'id': id_carta,
                                'orientacao': orientacao,
                                'posicao': posicao
                            })
                            
                            ordem = {"PASSADO": 0, "PRESENTE": 1, "FUTURO": 2}
                            st.session_state.cartas_adicionadas.sort(key=lambda x: ordem[x['posicao']])
                            
                            st.session_state[f"carta_nome_{i}_value"] = ""
                            st.success(f"✅ {carta['nome']} adicionada ao {posicao}")
                            st.rerun()
                        else:
                            st.warning(f"⚠️ {posicao} já tem uma carta")
                    else:
                        st.error(f"❌ Carta '{nome_carta}' não encontrada")
                        sugestoes = []
                        for id_c, carta_c in BARALHO_CIGANO.items():
                            if nome_carta.lower() in carta_c['nome'].lower():
                                sugestoes.append(carta_c['nome'])
                        if sugestoes:
                            st.info(f"💡 Você quis dizer: {', '.join(sugestoes[:3])}?")
                else:
                    st.warning("⚠️ Digite o nome da carta")
        
        st.markdown("---")
    
    # Exibir cartas e botão de interpretação
    if len(st.session_state.cartas_adicionadas) == 3:
        st.success("✅ Todas as 3 cartas foram inseridas com sucesso!")
        
        st.markdown("<h3>🃏 SUAS CARTAS</h3>", unsafe_allow_html=True)
        cols = st.columns(3)
        
        for idx, (col, carta_info) in enumerate(zip(cols, st.session_state.cartas_adicionadas)):
            with col:
                # Garantir que a carta está atualizada
                if 'id' in carta_info and carta_info['id'] in BARALHO_CIGANO:
                    carta_info['carta'] = BARALHO_CIGANO[carta_info['id']].copy()
                
                html_card = criar_card_carta(
                    carta_info['carta'],
                    carta_info['posicao'],
                    carta_info['orientacao']
                )
                st.markdown(html_card, unsafe_allow_html=True)
                
                # Mostrar arquétipo com função SEGURA
                arquitetura = obter_arquetipo_seguro(carta_info)
                st.markdown(f"""
                <div style='text-align: center; margin-top: 5px; font-size: 12px; color: #6C757D;'>
                    🏛 {arquitetura}
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("🔮 **ANÁLISE JUNGUIANA COMPLETA**", use_container_width=True, type="primary"):
                with st.spinner("🔮 Conectando com o inconsciente coletivo e sabedoria cigana..."):
                    # ATUALIZAR CARTAS ANTES DA INTERPRETAÇÃO
                    atualizar_cartas_session_state()
                    
                    interpretacao = interpretar_tiragem(
                        st.session_state.cartas_adicionadas,
                        st.session_state.pergunta
                    )
                    st.session_state.interpretacao = interpretacao
                    st.rerun()
    
    # Exibir interpretação
    if st.session_state.interpretacao:
        st.markdown("---")
        st.markdown("<h2 style='text-align: center;'>🔮 ANÁLISE DO BARALHO CIGANO</h2>", unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="interpretacao-box">', unsafe_allow_html=True)
            st.markdown(st.session_state.interpretacao)
            st.markdown('</div>', unsafe_allow_html=True)
            st.caption("🙏 O Baralho Cigano é um espelho da alma. O livre arbítrio é seu maior poder.")
        
        if st.button("🔄 NOVA CONSULTA", key="nova_consulta_fim"):
            st.session_state.cartas_adicionadas = []
            st.session_state.interpretacao = None
            st.session_state.pergunta = ""
            st.rerun()
    
    # Rodapé
    st.markdown("""
    <div class="rodape">
        <small>
        🔮 Baralho Cigano Tradicional • 36 Lâminas • Psicologia Analítica Junguiana<br>
        ⚡ Use seu baralho físico • Insira as cartas tiradas • Receba análise profunda<br>
        ✨ A sabedoria ancestral encontra a psicologia profunda
        </small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
