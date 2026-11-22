import streamlit as st
import plotly.express as px
from analysis import load_data, player_summary

st.set_page_config(page_title="Sports Performance Dashboard", layout="wide")
st.title("🏏 Sports Performance Analytics Dashboard")

df = load_data()

# ---- Sidebar filters ----
st.sidebar.header("Filters")
opponents = st.sidebar.multiselect(
    "Opponent", df["opponent"].unique(), default=list(df["opponent"].unique()))
filtered = df[df["opponent"].isin(opponents)]

summary = player_summary(filtered)

# ---- KPI cards ----
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Matches", filtered["match_id"].nunique())
c2.metric("Total Runs", int(filtered["runs"].sum()))
c3.metric("Total Wickets", int(filtered["wickets"].sum()))
c4.metric("Total Sixes", int(filtered["sixes"].sum()))

st.divider()

# ---- Charts row 1 ----
left, right = st.columns(2)

with left:
    fig = px.bar(summary.sort_values("runs", ascending=False),
                 x="player", y="runs", color="runs", title="Top Run Scorers")
    st.plotly_chart(fig, use_container_width=True)

with right:
    fig = px.bar(summary.sort_values("wickets", ascending=False),
                 x="player", y="wickets", color="wickets", title="Top Wicket Takers")
    st.plotly_chart(fig, use_container_width=True)

# ---- Charts row 2 ----
left, right = st.columns(2)

with left:
    fig = px.scatter(summary, x="strike_rate", y="batting_avg", size="runs",
                     text="player", title="Strike Rate vs Batting Average")
    st.plotly_chart(fig, use_container_width=True)

with right:
    player = st.selectbox("Player chuno (trend ke liye)", summary["player"])
    p_df = filtered[filtered["player"] == player].sort_values("date")
    fig = px.line(p_df, x="date", y="runs", markers=True,
                  title=f"{player} - Runs per Match")
    st.plotly_chart(fig, use_container_width=True)

# ---- Table ----
st.subheader("Player Summary Table")
st.dataframe(summary.sort_values("runs", ascending=False), use_container_width=True)