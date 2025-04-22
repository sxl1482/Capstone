import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import base64


def set_background(image_path):
    with open(image_path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_background("pictures/streamlit_background.jpg")
# Load data
@st.cache_data
def load_data(url):
    return pd.read_csv(url)

url = "https://raw.githubusercontent.com/sxl1482/Capstone/refs/heads/main/df_ext.csv"
df = load_data(url)

# Filter data for year 2025
df = df[df['Year'] == 2025]

# Streamlit interface
st.title("Flu Forecast Visualization (2025)")

# User inputs
state_selected = st.selectbox("Select State:", options=df['State'].unique())
week_input = st.slider("Select Week:", min_value=1, max_value=27, value=10)

# Data filtering
state_df = df[df['State'] == state_selected]

# Display predicted value for selected state and week
predicted_row = state_df[state_df['Week'] == week_input]
if not predicted_row.empty:
    predicted_value = predicted_row['cases_per_100k'].values[0]
    st.markdown(f"### {state_selected}'s Predicted Flu Cases in Week {week_input}: **{predicted_value:.1f} cases per 100,000**")
else:
    st.markdown(f"### No prediction available for {state_selected} in Week {week_input}.")

# Forecast next 3 weeks from input
forecast_df = state_df[(state_df['Week'] > week_input) & (state_df['Week'] <= week_input + 3)]
st.subheader(f"Forecast for Weeks {week_input + 1} to {week_input + 3}")

fig, ax = plt.subplots()
ax.plot(forecast_df['Week'], forecast_df['cases_per_100k'], marker='o', color='white')

# Add value labels above each point
for i, row in forecast_df.iterrows():
    ax.text(
        row['Week'], 
        row['cases_per_100k'] + 0.5,  # slight vertical offset
        f"{row['cases_per_100k']:.1f}", 
        color='white', 
        ha='center',
        fontsize=9
    )

ax.set_title(f"3-Week Forecast for {state_selected} from Week {week_input}", color='white')
ax.set_xlabel('Week', color='white')
ax.set_ylabel('Cases per 100k', color='white')
ax.tick_params(colors='white')
fig.patch.set_alpha(0)
ax.set_facecolor('none')
st.pyplot(fig)

# Forecast until week 30
forecast_to_30_df = state_df[(state_df['Week'] > week_input) & (state_df['Week'] <= 30)]
st.subheader(f"Extended Forecast from Week {week_input + 1} to Week 30")

fig2, ax2 = plt.subplots()
ax2.plot(forecast_to_30_df['Week'], forecast_to_30_df['cases_per_100k'], marker='o', color='white')

# Add value labels above each point
for i, row in forecast_to_30_df.iterrows():
    ax2.text(
        row['Week'],
        row['cases_per_100k'] + 0.5,  # offset for visibility
        f"{row['cases_per_100k']:.1f}",
        color='white',
        ha='center',
        fontsize=9
    )

ax2.set_title(f"Forecast until Week 30 for {state_selected}", color='white')
ax2.set_xlabel('Week', color='white')
ax2.set_ylabel('Cases per 100k', color='white')
ax2.tick_params(colors='white')
fig2.patch.set_alpha(0)
ax2.set_facecolor('none')
st.pyplot(fig2)


import plotly.express as px

# Convert state name to abbreviation
state_abbrev = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
    'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
    'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
    'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
    'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH',
    'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC',
    'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA',
    'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD', 'Tennessee': 'TN',
    'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA',
    'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY', 'District of Columbia': 'DC'
}

week_df = df[df['Week'] == week_input].copy()
week_df['code'] = week_df['State'].map(state_abbrev)

fig = px.choropleth(
    week_df,
    locations='code',
    locationmode='USA-states',
    color='cases_per_100k',
    scope='usa',
    color_continuous_scale='Oranges',
    hover_name='State',
    hover_data={'cases_per_100k': ':.1f'},
    title=f"Flu Cases per 100,000 by State – Week {week_input}"
)

fig.update_layout(
    geo=dict(bgcolor='rgba(0,0,0,0)'),
    paper_bgcolor='#0a1528',
    font_color='white',
)

st.plotly_chart(fig)







