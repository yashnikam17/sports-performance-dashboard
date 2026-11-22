import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from analysis import load_data, player_summary, opponent_summary, recent_form

st.set_page_config(page_title="Sports Performance Dashboard",
                   page_icon="🏏", layout="wide")

# ---------- Custom CSS ----------
st.markdown("""
<style>
.block-container {padding-top: 1.5rem;}
div[data-testid="stMetric"] {
    background: #1e2530; border: 1px solid #2f3a4a;
    padding: 14px; border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

st.title("🏏 Sports Performance Analytics Dashboard")
st.caption("Player performance analysis with Python, Pandas, Plotly & Streamlit")

df = load_data()

# ---------- Sidebar ----------
st.sidebar.header("🔎 Filters")
all_opps = sorted(df["opponent"].unique())
opponents = st.sidebar.multiselect("Opponent", all_opps, default=all_opps)

date_min, date_max = df["date"].min().date(), df["date"].max().date()
date_range = st.sidebar.date_input("Date range", (date_min, date_max),
                                   min_value=date_min, max_value=date_max)

filtered = df[df["opponent"].isin(opponents)]
if len(date_range) == 2:
    filtered = filtered[(filtered["date"].dt.date >= date_range[0]) &
                        (filtered["date"].dt.date <= date_range[1])]

if filtered.empty:
    st.warning("Is filter mein koi data nahi hai. Filter change karo.")
    st.stop()

summary = player_summary(filtered)

# ---------- KPI cards ----------
top_bat = summary.sort_values("runs", ascending=False).iloc[0]
top_bowl = summary.sort_values("wickets", ascending=False).iloc[0]

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Matches", filtered["match_id"].nunique())
c2.metric("Total Runs", int(filtered["runs"].sum()))
c3.metric("Total Wickets", int(filtered["wickets"].sum()))
c4.metric("Top Scorer", top_bat["player"], f"{int(top_bat['runs'])} runs")
c5.metric("Top Bowler", top_bowl["player"], f"{int(top_bowl['wickets'])} wkts")

st.divider()

# ---------- Tabs ----------
tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Overview", "👤 Player Analysis", "⚔️ Compare Players", "🌍 Opponent Analysis"])

# ===== TAB 1: Overview =====
with tab1:
    l, r = st.columns(2)
    with l:
        fig = px.bar(summary.sort_values("runs", ascending=False),
                     x="player", y="runs", color="runs",
                     color_continuous_scale="Blues", title="Top Run Scorers")
        st.plotly_chart(fig, use_container_width=True)
    with r:
        fig = px.bar(summary.sort_values("wickets", ascending=False),
                     x="player", y="wickets", color="wickets",
                     color_continuous_scale="Reds", title="Top Wicket Takers")
        st.plotly_chart(fig, use_container_width=True)

    l, r = st.columns(2)
    with l:
        fig = px.scatter(summary, x="strike_rate", y="batting_avg",
                         size="runs", color="player", text="player",
                         title="Strike Rate vs Batting Average")
        fig.update_traces(textposition="top center")
        st.plotly_chart(fig, use_container_width=True)
    with r:
        fig = px.bar(summary.dropna(subset=["economy"]).sort_values("economy"),
                     x="player", y="economy", color="economy",
                     color_continuous_scale="Viridis_r",
                     title="Bowling Economy (lower is better)")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 Player Summary Table")
    st.dataframe(summary.sort_values("runs", ascending=False),
                 use_container_width=True, hide_index=True)

# ===== TAB 2: Player Analysis =====
with tab2:
    player = st.selectbox("Player chuno", summary["player"], key="single")
    p_df = filtered[filtered["player"] == player].sort_values("date")
    p_sum = summary[summary["player"] == player].iloc[0]

    a, b, c, d, e = st.columns(5)
    a.metric("Runs", int(p_sum["runs"]))
    b.metric("Batting Avg", p_sum["batting_avg"])
    c.metric("Strike Rate", p_sum["strike_rate"])
    d.metric("Highest", int(p_sum["highest"]))
    e.metric("Last 5 Avg", round(recent_form(filtered, player), 1))

    l, r = st.columns(2)
    with l:
        p_df = p_df.assign(rolling_avg=p_df["runs"].rolling(5, min_periods=1).mean())
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=p_df["date"], y=p_df["runs"],
                                 mode="lines+markers", name="Runs"))
        fig.add_trace(go.Scatter(x=p_df["date"], y=p_df["rolling_avg"],
                                 mode="lines", name="5-match avg",
                                 line=dict(dash="dash")))
        fig.update_layout(title=f"{player} - Runs Trend")
        st.plotly_chart(fig, use_container_width=True)
    with r:
        fig = px.pie(values=[p_sum["fours"] * 4, p_sum["sixes"] * 6,
                             p_sum["runs"] - p_sum["fours"] * 4 - p_sum["sixes"] * 6],
                     names=["Fours", "Sixes", "Singles/Doubles"],
                     title=f"{player} - How runs are scored", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

# ===== TAB 3: Compare =====
with tab3:
    col1, col2 = st.columns(2)
    players = list(summary["player"])
    p1 = col1.selectbox("Player 1", players, index=0)
    p2 = col2.selectbox("Player 2", players, index=min(1, len(players) - 1))

    metrics = ["runs", "batting_avg", "strike_rate", "fours", "sixes", "wickets"]
    comp = summary[summary["player"].isin([p1, p2])]
    norm = comp.copy()
    for m in metrics:
        mx = summary[m].max()
        norm[m] = comp[m] / mx * 100 if mx else 0

    fig = go.Figure()
    for _, row in norm.iterrows():
        fig.add_trace(go.Scatterpolar(
            r=[row[m] for m in metrics] + [row[metrics[0]]],
            theta=metrics + [metrics[0]], fill="toself", name=row["player"]))
    fig.update_layout(title=f"{p1} vs {p2} (Radar)",
                      polar=dict(radialaxis=dict(visible=True, range=[0, 100])))
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(comp.set_index("player")[metrics].T, use_container_width=True)

# ===== TAB 4: Opponent =====
with tab4:
    opp = opponent_summary(filtered)
    l, r = st.columns(2)
    with l:
        fig = px.bar(opp.sort_values("runs", ascending=False),
                     x="opponent", y="runs", color="runs",
                     title="Runs against each Opponent")
        st.plotly_chart(fig, use_container_width=True)
    with r:
        fig = px.bar(opp, x="opponent", y="runs_per_match", color="opponent",
                     title="Avg Team Runs per Match vs Opponent")
        st.plotly_chart(fig, use_container_width=True)

    heat = filtered.pivot_table(index="player", columns="opponent",
                                values="runs", aggfunc="sum")
    fig = px.imshow(heat, text_auto=True, aspect="auto",
                    color_continuous_scale="YlOrRd",
                    title="Player vs Opponent Runs Heatmap")
    st.plotly_chart(fig, use_container_width=True)

st.caption("Made by Yash & Friend | Data is simulated for demo purposes")