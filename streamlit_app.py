import altair as alt
import pandas as pd
import streamlit as st
import vega_datasets
from vega_datasets import data
import country_converter as coco
cc = coco.CountryConverter()


@st.cache
def load_data():

    df = pd.read_csv("https://github.com/zoe-love/BMI-706-Project/blob/main/wash_data_cleaned.csv.zip?raw=true", compression = 'zip')

    
    # remove country without numeric code (Channel Islands)
    df = df[df['iso3'] != 'CHI']

    # add numeric country codes
    df['country-code'] = coco.convert(names = df['iso3'], to='ISOnumeric')

    return df

df = load_data()

### P1.2 ###


st.write("## Global Water, Hygeine, and Sanitation Data")

# Year selection Slider

year = st.slider(label = "Year Select", min_value = df['year'].min(), max_value = df['year'].max(), value = 2012)
subset = df[df["year"] == year]

# Type of covereage selection 
measure = st.radio(
    label = 'Measure Type',
    options = subset['measure'].unique().tolist()
)
subset = subset[subset["measure"] == measure]

# Country selection
countries = st.multiselect(label = 'Country Select', 
    options = subset['name'].unique().tolist(), 
    default = [
        "Austria",
        "Germany",
        "Iceland",
        "Spain",
        "Sweden",
        "Thailand",
        "Turkey",
]
)
subset = subset[subset["name"].isin(countries)]


chart = alt.Chart(alt.topo_feature(data.world_110m.url, 'countries')).mark_geoshape(
    stroke='#aaa', strokeWidth=0.25
).transform_lookup(
    lookup='id', from_=alt.LookupData(data=df, key='country-code', fields=['coverage'])
).encode(
    color = 'coverage:Q',
    tooltip = alt.Tooltip('pop_n:Q')
).project(
    type='equirectangular'
).properties(
    width=900,
    height=500
).configure_view(
    stroke=None
)
### P2.5 ###

st.altair_chart(chart, use_container_width=True)

countries_in_subset = subset["Country"].unique()
if len(countries_in_subset) != len(countries):
    if len(countries_in_subset) == 0:
        st.write("No data avaiable for given subset.")
    else:
        missing = set(countries) - set(countries_in_subset)
        st.write("No data available for " + ", ".join(missing) + ".")
