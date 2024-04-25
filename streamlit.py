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


okruhy_tab, obor_tab, poloha_tab, mapicky_tab = st.tabs(["Okruhy", "Podle oboru", "Podle státu", "Mapičky"])


with okruhy_tab:
    st.header("Počet uchazečů kombinovaného studia")
    okruhy_df = data[["OKRUH1", "OKRUH2"]].dropna()
    pivot_table = okruhy_df.pivot_table(
        index="OKRUH1", columns="OKRUH2", aggfunc=len, fill_value=0
    )
    pivot_table.index.name = "Okruh 1/Okruh 2"
    okruh1_counts = okruhy_df["OKRUH1"].value_counts()
    okruh2_counts = okruhy_df["OKRUH2"].value_counts()

    st.dataframe(pivot_table, use_container_width=True)

    fig_okruh1 = px.bar(okruh1_counts, x=okruh1_counts.index, y=okruh1_counts.values, color_discrete_sequence=["#007582"])
    fig_okruh2 = px.bar(okruh2_counts, x=okruh2_counts.index, y=okruh2_counts.values, color_discrete_sequence=["#007582"])
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

with obor_tab:
    st.header("Počet uchazečů dle oborů")
    with st.form(key="form"):
        col1, col2 = st.columns(2)
        obor = col1.selectbox("Vyberte obor", data["CZ_NAZEV"].unique())
        rok = col2.selectbox("Vyberte rok", ["Všechny"] + data["ROK_PR"].unique().tolist())
        
        not_cr = col1.checkbox("Zobrazit bez ČR")
        pouze_cr = col2.checkbox("Zobrazit pouze ČR")

        submit_button = st.form_submit_button(label="Zobrazit")
    
    if not_cr and pouze_cr:
        st.warning("Nelze zvolit obě možnosti zároveň.")
        st.stop()

    new_data = data[(data["CZ_NAZEV"] == obor)]
    if rok != "Všechny":
        new_data = new_data[(new_data["ROK_PR"] == rok)]

    stat = new_data["STAT_BYDLISTE"].value_counts()
    if not_cr:
        stat = new_data.loc[new_data["STAT_BYDLISTE"] != "Česká republika"][
            "STAT_BYDLISTE"
        ].value_counts()
    
    if pouze_cr:
        stat = new_data.loc[new_data["STAT_BYDLISTE"] == "Česká republika"][
            "STAT_BYDLISTE"
        ].value_counts()

    if stat.empty:
        st.warning("Žádná data pro zvolené parametry.")
    else:
        col1, col2 = st.columns(2)
        
        if not pouze_cr:
            fig = px.bar(stat, x=stat.index, y=stat.values, color_discrete_sequence=["#007582"])
            pie = px.pie(stat, values=stat.values, names=stat.index, color_discrete_sequence=["#007582", "#FFD700", "#87CEEB", "#50C878", "#FFDAB9"])


            col1.plotly_chart(fig)
            col2.plotly_chart(pie)

        vzdelani = new_data["stupen_vzdelani"].value_counts()
        vzdelani_fig = px.bar(
            vzdelani,
            x=vzdelani.index,
            y=vzdelani.values,
            labels={"x": "Stupeň vzdělání", "y": "Počet uchazečů"},
            title="Počet uchazečů dle stupně vzdělání",
            color_discrete_sequence=["#007582", "#FFD700", "#87CEEB", "#50C878", "#FFDAB9"]
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
            color_discrete_sequence=["#007582", "#FFD700", "#87CEEB", "#50C878", "#FFDAB9"]
        )

        col2.plotly_chart(kolo_fig)
        
        st.write("Mapy")

with poloha_tab:
    st.header("Počet uchazečů dle bydliště (bez ČR)")
    staty_bez_cr = data.loc[(data["STAT_BYDLISTE"] != "Česká republika")]

    with st.form(key="form2"):
        col1, col2 = st.columns(2)
        poloha = col1.selectbox("Vyberte filtr", staty_bez_cr["STAT_BYDLISTE"].unique())
        rok = col2.selectbox("Vyberte rok", data["ROK_PR"].unique())

        submit_button = st.form_submit_button(label="Zobrazit")

    staty_df = staty_bez_cr[(staty_bez_cr["STAT_BYDLISTE"] == poloha) & (staty_bez_cr["ROK_PR"] == rok)]
    
    if staty_df.empty:
        st.warning("Žádná data pro zvolené parametry.")
    
    else:
        obory = staty_df["CZ_NAZEV"].value_counts()
        
        fig_obory = px.bar(
            obory,
            x=obory.index,
            y=obory.values,
            labels={"x": "Obor", "y": "Počet uchazečů"},
            color_discrete_sequence=["#007582", "#FFD700", "#87CEEB", "#50C878", "#FFDAB9"],
        )
        
        st.plotly_chart(fig_obory, use_container_width=True)
        
with mapicky_tab:
    st.header("Mapičky")
    st.write("Tady budou mapičky")
    
    gdf = gpd.read_file("./vendor/geo-countries/data/countries.geojson")