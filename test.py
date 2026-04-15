import streamlit as st
import altair as alt
import pandas as pd

# Load the forecast CSV
df = pd.read_csv("forecast_export.csv")
df["ds"] = pd.to_datetime(df["ds"])

# Filter for one brand-metric (or use Streamlit dropdowns)
brand = "Brand1"
metric = "MOTRX"
subset = df[(df["PRODUCT"] == brand) & (df["METRIC"] == metric)]

# Color scale for status
color_scale = alt.Scale(domain=["Pass", "Fail", "Holiday"], range=["grey", "red", "blue"])

# Forecast bounds
interval = alt.Chart(subset).mark_area(opacity=0.2, color='blue').encode(
    x='ds:T',
    y='yhat_lower:Q',
    y2='yhat_upper:Q'
)

# Actual dots
points = alt.Chart(subset).mark_circle(size=60).encode(
    x='ds:T',
    y='y:Q',
    color=alt.Color('Legend:N', scale=color_scale),
    tooltip=['ds:T', 'y:Q', 'Legend:N', 'holiday:N']
)

# Combine
chart = (interval + points).properties(
    width=800,
    height=400,
    title=f"{brand} | {metric} - Forecast Check"
).configure_axis(grid=False)

# Show in Streamlit
st.altair_chart(chart, use_container_width=True)
