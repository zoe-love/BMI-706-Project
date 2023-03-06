import altair as alt
import pandas as pd
import streamlit as st
import vega_datasets
from vega_datasets import data
import country_converter as coco
cc = coco.CountryConverter()


@st.cache
def load_data():

    df = pd.read_csv("https://raw.githubusercontent.com/zoe-love/BMI-706-Project/main/wash_data_cleaned.csv")

    return df

df = load_data()

### TITLE ###
st.write("## Global Water, Hygeine, and Sanitation Data")

# Year selection Slider

year = st.slider(
    label = "Year Select",
    min_value = int(df['year'].min()),
    max_value = int(df['year'].max()),
    value = 2012,
    step = 1)
subset = df[df["year"] == year]

# Type of covereage selection 

type = st.radio(
    label = 'Measure Type',
    options = ['wat', 'hyg', 'san']
)
subset = subset[subset["measure"] == type]

# Country selection

countries = st.selectbox(label = 'Country Select', 
    options = subset['name'].unique().tolist())
subset = subset[subset["name"] == countries]

# set levels for bar chart based on measure
wat_levels = ['bas', 'lim', 'unimp', 'sur']
hyg_levels = ['bas', 'lim', 'nfac']
san_levels = ['bas', 'lim', 'sew_c', 'sep', 'lat', 'unimp', 'od']

if type == 'wat':
  levels = wat_levels
elif type == 'hyg':
  levels = hyg_levels
else:
  levels = san_levels

# Global overview = subset_wide
subset_wide = pd.pivot_table(subset, values = 'coverage', index = ['name', 'year', 'pop_n', "iso3", 'country-code'], columns = ['measure', 'level_1']).reset_index()
subset_wide.columns = [' '.join(col).strip() for col in subset_wide.columns.values]

# set wide levels
levels_wide = [(type + " ") + i for i in levels]


### Chart 1 ###
brush = alt.selection_interval( encodings=['x'])

selection = alt.selection_multi(fields=['level_1'], bind='legend')

upper = alt.Chart(subset).mark_line(point=True).encode(
    x='year:O',
    y='coverage:Q',
    color='level_1:N',
    opacity=alt.condition(selection, alt.value(1), alt.value(0.2))
).transform_filter(
    brush
).properties(
    width=550
).add_selection(
    selection
)

country_bar = alt.Chart(subset).mark_bar().encode(
    x='year:O',
    y='coverage:Q',
    color='level_1:N',
    opacity=alt.condition(selection, alt.value(1), alt.value(0.2))
).add_selection(
    brush
).properties(
    width=550
).add_selection(
    selection
)

chart1 = upper & country_bar
chart1

st.altair_chart(chart1, use_container_width=True)

countries_in_subset = subset["name"].unique()
if len(countries_in_subset) != len(countries):
    if len(countries_in_subset) == 0:
        st.write("No data avaiable for given subset.")
    else:
        missing = set(countries) - set(countries_in_subset)
        st.write("No data available for " + ", ".join(missing) + ".")
