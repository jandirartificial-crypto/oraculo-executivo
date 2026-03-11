# app.py (seu arquivo principal)

import streamlit as st
from terapeuta_digital import show_terapeuta_digital
# ... seus outros imports ...

# Configuração da página
st.set_page_config(layout="wide", page_title="Seu App")

# ... suas outras abas (ex: Tarot, Baralho Cigano) ...

# Criando as abas
aba1, aba2, aba3 = st.tabs(["🔮 Tarot", "🃏 Baralho Cigano", "🧘 Terapeuta Digital"])

with aba1:
    # ... seu código do tarot ...
    pass

with aba2:
    # ... seu código do baralho cigano ...
    pass

with aba3:
    # CHAMADA PARA O NOVO MÓDULO
    show_terapeuta_digital()
