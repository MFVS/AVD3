import streamlit as st
import pandas as pd
import plotly.express as px


data = pd.read_csv("data/uchazeci_transformed.csv")

st.set_page_config(
    page_title="Uchazeči UJEP PŘF",
    page_icon=":school:",
    layout="wide",
)

st.title("Uchazeči UJEP PŘF")

obor_tab, poloha_tab = st.tabs(["Obor", "Poloha"])

with obor_tab:
    obor = st.selectbox("Vyber obor", data["CZ_NAZEV"].unique())

    new_data = data[data["CZ_NAZEV"] == obor]

    st.dataframe(new_data)

    stat = new_data["STAT_BYDLISTE"].value_counts()
    ciz_stat = new_data.loc[new_data["STAT_BYDLISTE"] != "Česká republika"][
        "STAT_BYDLISTE"
    ].value_counts()

    fig = px.bar(stat, x=stat.index, y=stat.values)
    pie = px.pie(ciz_stat, values=ciz_stat.values, names=ciz_stat.index)

    col1, col2 = st.columns(2)

    col1.plotly_chart(fig)
    col2.plotly_chart(pie)


    vzdelani = new_data["stupen_vzdelani"].value_counts()
    vzdelani_fig = px.bar(
        vzdelani,
        x=vzdelani.index,
        y=vzdelani.values,
        labels={"x": "Stupeň vzdělání", "y": "Počet uchazečů"},
        title="Počet uchazečů dle stupně vzdělání",
    )
    vzdelani_fig.update_layout(xaxis=dict(tickmode="array", tickvals=[], ticktext=[]))


    st.plotly_chart(vzdelani_fig)


    kolo = new_data["KOLO_PRIHLASKY"].value_counts()

    kolo_fig = px.bar(
        kolo,
        x=kolo.index,
        y=kolo.values,
        labels={"x": "Kolo přihlášky", "y": "Počet uchazečů"},
        title="Počet uchazečů dle kola přihlášky",
    )

    st.plotly_chart(kolo_fig)
