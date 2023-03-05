import altair as alt
import pandas as pd
import streamlit as st
import vega_datasets
from vega_datasets import data
import country_converter as coco
cc = coco.CountryConverter()


@st.cache
def load_data():

    df = pd.read_csv("https://github.com/zoe-love/BMI-706-Project/blob/main/wash_data_cleaned.csv.zip")
    
    # remove country without numeric code (Channel Islands)
    df = df[df['iso3'] != 'CHI']

    # add numeric country codes
    df['country-code'] = coco.convert(names = df['iso3'], to='ISOnumeric')

    return df

df = load_data()

### P1.2 ###


st.write("## Global Water, Hygeine, and Sanitation Data")

# Year selection Slider

year = st.slider(label = "Year Select", min_value = 2000, max_value = 2020, value = 2012)
subset = df[df["year"] == year]

### P2.3 ###
# replace with st.multiselect
# (hint: can use current hard-coded values below as as `default` for selector)
countries = st.multiselect(label = 'Country Select', 
    options = ["Austria",
        "Germany",
        "Iceland",
        "Spain",
        "Sweden",
        "Thailand",
        "Turkey"], 
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


# Modify coverage type
coverage_type = st.selectbox(label ="Converage Type", 
        options = ['wat', 'hyg', 'san'], index = 0)
subset = subset[subset["measure"] == coverage_type]


chart = alt.Chart(subset).mark_rect().encode(
    x=alt.X("Age", sort=ages),
    y=alt.Y("Country:N"),
    color=alt.Color("Rate", scale = alt.Scale(clamp=True, domain=[0.01, 1000], type="log")),
    tooltip=["Rate:Q"],
).properties(
    title=f"{cancer} mortality rates for {'males' if sex == 'M' else 'females'} in {year}",
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
