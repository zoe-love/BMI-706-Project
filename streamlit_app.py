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
st.write("## Global Water, Hygiene, and Sanitation Data")

# Year selection Slider

year = st.select_slider(
    label = "Year Select",
    options = df['year'].unique().tolist())
subset = df[df["year"] == year]

# Type of covereage selection 
#st.dataframe(df)

type = st.radio(
    label = 'Measure Type',
    options = subset['measure'].unique().tolist())
subset = subset[subset["measure"] == type]

# Global overview = subset_wide
subset_wide = pd.pivot_table(subset, values = 'coverage', index = ['name', 'year', 'pop_n', "iso3", 'country-code'], columns = ['measure', 'level_1']).reset_index()
subset_wide.columns = [' '.join(col).strip() for col in subset_wide.columns.values]
if type == 'san':
  subset_wide = subset_wide.drop(columns = ['san lat', 'san sep', 'san sew_c'])
else:
  subset_wide = subset_wide


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

# set levels for bar chart based on measure
wat_levels = ['bas', 'lim', 'unimp', 'sur']
hyg_levels = ['bas', 'lim', 'nfac']
san_levels = ['bas', 'lim', 'unimp', 'od']

if type == 'wat':
  levels = wat_levels
elif type == 'hyg':
  levels = hyg_levels
else:
  levels = san_levels



# set wide levels
levels_wide = [(type + " ") + i for i in levels]

### Chart 1 ###
global_base = alt.Chart(subset_wide).properties(
    width=550
)


global_chart = global_base.transform_fold(
  levels_wide,
  as_=['column', 'value']
).mark_bar().encode(
  x=alt.X('name:O',title='Countries', sort=alt.EncodingSortField(levels_wide[0], op='max'), axis=alt.Axis(labels=False)),
  y='value:Q',
  color='column:N'
)

rule = global_base.mark_rule(color='red').encode(
    x=alt.X('name:O',title='Countries', sort=alt.EncodingSortField(levels_wide[0], op='max'), axis=alt.Axis(labels=False)),
    size=alt.value(3)
).transform_filter(
    alt.datum.name == country
)


country_bar = alt.Chart(subset_wide[subset_wide['name']== country]).transform_fold(
  levels_wide,
  as_=['column', 'value']
).mark_bar().encode(
    x=alt.X('name:O', title=f'{country}', axis=alt.Axis(labels=False)),
    y='value:Q',
    color='column:N'
).properties(
    width=550,
    height = 100
)

(global_chart + rule) & country_bar

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

