import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="TZR — Sam Brady",
    page_icon="🟠",
    layout="wide"
)

# Remove Streamlit default padding and hide header/footer
st.markdown("""
<style>
    #MainMenu, header, footer {visibility: hidden;}
    .block-container {padding: 0 !important; max-width: 100% !important;}
    iframe {border: none;}
</style>
""", unsafe_allow_html=True)

with open("tzr_sam_dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

components.html(html, height=4200, scrolling=True)
