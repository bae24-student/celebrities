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
    fig, ax = plt.figure(figsize=(13, 7))
    sns.barplot(data=df_categories, x="avg(Earnings)", y="Category", orient="h",
                order=df_categories.sort_values("avg(Earnings)", ascending=False)["Category"], ax=ax)
    plt.title("Average Yearly Earnings", fontsize=16)
    plt.xlabel("Earnings (in USD millions)")
    plt.tight_layout()
    st.pyplot(fig)
