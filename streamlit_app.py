import altair as alt
import pandas as pd
import streamlit as st
import vega_datasets
from vega_datasets import data
import country_converter as coco
cc = coco.CountryConverter()


@st.cache_data
def load_data():

    df = pd.read_csv("https://raw.githubusercontent.com/zoe-love/BMI-706-Project/main/wash_data_cleaned.csv")

    return df

df = load_data()

### TITLE ###
st.write("## Global Water, Hygeine, and Sanitation Data")

# Year selection Slider

year = st.select_slider(
    label = "Year Select",
    options = df['year'].unique().tolist())
subset = df[df["year"] == year]

# Type of covereage selection 
st.dataframe(df)

type = st.radio(
    label = 'Measure Type',
    options = subset['measure'].unique().tolist())
subset = subset[subset["measure"] == type]


# Country selection

country = st.selectbox(label = 'Country Select', 
    options = subset['name'].unique().tolist())
subset = subset[subset["name"] == country]

# create line chart dataframe based on measure
if type == 'wat':
  line_df = df[(df['measure']== type) & (df['name'] == country)]
elif type == 'hyg':
  line_df = df[(df['measure']== type) & (df['name'] == country)]
else:
  line_df = df[(df['measure']== type) & (df['name'] == country)]

### Chart 1 ###
brush = alt.selection_interval( encodings=['x'])

selection = alt.selection_multi(fields=['level_1'], bind='legend')

upper = alt.Chart(line_df).mark_line(point=True).encode(
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

country_bar = alt.Chart(line_df).mark_bar().encode(
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

st.altair_chart(chart1, use_container_width=True)

