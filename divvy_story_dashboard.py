import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime
import calendar

# Set Streamlit page config
st.set_page_config(
    page_title="🚲 Divvy Bike Usage Dashboard (2020–2024)",
    page_icon="🚴‍♀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---- Custom CSS ----
st.markdown("""
    <style>
        html, body, [class*="css"] {
            font-family: 'Segoe UI', sans-serif;
            background-color: #0e1117;
            color: #f1f1f1;
        }
        .big-font {
            font-size: 1.5rem !important;
            font-weight: 600;
        }
        .small-note {
            font-size: 0.85rem;
            color: #AAAAAA;
        }
    </style>
""", unsafe_allow_html=True)

# ---- Title and Description ----
st.markdown("## 🚴‍♂️ Divvy Bike Usage Dashboard (2020–2024)")
st.markdown("_Explore rider behavior, usage trends, peak hours, and seasonal patterns using Divvy Bike data._")

# ---- File Upload ----
uploaded_file = st.file_uploader("📂 Upload your Divvy CSV file (max ~100MB)", type=["csv"])

if uploaded_file is None:
    st.warning("Please upload the CSV file to proceed.")
    st.stop()

df = pd.read_csv(uploaded_file)

# ---- Data Preprocessing ----
df['started_at'] = pd.to_datetime(df['started_at'], errors='coerce')
df['ended_at'] = pd.to_datetime(df['ended_at'], errors='coerce')
df.dropna(subset=['started_at', 'ended_at'], inplace=True)

df['hour'] = df['started_at'].dt.hour
df['day_of_week'] = df['started_at'].dt.day_name()
df['month'] = df['started_at'].dt.month
df['year'] = df['started_at'].dt.year

# ---- Sidebar Filters ----
st.sidebar.markdown("### 🔧 Filter Options")
rider_types = df['member_casual'].dropna().unique().tolist()
selected_rider = st.sidebar.selectbox("Select Rider Type", options=rider_types)

days = ["All"] + list(calendar.day_name)
selected_day = st.sidebar.selectbox("Select Day", options=days)

months = ["All"] + list(calendar.month_name[1:])
selected_month = st.sidebar.selectbox("Select Month", options=months)

# ---- Apply Filters ----
df_filtered = df[df['member_casual'] == selected_rider]
if selected_day != "All":
    df_filtered = df_filtered[df_filtered['day_of_week'] == selected_day]
if selected_month != "All":
    month_number = list(calendar.month_name).index(selected_month)
    df_filtered = df_filtered[df_filtered['month'] == month_number]

# ---- Summary Section ----
with st.expander("📊 Summary Statistics", expanded=True):
    total_rides = len(df_filtered)
    avg_ride_duration = (df_filtered['ended_at'] - df_filtered['started_at']).dt.total_seconds().mean() / 60

    col1, col2 = st.columns(2)
    col1.metric("Total Rides", f"{total_rides:,}")
    col2.metric("Avg Ride Duration", f"{avg_ride_duration:.2f} mins")

# ---- Plot by Hour ----
with st.expander("⏰ Ride Start Times by Hour"):
    st.markdown("Riders typically use Divvy bikes most during commuting hours (7–9AM, 4–6PM).")
    fig = px.histogram(df_filtered, x='hour', nbins=24, title=f"Rides by Hour ({selected_rider.title()} Riders)",
                       labels={'hour': 'Hour of Day'}, color_discrete_sequence=['#00cc96'])
    fig.update_layout(plot_bgcolor="#0e1117", paper_bgcolor="#0e1117", font_color="white")
    st.plotly_chart(fig, use_container_width=True)

# ---- Day of Week Usage ----
with st.expander("📅 Usage by Day of the Week"):
    counts = df_filtered['day_of_week'].value_counts().reindex(calendar.day_name)
    fig = px.bar(
        x=counts.index, y=counts.values,
        labels={"x": "Day", "y": "Number of Rides"},
        title=f"Weekly Usage Pattern - {selected_rider.title()} Riders",
        color_discrete_sequence=['#636efa']
    )
    fig.update_layout(plot_bgcolor="#0e1117", paper_bgcolor="#0e1117", font_color="white")
    st.plotly_chart(fig, use_container_width=True)

# ---- Map Visualization ----
with st.expander("🗺️ Start Location Heatmap"):
    st.markdown("This map shows where riders most commonly begin their trips.")
    if 'start_lat' in df_filtered.columns and 'start_lng' in df_filtered.columns:
        map_df = df_filtered[['start_lat', 'start_lng']].dropna().rename(
            columns={'start_lat': 'latitude', 'start_lng': 'longitude'})
        st.map(map_df.head(1000))  # limit to 1000 points for performance
    else:
        st.warning("Map could not be rendered. Required columns missing.")

# ---- Storytelling Section ----
with st.expander("📖 Storytelling: What Did We Learn?"):
    st.markdown("""
    - 🚴 **Members ride significantly more than casual users**, especially during weekdays and commuting hours.
    - 🌤️ **Summer months see a spike in activity**, suggesting recreational use increases seasonally.
    - 📍 **Start locations cluster around business and downtown hubs**, aligning with commuting trends.
    - 🕗 **Morning (7–9 AM) and Evening (4–6 PM)** ride spikes reflect work-home transitions.
    - 📈 **Weekend usage skews toward casual users**, especially in tourist-heavy or park areas.
    
    This dashboard helps Divvy understand rider behavior and optimize station placement and fleet management.
    """)

# ---- Footer ----
st.markdown("<br><hr><p class='small-note'>© 2024 Divvy Data Dashboard • Built with Streamlit</p>", unsafe_allow_html=True)
