import streamlit as st
st.set_page_config(
    page_title="Uchazeči UJEP PŘF",
    page_icon=":school:",
    layout="wide",
)
from mapicky import mapa_mest, mapa_staty
from streamlit_folium import st_folium


def mapa_mest_cached():
    return mapa_mest()

def mapa_staty_cached():
    return mapa_staty()

mesta_folium = mapa_mest_cached()
staty_folium = mapa_staty_cached()

st_folium(mesta_folium, return_on_hover=False)
st_folium(staty_folium, return_on_hover=False)
st.stop()
# st.map(mapa_mest())