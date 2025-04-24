import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import base64
import plotly.express as px



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
st.title("Flu Forecast Dashboard for 2025")

# User inputs
state_selected = st.selectbox("Please Select a State:", options=df['State'].unique())
week_input = st.slider("Please Select a Week:", min_value=1, max_value=27, value=10)

# Data filtering
state_df = df[df['State'] == state_selected]

#Prediicted Cases
predicted_row = state_df[state_df['Week'] == week_input]
if not predicted_row.empty:
    predicted_value = predicted_row['cases_per_100k'].values[0]

    # Determine risk level
    if predicted_value < 5:
        risk_level = 'Minimal'
    elif predicted_value < 15:
        risk_level = 'Low'
    elif predicted_value < 30:
        risk_level = 'Medium'
    else:
        risk_level = 'High'

    st.markdown(f"""
        <div style='font-size: 22px; font-weight: bold;'>
            {state_selected}'s Predicted Flu Cases in Week {week_input}:
        </div>
        <div style='font-size: 36px; font-weight: bold; margin-top: 4px;'>
            {predicted_value:.1f} cases per 100,000
        </div>
        <div style='font-size: 20px; margin-top: 6px;'>
            Weekly Flu Risk Level: <strong>{risk_level}</strong>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"### No prediction available for {state_selected} in Week {week_input}.")



import plotly.express as px

# --- 3-week forecast (Week X to X+2) ---
forecast_df = state_df[(state_df['Week'] >= week_input) & (state_df['Week'] <= week_input + 2)]
forecast_df = forecast_df.sort_values('Week').dropna(subset=['cases_per_100k'])

st.subheader(f"Flu Forecasts for Weeks {week_input} to {week_input + 2}")

if not forecast_df.empty:
    fig = px.line(
        forecast_df,
        x='Week',
        y='cases_per_100k',
        markers=True,
        title=f"3-Week Forecast for {state_selected} (Weeks {week_input} to {week_input + 2})",
        hover_data={'Week': True, 'cases_per_100k': ':.1f'}
    )
    fig.update_traces(
        line=dict(color='white'),
        marker=dict(color='white'),
        hoverlabel=dict(font=dict(size=16))
    )
    fig.update_layout(
        paper_bgcolor='#0a1528',
        plot_bgcolor='#0a1528',
        font_color='white'
    )
    st.plotly_chart(fig)
else:
    st.markdown("No forecast data available.")


# --- Extended forecast (Week X to Week 30) ---
forecast_to_30_df = state_df[(state_df['Week'] >= week_input) & (state_df['Week'] <= 30)]
forecast_to_30_df = forecast_to_30_df.sort_values('Week').dropna(subset=['cases_per_100k'])

st.subheader(f"Extended Flu Forecasts for Weeks {week_input} to 30")

if not forecast_to_30_df.empty:
    fig2 = px.line(
        forecast_to_30_df,
        x='Week',
        y='cases_per_100k',
        markers=True,
        title=f"Extended Forecast for {state_selected} (Weeks {week_input} to 30)",
        hover_data={'Week': True, 'cases_per_100k': ':.1f'}
    )
    fig2.update_traces(
        line=dict(color='white'),
        marker=dict(color='white'),
        hoverlabel=dict(font=dict(size=16))
    )
    fig2.update_layout(
        paper_bgcolor='#0a1528',
        plot_bgcolor='#0a1528',
        font_color='white'
    )
    st.plotly_chart(fig2)
else:
    st.markdown("No forecast data available.")

# --- Choropleth Map ---
st.subheader(f"Flu Forecasts Across the US in Week {week_input}")

# Define state abbreviation dictionary FIRST
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

# Then safely use it here
week_df = df[df['Week'] == week_input].copy()
week_df['code'] = week_df['State'].map(state_abbrev)

import pandas as pd
# Assign risk levels based on case thresholds
def get_risk_level(cases):
    if cases < 5:
        return 'Minimal'
    elif cases < 15:
        return 'Low'
    elif cases < 30:
        return 'Medium'
    else:
        return 'High'

# Apply function to create the column
week_df['risk_level'] = week_df['cases_per_100k'].apply(get_risk_level)

# THEN convert to ordered categorical
risk_order = ['Minimal', 'Low', 'Medium', 'High']
week_df['risk_level'] = pd.Categorical(week_df['risk_level'], categories=risk_order, ordered=True)

# Define discrete color mapping
risk_colors = {
    'Minimal': '#FDFD96',  # bright pastel yellow (lemon sorbet)
    'Low':     '#FFB347',  # vivid orange (apricot)
    'Medium':  '#FF7043',  # punchy orange-red (melon red)
    'High':    '#D32F2F'   # deep red (crimson danger)
}

fig = px.choropleth(
    week_df,
    locations='code',
    locationmode='USA-states',
    color='risk_level',
    category_orders={'risk_level': risk_order},  # <-- forces correct legend order
    color_discrete_map=risk_colors,
    scope='usa',
    hover_name='State',
    hover_data={'cases_per_100k': ':.1f', 'risk_level': True},
    title=f"Flu Risk Level by State – Week {week_input}"
)

fig.update_layout(
    geo=dict(
        bgcolor='rgba(0,0,0,0)',
        showland=True,
        landcolor='rgba(0,0,0,0)',
        showframe=False,
        projection=dict(type='albers usa')
    ),
    paper_bgcolor='#0a1528',
    font_color='white',
    hoverlabel=dict(font=dict(size=16))
)

highlight_state_code = state_abbrev.get(state_selected)

# Optional: Add selected state outline (keep this if you already use it)
if highlight_state_code:
    fig.add_scattergeo(
        locations=[highlight_state_code],
        locationmode="USA-states",
        geo="geo",
        mode="markers+text",
        marker=dict(
            size=0.1,
            line=dict(width=8, color='green')
        ),
        name=f"{state_selected} (Selected)",
        showlegend=False,
        text=[state_selected],
        textposition="top center",
        hoverinfo="skip"
    )

st.plotly_chart(fig)

# Mitigation recommendations dictionary
mitigation_guidance = {
    'Minimal': """
**🧑‍⚕️ Public Health Officials**
- Maintain routine flu surveillance and update emergency response protocols.  
- Stockpile antivirals, testing kits, and PPE.  
- Prepare vaccination outreach materials and risk communication templates.  
- Promote general wellness campaigns (nutrition, physical activity, sleep hygiene).  

**👥 General Population**
- Practice routine hygiene (handwashing, covering coughs).  
- Stay current with annual flu vaccinations.  
- Maintain healthy lifestyle: balanced nutrition, exercise, sleep.  
- Ensure adequate vitamin intake (especially D and C) through food or supplements.
""",
    'Low': """
**🧑‍⚕️ Public Health Officials**
- Begin early communication with local agencies and community partners.  
- Emphasize flu vaccination in schools, elder care facilities, and workplaces.  
- Coordinate with pharmacies on vitamin supplement supply (especially D and C).  
- Share risk trends with providers and EMS for mild prep measures.  

**👥 General Population**
- Get vaccinated if not done yet.  
- Begin limiting non-essential exposure to crowded areas.  
- Boost intake of immune-supporting foods: citrus, fatty fish, cereals, greens.
""",
    'Medium': """
**🧑‍⚕️ Public Health Officials**
- Expand targeted vaccination campaigns in higher-risk regions.  
- Distribute regional health alerts (symptoms, when to seek care).  
- Increase access to testing.  
- Support nutritional aid programs in schools and food banks.  

**👥 General Population**
- Stay home if feeling unwell or exposed.  
- Avoid large gatherings.  
- Sanitize frequently touched surfaces.  
- Help vulnerable household members with meals/supplements.
""",
    'High': """
**🧑‍⚕️ Public Health Officials**
- Activate distancing protocols: school closures, telework.  
- Issue public health alerts via all media.  
- Send mobile health units to hotspots.  
- Deliver immune-boosting foods and supplements to vulnerable areas.  

**👥 General Population**
- Strictly follow health guidelines (stay home, wear masks, distance).  
- Stay hydrated and eat vitamin-rich foods.  
- Avoid non-essential travel.  
- Monitor symptoms closely and seek care early if needed.
"""
}


st.markdown("---")
st.subheader("🛡️ Recommended Mitigation Measures")
st.markdown(mitigation_guidance[risk_level])






