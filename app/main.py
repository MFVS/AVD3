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

# tabs obecny prehled (nejake filtrace)

with obor_tab:
    col1, col2 = st.columns(2)
    okruhy_df = data[["OKRUH1", "OKRUH2"]].dropna()
    pivot_table = okruhy_df.pivot_table(
        index="OKRUH1", columns="OKRUH2", aggfunc=len, fill_value=0
    )
    okruh1_counts = okruhy_df["OKRUH1"].value_counts()
    okruh2_counts = okruhy_df["OKRUH2"].value_counts()
    
    col1.table(pivot_table)
    # col1.dataframe(pivot_table)
    
    fig_okruh1 = px.bar(okruh1_counts, x=okruh1_counts.index, y=okruh1_counts.values, title="OKRUH 1")
    fig_okruh2 = px.bar(okruh2_counts, x=okruh2_counts.index, y=okruh2_counts.values, title="OKRUH 2")
    
    col2.plotly_chart(fig_okruh1)
    col2.plotly_chart(fig_okruh2)
    
    
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

with poloha_tab:
    col1, col2 = st.columns(2)
    poloha = col1.selectbox("Vyberte filtr", ["Stát"])
    rok = col2.selectbox("Vyberte rok", data["ROK_PR"].unique())

    match poloha:
        case "Stát":
            staty_bez_cr = data.loc[(data["STAT_OBCANSTVI"] != "Česká republika") & (data["ROK_PR"] == rok)]
            staty_counts = staty_bez_cr["STAT_OBCANSTVI"].value_counts()
            obory_counts = staty_bez_cr["PR_NAZEV"].value_counts()
            
            st.header("Počet uchazečů dle občanství (bez ČR)")
            fig = px.bar(staty_counts, x=staty_counts.index, y=staty_counts.values)
            st.plotly_chart(fig, use_container_width=True)
            
            st.header("Počet uchazečů dle oborů")
            fig = px.bar(obory_counts, x=obory_counts.index, y=obory_counts.values)
            st.plotly_chart(fig, use_container_width=True)
