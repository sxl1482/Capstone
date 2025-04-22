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
ax2.set_title(f"Forecast until Week 30 for {state_selected}", color='white')
ax2.set_xlabel('Week', color='white')
ax2.set_ylabel('Cases per 100k', color='white')
ax2.tick_params(colors='white')
fig2.patch.set_alpha(0)
ax2.set_facecolor('none')
st.pyplot(fig2)

import matplotlib as mpl

# US map visualization using Geopandas
st.subheader(f"US States Cases per 100k in Week {week_input}")

# Geopandas US States shape file
usa = gpd.read_file('https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json')
week_df = df[df['Week'] == week_input].copy()
week_df = week_df.rename(columns={"State": "name"})
us_map = usa.merge(week_df, on='name', how='left')

# Avoid NaNs
us_map['cases_per_100k'] = us_map['cases_per_100k'].fillna(0)

# Define colormap
cmap = mpl.cm.Oranges
norm = mpl.colors.Normalize(vmin=us_map['cases_per_100k'].min(), vmax=us_map['cases_per_100k'].max())

fig3, ax3 = plt.subplots(figsize=(15, 10))
us_map.plot(
    column='cases_per_100k',
    cmap=cmap,
    linewidth=0.8,
    ax=ax3,
    edgecolor='0.8'
)

# Custom colorbar with white text
sm = mpl.cm.ScalarMappable(cmap=cmap, norm=norm)
sm._A = []  # Required for ScalarMappable to work in matplotlib

cbar = fig3.colorbar(sm, ax=ax3, orientation="vertical", fraction=0.03, pad=0.01)
cbar.set_label("Cases per 100k", color='white')
cbar.ax.yaxis.set_tick_params(color='white')
plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white')

# Finish styling
ax3.set_title(f"Cases per 100k by State in Week {week_input}", fontsize=16, color='white')
ax3.axis('off')
fig3.patch.set_alpha(0)
ax3.set_facecolor('none')

st.pyplot(fig3)






