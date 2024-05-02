import polars as pl
import geopandas as gpd
import folium
import streamlit as st


@st.cache_resource
def get_gdf_countries():
    geojson_filepath = "./vendor/geo-countries/data/countries.geojson"
    gdf = gpd.read_file(geojson_filepath, engine='fiona')
    # gdf.geometry.set_crs('EPSG:4326', inplace=True)
    return gdf

@st.cache_resource
def get_gdf_obce():
    geojson_filepath = "./vendor/obce-transformed.geojson"
    gdf = gpd.read_file(geojson_filepath, engine='fiona')
    # gdf.geometry.set_crs('EPSG:4326', inplace=True)
    return gdf

def mapa_staty():
    country_codes_df = pl.read_csv('data/country_codes.csv')
    df_uchazeci = pl.read_csv("data/prf_uchazeci.csv").join(other=country_codes_df, left_on="STAT_OBCANSTVI", right_on="country_name", how="left")
    gdf = get_gdf_countries()
    # Filter the GeoDataFrame based on the ISO_A3 value
    stat = df_uchazeci.select("STAT_OBCANSTVI")
    joined_df = stat.join(other=country_codes_df, left_on="STAT_OBCANSTVI", right_on="country_name", how="left")
    joined_df = joined_df.group_by("ISO3166-1-Alpha-3").agg(pl.count("STAT_OBCANSTVI").alias("count"))
    m = folium.Map()
    # Add a text label with a value to the centroid of the selected feature
    for row in joined_df.iter_rows(named=True):
        obec = row["ISO3166-1-Alpha-3"]
        print(obec)
        if obec is None:
            continue
        count = row["count"]
        selected_feature = gdf[gdf['ISO_A3'] == obec]
        folium.GeoJson(selected_feature).add_to(m)
        folium.Marker(
            location=[selected_feature['geometry'].centroid.y.values[0], selected_feature['geometry'].centroid.x.values[0]],
            icon=folium.DivIcon(html=f'<div style="font-size: 11pt; color: black;">{obec}:{count}</div>')
        ).add_to(m)
    return m

def mapa_mest():
    country_codes_df = pl.scan_csv('data/country_codes.csv')
    df_uchazeci = pl.scan_csv("data/prf_uchazeci.csv").join(other=country_codes_df, left_on="STAT_OBCANSTVI", right_on="country_name", how="left")
    df_cz_uchazeci = df_uchazeci.filter(pl.col("ISO3166-1-Alpha-3") == "CZE")
    places_df = pl.scan_csv("data/places.csv")
    df_cz_uchazeci = df_cz_uchazeci.join(other=places_df, how="left", right_on="obec_name", left_on="OBEC_BYDLISTE")
    gdf_obce = get_gdf_obce()
    grouped = df_cz_uchazeci.group_by("obec_id").agg(
        pl.col("OBEC_BYDLISTE").unique().alias("obce"),
        pl.col("OBEC_BYDLISTE").n_unique().alias("#obci"),
        pl.col("OBEC_BYDLISTE").sample().first().alias("obec"),
        pl.col("PSC_BYDL").sample().first().alias("PSC_BYDL"),
        pl.count("obec_id").alias("count")
    )
    grouped = grouped.with_columns((pl.col("obce").list.len() == pl.lit(1)).alias("valid")).collect()

    assert grouped.filter(pl.col("valid").not_()).__len__() == 0
    m = folium.Map(tiles='cartodbpositron', location=[50.073658, 14.418540], zoom_start=8)
    not_found_count = 0
    for row in grouped.iter_rows(named=True):
        print(row)
        obec = row.get("obec_id")
        count = row["count"]
        selected_feature = gdf_obce[gdf_obce['id'] == str(obec)]
        if selected_feature is None or len(selected_feature) == 0:
            not_found_count += 1
            print(f"Not found: {obec}")
            continue
        folium.GeoJson(selected_feature).add_to(m)

        folium.Marker(
            location=[selected_feature['geometry'].centroid.y.values[0], selected_feature['geometry'].centroid.x.values[0]],
            icon=folium.DivIcon(html=f'<div style="font-size: 9pt; color: black; font-family: monospace;">{count}</div>')
        ).add_to(m)
    return m