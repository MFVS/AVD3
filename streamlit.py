import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
import folium


data = pd.read_csv("data/uchazeci_transformed.csv")

st.set_page_config(
    page_title="Uchazeči UJEP PŘF",
    page_icon=":school:",
    layout="wide",
)

st.title("Uchazeči UJEP PŘF")


okruhy_tab, obor_tab, poloha_tab, mapicky_tab = st.tabs(["Okruhy", "Podle oboru", "Cizí státy", "Mapičky"])


with okruhy_tab:
    st.header("Počet uchazečů kombinovaného studia")
    okruhy_df = data[["OKRUH1", "OKRUH2"]].dropna()
    pivot_table = okruhy_df.pivot_table(
        index="OKRUH1", columns="OKRUH2", aggfunc=len, fill_value=0
    )
    okruh1_counts = okruhy_df["OKRUH1"].value_counts()
    okruh2_counts = okruhy_df["OKRUH2"].value_counts()
    
    st.table(pivot_table)
    
    fig_okruh1 = px.bar(okruh1_counts, x=okruh1_counts.index, y=okruh1_counts.values)
    fig_okruh2 = px.bar(okruh2_counts, x=okruh2_counts.index, y=okruh2_counts.values)
    st.subheader("Okruhy 1")
    
    col1, col2, col3 = st.columns([3, 1, 1])
    
    col1.plotly_chart(fig_okruh1, use_container_width=True)
    
    head1 = okruh1_counts.head(5)
    for index, value in head1.items():
        col2.metric("Okruh", index)
        col3.metric("Počet", value)
    # col2.metric("Okruh", okruh1_counts.idxmax())
    # col2.metric("Počet", okruh1_counts.max())
    
    st.divider()
    st.subheader("Okruhy 2")
    
    col1, col2, col3 = st.columns([3, 1, 1])
    
    col1.plotly_chart(fig_okruh2, use_container_width=True)
    
    head2 = okruh2_counts.head(5)
    for index, value in head2.items():
        col2.metric("Okruh", index)
        col3.metric("Počet", value)
    # col2.subheader("Nejčastější okruhy 2")
    # col2.metric("Okruh", okruh2_counts.idxmax())
    # col2.metric("Počet", okruh2_counts.max())

with obor_tab:
    st.header("Počet uchazečů dle oborů")
    with st.form(key="form"):
        col1, col2 = st.columns(2)
        obor = col1.selectbox("Vyberte obor", data["CZ_NAZEV"].unique())
        rok = col2.selectbox("Vyberte rok", data["ROK_PR"].unique())

        submit_button = st.form_submit_button(label="Zobrazit")

    new_data = data[(data["CZ_NAZEV"] == obor) & (data["ROK_PR"] == rok)]

    if new_data.empty:
        st.warning("Nenalezeny žádné záznamy")
    else:

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


        col1.plotly_chart(vzdelani_fig)


        kolo = new_data["KOLO_PRIHLASKY"].value_counts()

        kolo_fig = px.bar(
            kolo,
            x=kolo.index,
            y=kolo.values,
            labels={"x": "Kolo přihlášky", "y": "Počet uchazečů"},
            title="Počet uchazečů dle kola přihlášky",
        )

        col2.plotly_chart(kolo_fig)

with poloha_tab:
    st.header("Počet uchazečů dle bydliště (bez ČR)")
    staty_bez_cr = data.loc[(data["STAT_BYDLISTE"] != "Česká republika")]
    
    with st.form(key="form2"):
        col1, col2 = st.columns(2)
        poloha = col1.selectbox("Vyberte filtr", staty_bez_cr["STAT_BYDLISTE"].unique())
        rok = col2.selectbox("Vyberte rok", data["ROK_PR"].unique())
        
        submit_button = st.form_submit_button(label="Zobrazit")

    staty_bez_cr = data.loc[(data["STAT_OBCANSTVI"] != "Česká republika") & (data["ROK_PR"] == rok)]
    st.write(staty_bez_cr)
    staty_counts = staty_bez_cr["STAT_OBCANSTVI"].value_counts()
    obory_counts = staty_bez_cr["PR_NAZEV"].value_counts()
    
    st.write(staty_counts)
    st.write(obory_counts)
    
    fig = px.bar(staty_counts, x=staty_counts.index, y=staty_counts.values)
    st.plotly_chart(fig, use_container_width=True)
    
    st.header("Počet uchazečů dle oborů")
    fig = px.bar(obory_counts, x=obory_counts.index, y=obory_counts.values)
    st.plotly_chart(fig, use_container_width=True)


with mapicky_tab:
    st.header("Mapičky")
    st.write("Tady budou mapičky")
    
    gdf = gpd.read_file("./vendor/geo-countries/data/countries.geojson")