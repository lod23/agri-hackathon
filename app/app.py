import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Should I Irrigate?", layout="centered")
st.title("Should I irrigate my corn?")
st.caption("Delaware corn · USDA county yields + U.S. Drought Monitor, 2015–2025")

gap = pd.read_csv("data/irrigation_gap.csv", dtype={"fips": str})
drought = pd.read_csv("data/drought_de.csv", dtype={"fips": str})
drought["mapDate"] = pd.to_datetime(drought["mapDate"])
drought["dsci"] = drought[["d0", "d1", "d2", "d3", "d4"]].sum(axis=1)

county = st.selectbox("Your county", sorted(gap["County"].unique()))
g = gap[gap["County"] == county]
fips = g["fips"].iloc[0]

latest = drought[drought["fips"] == fips].sort_values("mapDate").iloc[-1]
is_dry = latest["dsci"] >= 10
past = g[g["dsci"] >= 10] if is_dry else g[g["dsci"] < 10]
if past.empty:
    past = g
gain = past["irr_gain"].mean()

c1, c2 = st.columns(2)
c1.metric("Drought score now", f"{latest['dsci']:.0f}",
          help="0 = no drought, 500 = worst. Week of " + latest["mapDate"].strftime("%b %d, %Y"))
c2.metric("Expected extra yield", f"+{gain:.0f} bu/acre",
          help=f"Average from {len(past)} past {'dry' if is_dry else 'normal'} seasons")

st.subheader("Is it worth it?")
price = st.number_input("Your corn price ($/bu)", value=4.00, step=0.25)
cost = st.number_input("Your irrigation cost ($/acre)", value=100.0, step=10.0)
net = gain * price - cost

if net > 0:
    st.success(f"Irrigating likely earns about **${net:,.0f} more per acre**.")
else:
    st.warning(f"Irrigating likely costs about **${-net:,.0f} more per acre** than it returns.")

chart = g.melt(id_vars="Year", value_vars=["irr", "non_irr"], var_name="Field", value_name="bu/acre")
chart["Field"] = chart["Field"].map({"irr": "Irrigated", "non_irr": "Not irrigated"})
fig = px.bar(chart, x="Year", y="bu/acre", color="Field", barmode="group",
             title=f"{county.title()}: irrigated vs non-irrigated corn yield")
st.plotly_chart(fig, use_container_width=True)

st.caption("Historical pattern, not a forecast. Enter your own price and cost.")