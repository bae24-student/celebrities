import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
import json
from shapely.geometry import Polygon
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns

with st.echo(code_location='below'):
    st.header('Top-100 Highest-Paid Celebrities 2020')
    @st.cache(allow_output_mutation=True)
    def get_data(url):
        return pd.read_csv(url)

    df_100_celeb = get_data("Top_100_celebrities_2020.csv").set_index("rank")
    df_celeb_states = get_data("Celebrities_and_states.csv")
    df_categories = get_data("Top Celebrities 2015-2020.csv")
    df_celebs = get_data("https://storage.googleapis.com/kagglesdsdata/datasets/622168/2148774/forbes_celebrity_100.csv?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=gcp-kaggle-com%40kaggle-161607.iam.gserviceaccount.com%2F20220613%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20220613T173354Z&X-Goog-Expires=259199&X-Goog-SignedHeaders=host&X-Goog-Signature=081f50da11f1107eeb7d72c6ffdb965d40d488dcbe462f54f7a6d77d380640b6d5d8ee35d3dd4ec167daf8d4c0b145941f4af23c7771f89cc31127fba81699637448dcaf1b9c7a31976ffe14c80d9c4f78111bd7779b5cff014ba3c4fa1d50993c24d11c20246caa612c23263934b8227633f3fe9d75f9a4a3295ba9ab9f0506463c0d7f40b647df5c17420514a314ee0e149aa778b1fd0fedc9c0e2e6f39dd5fd3c81099aada8556889aaf78b1a02cf34900d3220c6befe7b75f575d5e15c6e81de7dddc088de91eb76d00d776ae3afe70e51d18711d0f9fa7c9683f05128f2841578d5cf1881e4ee447cc1d9bf95c9d89b8ec73ccbd9d64ece85f267dcaede")
    st.dataframe(df_100_celeb[['name', 'earnings']])

    with open('us_states.json', encoding='utf-8') as f:
        a = json.load(f)
    geo_data = []

    for i in range(0, 50):
        try:
            poly = Polygon(a['features'][i]['geometry']['coordinates'][0][0])
            geo_data.append({'name': a['features'][i]['properties']['name'], 'poly': poly})
        except TypeError:
            poly = Polygon(a['features'][i]['geometry']['coordinates'][0])
            geo_data.append({'name': a['features'][i]['properties']['name'], 'poly': poly})
    df_geo = pd.DataFrame(geo_data)
    df_geo_celeb = df_geo.merge(df_celeb_states, left_on='name', right_on='state', how='left').fillna(0.0)
    gdf = gpd.GeoDataFrame(df_geo_celeb, geometry='poly')

    pickup_counts = gdf["name_x"].value_counts()
    fig, ax = plt.subplots(figsize=(10, 10))
    gdf.set_index("name_x").assign(pickup_counts=pickup_counts).plot(
        column="pickup_counts", ax=ax, legend=True)
    st.pyplot(fig)

    option = st.selectbox(
        'Choose a celebrity',
        (df_100_celeb.set_index("name").drop(["BTS", "Kiss"]).reset_index()['name']))

    pd.set_option('max_colwidth', 200)
    image_url = df_100_celeb.loc[df_100_celeb['name'] == option, 'image'].to_string().split()[2]
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content))
    st.image(image)

    name = option
    api_url = 'https://api.api-ninjas.com/v1/celebrity?name={}'.format(name)
    r = requests.get(api_url, headers={'X-Api-Key': '2UE2iYcUN7olu1U3zszpLQ==odzAs4dPV2STYaUF'})
    celeb_info = pd.DataFrame(r.json())
    st.dataframe(celeb_info)

    st.header("Highest-Paid Celebrities 2005-2020")
    df_celebs.rename(columns={"Pay (USD millions)": "Earnings"}, inplace=True)
    top_celebs = df_celebs.groupby("Name").agg(earning=("Earnings","sum"),
                      category=("Category","first"),avg_earning=("Earnings","mean")).sort_values("earning",ascending=False)[:16]
    fig, ax = plt.subplots(figsize=(13,7))
    sns.barplot(data=top_celebs, x="earning", y=top_celebs.index, orient="h")
    plt.xlabel("Earnings (in USD Millions)")
    plt.title("Top-15 Highest-Paid Celebrities 2005-2020",fontsize=16)
    plt.ylabel(None)
    st.pyplot(fig)
    
    fig, ax = plt.subplots(figsize=(13, 7))
    sns.barplot(data=df_categories, x="avg(Earnings)", y="Category", orient="h",
                order=df_categories.sort_values("avg(Earnings)", ascending=False)["Category"], ax=ax)
    plt.title("Average Yearly Earnings", fontsize=16)
    plt.xlabel("Earnings (in USD millions)")
    plt.tight_layout()
    st.pyplot(fig)
   
