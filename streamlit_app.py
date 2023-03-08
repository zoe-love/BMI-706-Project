import altair as alt
import pandas as pd
import streamlit as st
import vega_datasets
from vega_datasets import data
import country_converter as coco
from PIL import Image
cc = coco.CountryConverter()


@st.cache_data
def load_data():

    df = pd.read_csv("https://raw.githubusercontent.com/zoe-love/BMI-706-Project/main/wash_data_cleaned.csv")

    return df

df = load_data()

### TITLE ###
st.write("## Global Water, Hygiene, and Sanitation Data")

image = Image.open('infographic.jpg')
st.image(image, caption='Breakdown of WASH Data')

# Year selection Slider

year = st.select_slider(
    label = "Year Select",
    options = df['year'].unique().tolist(),
    value = 2012)
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

## Chart 1 ##
source = alt.topo_feature(data.world_110m.url, 'countries')

width = 600
height  = 300
project = 'equirectangular'

background = alt.Chart(source
).mark_geoshape(
    fill='#aaa',
    stroke='white'
).properties(
    width=width,
    height=height
).project(project)

selector = alt.selection_single(
    empty='all', fields=['id']
    )

chart_base = alt.Chart(source
    ).properties( 
        width=width,
        height=height
    ).project(project
    ).add_selection(selector
    ).transform_lookup(
        lookup="id",
        from_=alt.LookupData(subset[subset['level_1']=='bas'], "country-code", ["coverage", 'name', 'pop_n', 'year', 'level_1'])
    )

map = chart_base.mark_geoshape().encode(
    color='coverage:Q',
    tooltip=['pop_n:Q', 'name:N']
    ).transform_filter(
    selector
    ).properties(
    title=f'{type} coverage globally in {year}'
)
chart1 = alt.vconcat(background + map)
chart1

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

### Chart 2 ###
selection = alt.selection_multi(fields=['column'], bind='legend')

global_base = alt.Chart(subset_wide).properties(
    width=500
)

global_chart = global_base.transform_fold(
  levels_wide,
  as_=['column', 'value']
).mark_bar().encode(
  x=alt.X('name:O',title='Countries', sort=alt.EncodingSortField(levels_wide[0], op='max'), axis=alt.Axis(labels=False)),
  y='value:Q',
  color='column:N',
  opacity=alt.condition(selection, alt.value(1), alt.value(0.2))
).add_selection(
    selection
)
# Add line to global overview for country selected
rule = global_base.mark_rule(color='red').encode(
    x=alt.X('name:O',title='Countries', sort=alt.EncodingSortField(levels_wide[0], op='max'), axis=alt.Axis(labels=False)),
    size=alt.value(3)
).transform_filter(
    alt.datum.name == country
)

# Add Country specific bar chart
country_bar = alt.Chart(subset_wide[subset_wide['name']== country]).transform_fold(
  levels_wide,
  as_=['column', 'value']
).mark_bar().encode(
    x=alt.X('name:O', title=f'{country}', axis=alt.Axis(labels=False)),
    y=alt.Y('value:Q', title = ''),
    color='column:N',
    opacity=alt.condition(selection, alt.value(1), alt.value(0.2))
).properties(
    width=50
).add_selection(
    selection
)

(global_chart + rule) | country_bar

## Chart 3##
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
    width=275
).add_selection(
    selection
)

country_bar = alt.Chart(line_df).mark_bar().encode(
    x='year:O',
    y=alt.Y('coverage:Q', title = ''),
    color='level_1:N',
    opacity=alt.condition(selection, alt.value(1), alt.value(0.2))
).add_selection(
    brush
).properties(
    width=275
).add_selection(
    selection
)

chart3 = upper | country_bar

st.altair_chart(chart3, use_container_width=True)


st.write("## Breakdown of Service Levels")
@st.cache_data
def load_breakdown_data():

    df = pd.read_csv("https://raw.githubusercontent.com/zoe-love/BMI-706-Project/main/wash_data_breakdown.csv")

    return df

wash_df = load_breakdown_data() 

df_subset = wash_df[(wash_df["year"] == year) &
                    (wash_df["name"] == country) &
                    (wash_df["measure"] == type)]

# Create dataframes for charts
if type == 'hyg':
  df_bar = df_subset[df_subset['level_0'].isin(['improved_1', 'unimproved'])]

  df_improved_1 = df_subset[df_subset['level_0'] == 'improved_1']

  df_unimproved = df_subset[df_subset['level_0'] == 'unimproved']
else:
  df_bar = df_subset[(df_subset['level_0'].isin(['improved_1', 'unimproved'])) & 
                  (df_subset['level_1'] != 'bas')]

  df_improved_1 = df_subset[(df_subset['level_0'] == 'improved_1') & 
                        (df_subset['level_1'] != 'bas')]

  df_sm = df_subset[df_subset['level_0'] == 'sm_criteria']

  df_improved_2 = df_subset[df_subset['level_0'] == 'improved_2']

  df_unimproved = df_subset[df_subset['level_0'] == 'unimproved']

# Specify order and colors
if type == 'wat':
  bar_sort = ["Safely managed", "Basic", "Limited", "Unimproved", "Surface water"]
  bar_color = ['#85EF73', '#C5F0AA', '#FBE48F', '#FFCC99', '#FF8585']

  imp_1_sort = ["Safely managed", "Basic", "Limited"]
  imp_1_color = ['#85EF73', '#C5F0AA', '#FBE48F']

  sm_sort = ["Available when needed", "Accessible on premises", "Free from contamination"]
  sm_color = ['#85EF73','#C5F0AA','#D5F3D3'] 

  imp_2_sort = ["Piped", "Non-piped"]
  imp_2_color = ['#85EF73','#C5F0AA'] 

  unimp_sort = ["Unimproved", "Surface water"]
  unimp_color = ['#FFCC99', '#FF8585']
elif type == 'san':
  bar_sort = ["Safely managed", "Basic", "Limited", "Unimproved", "Open defecation"]
  bar_color = ['#85EF73', '#C5F0AA', '#FBE48F', '#FFCC99', '#FF8585']

  imp_1_sort = ["Safely managed", "Basic", "Limited"]
  imp_1_color = ['#85EF73', '#C5F0AA', '#FBE48F']

  sm_sort = ["Treated and disposed in situ", "Stored, then emptied and treated off-site", "Transported through a sewer"]
  sm_color = ['#D5F3D3','#C5F0AA','#85EF73']

  imp_2_sort = ["Sewer", "Septic tanks", "Latrines"]
  imp_2_color = ['#85EF73','#C5F0AA','#D5F3D3'] 

  unimp_sort = ["Unimproved", "Open defecation"]
  unimp_color = ['#FFCC99', '#FF8585']
else:
  bar_sort = ["Basic", "Limited", "No facility"]
  bar_color = ['#C5F0AA', '#FBE48F', '#FFCC99']

  imp_1_sort = ["Basic", "Limited"]
  imp_1_color = ['#C5F0AA', '#FBE48F']

  unimp_sort = ["No facility"]
  unimp_color = ['#FFCC99']

# Construct charts
if type == 'hyg':
  bar = alt.Chart(df_bar).mark_bar().encode(
      x=alt.X('coverage', title="", scale=alt.Scale(domain=[0, 100])),
      y=alt.Y('name',title="",axis=alt.Axis(labels=False)),
      color=alt.Color('Service',
                      sort=bar_sort,
                      scale=alt.Scale(domain=bar_sort,
                                      range=bar_color)),
      order=alt.Order('color_sort:Q'),
      tooltip=['Service', 'coverage']
  ).properties(
    title=country,
      width=570,
      height=50
  )

  imp_1 = alt.Chart(df_improved_1).mark_arc(innerRadius=75).encode(
      theta = alt.Theta('coverage', title=''),
      color = alt.Color('Service',
                      sort=imp_1_sort,
                      scale=alt.Scale(domain=imp_1_sort,
                                      range=imp_1_color)),
      order = alt.Order('color_sort:Q'),
      tooltip=['Service', 'coverage']
  ).properties(
      title="Improved services",
      width = 275
  )

  unimp = alt.Chart(df_unimproved).mark_arc(innerRadius=75).encode(
      theta = alt.Theta('coverage', title=''),
      color = alt.Color('Service',
                      # sort=unimp_sort,
                      scale=alt.Scale(domain=unimp_sort,
                                      range=unimp_color)),
      order = alt.Order('color_sort:Q'),
      tooltip=['Service', 'coverage']
  ).properties(
      title="Unimproved services",
      width = 275
  )

  breakdown = alt.hconcat(imp_1, unimp).resolve_scale(theta='independent')
  chart4 = alt.vconcat(bar, breakdown)
else:
  bar = alt.Chart(df_bar).mark_bar().encode(
      x=alt.X('sum(coverage)', title="", scale=alt.Scale(domain=[0, 100])),
      y=alt.Y('name',title="",axis=alt.Axis(labels=False)),
      color=alt.Color('Service',
                      sort=bar_sort,
                      scale=alt.Scale(domain=bar_sort,
                                      range=bar_color)),
      order=alt.Order('color_sort:Q'),
      tooltip=['Service', 'coverage']
  ).properties(
    title=country,
    width=680,
    height=50
  )

  imp_1 = alt.Chart(df_improved_1).mark_arc(innerRadius=75).encode(
      theta = alt.Theta('sum(coverage)', title=''),
      color = alt.Color('Service',
                      sort=imp_1_sort,
                      scale=alt.Scale(domain=imp_1_sort,
                                      range=imp_1_color)),
      order = alt.Order('color_sort:Q'),
      tooltip=['Service', 'coverage']
  ).properties(
      title="Improved services",
      width = 275
  )  
  
  sm = alt.Chart(df_sm).mark_bar().encode(
    x=alt.X('sum(coverage)', title="", scale=alt.Scale(domain=[0, 100])),
    y=alt.Y('Service',title="",
            sort=sm_sort,
            axis=alt.Axis(labels=False)),
    color=alt.Color('Service',title="Criteria",
                    sort=sm_sort,
                    scale=alt.Scale(domain=sm_sort,
                                    range=sm_color)),
      tooltip=['Service', 'coverage']
  ).properties(
      title="Safely managed criteria",
      width=275,
      height=100
  )

  imp_2 = alt.Chart(df_improved_2).mark_arc(innerRadius=75).encode(
      theta = alt.Theta('sum(coverage)', title=''),
      color = alt.Color('Service',
                      sort=imp_2_sort,
                      scale=alt.Scale(domain=imp_2_sort,
                                      range=imp_2_color)),
      tooltip=['Service', 'coverage']
  ).properties(
      title="Alternative breakdown",
      width = 275
  )

  unimp = alt.Chart(df_unimproved).mark_arc(innerRadius=75).encode(
      theta = alt.Theta('sum(coverage)', title=''),
      color = alt.Color('Service',
                      sort=unimp_sort,
                      scale=alt.Scale(domain=unimp_sort,
                                      range=unimp_color)),
      order = alt.Order('color_sort:Q'),
      tooltip=['Service', 'coverage']
  ).properties(
      title="Unimproved services",
      width = 275
  )

  step1 = alt.vconcat(sm, imp_2).resolve_scale(color='independent')
  step2 = alt.hconcat(imp_1, unimp).resolve_scale(color='independent',
                                                  theta='independent')
  step3 = alt.vconcat(step2, step1).resolve_scale(color='independent',
                                                    theta='independent')
  chart4 = alt.vconcat(bar, step3).resolve_scale(color='independent')

st.altair_chart(chart4, use_container_width=True)