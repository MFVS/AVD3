import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
import folium


data = pd.read_csv("data/uchazeci_transformed.csv")
colors = ["#007582", "#FFD700", "#87CEEB", "#50C878", "#FFDAB9"]

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

    fig_okruh1 = px.bar(okruh1_counts, x=okruh1_counts.index, y=okruh1_counts.values, color_discrete_sequence=colors)
    fig_okruh1.update_layout(showlegend=False)
    fig_okruh2 = px.bar(okruh2_counts, x=okruh2_counts.index, y=okruh2_counts.values, color_discrete_sequence=colors)
    fig_okruh2.update_layout(showlegend=False)

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
        rok = col2.selectbox("Vyberte rok", ["Vše"] + data["ROK_PR"].unique().tolist())
        
        not_cr = col1.checkbox("Zobrazit bez ČR")
        pouze_cr = col2.checkbox("Zobrazit pouze ČR")

        submit_button = st.form_submit_button(label="Zobrazit")
    
    if not_cr and pouze_cr:
        st.warning("Nelze zvolit obě možnosti zároveň.")
        st.stop()

    new_data = data[(data["CZ_NAZEV"] == obor)]
    if rok != "Vše":
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
        
        if not pouze_cr:
            fig = px.bar(stat, x=stat.index, y=stat.values,color=stat.index, color_discrete_sequence=colors)
            pie = px.pie(stat, values=stat.values, names=stat.index, color_discrete_sequence=colors)

            if len(stat) == 1:
                st.info("Uchazeči pouze z jednoho státu. " + stat.index[0])
                st.metric("Počet uchazečů", stat.values[0])
            else:
                sloupce_tab, kolace_tab = st.tabs(["Sloupcový", "Koláčový"])
                
                with sloupce_tab:
                    st.plotly_chart(fig, use_container_width=True)
                with kolace_tab:
                    st.plotly_chart(pie, use_container_width=True)
        
        col1, col2 = st.columns(2)

        vzdelani = new_data["stupen_vzdelani"].value_counts()
        vzdelani_fig = px.bar(
            vzdelani,
            x=vzdelani.index,
            y=vzdelani.values,
            labels={"x": "Stupeň vzdělání", "y": "Počet uchazečů"},
            title="Počet uchazečů dle stupně vzdělání",
            color_discrete_sequence=colors
        )
        vzdelani_fig.update_layout(xaxis=dict(tickmode="array", tickvals=[], ticktext=[]))

        col1.plotly_chart(vzdelani_fig)

        kolo = new_data["KOLO_PRIHLASKY"].value_counts()

        kolo_fig = px.bar(
            kolo,
            x=kolo.index,
            y=kolo.values,
            labels={"KOLO_PRIHLASKY": "Kolo přihlášky", "y": "Počet uchazečů"},
            title="Počet uchazečů dle kola přihlášky",
            color_discrete_sequence=colors
        )
        kolo_fig.update_layout(xaxis=dict(tickmode="linear", tickvals=[1, 2], ticktext=["1. kolo", "2. kolo"]))

        col2.plotly_chart(kolo_fig, use_container_width=True)
        
        st.write("Mapy")

with poloha_tab:
    st.header("Počet uchazečů dle bydliště (bez ČR)")
    staty_df = data.loc[(data["STAT_BYDLISTE"] != "Česká republika")]

    with st.form(key="form2"):
        col1, col2 = st.columns(2)
        poloha = col1.selectbox("Vyberte bzdliště", ["Vše"] + staty_df["STAT_BYDLISTE"].unique().tolist())
        rok = col2.selectbox("Vyberte rok", ["Vše"] + data["ROK_PR"].unique().tolist())

        submit_button = st.form_submit_button(label="Zobrazit")

    if poloha != "Vše":
        staty_df = staty_df[(staty_df["STAT_BYDLISTE"] == poloha)]
    if rok != "Vše":
        staty_df = staty_df[(staty_df["ROK_PR"] == rok)]
    
    if staty_df.empty:
        st.warning("Žádná data pro zvolené parametry.")
    
    else:
        col1, col2 = st.columns(2)
        
        col1.metric("Celkový počet uchazečů", staty_df.shape[0])
        
        obory = staty_df["CZ_NAZEV"].value_counts()
        
        bars_tab, pie_tab = st.tabs(["Sloupcový", "Koláčový"])
        with bars_tab:
            fig_obory = px.bar(
                obory,
                x=obory.index,
                y=obory.values,
                labels={"CZ_NAZEV": "Obor", "y": "Počet uchazečů"},
                color=obory.index,
                color_discrete_sequence=colors,
            )
            fig_obory.update_layout(showlegend=False)
            
            st.plotly_chart(fig_obory, use_container_width=True)
        with pie_tab:
            fig_obory_pie = px.pie(
                obory,
                values=obory.values,
                names=obory.index,
                color_discrete_sequence=colors
            )
            st.plotly_chart(fig_obory_pie, use_container_width=True)
        
with mapicky_tab:
    st.header("Mapičky")
    st.write("Tady budou mapičky")
    
    gdf = gpd.read_file("./vendor/geo-countries/data/countries.geojson")