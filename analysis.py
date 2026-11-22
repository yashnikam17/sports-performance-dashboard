import numpy as np
import pandas as pd


def load_data(path="data/matches.csv"):
    return pd.read_csv(path, parse_dates=["date"])


def player_summary(df):
    g = df.groupby("player").agg(
        matches=("match_id", "nunique"),
        runs=("runs", "sum"),
        balls=("balls_faced", "sum"),
        fours=("fours", "sum"),
        sixes=("sixes", "sum"),
        wickets=("wickets", "sum"),
        overs=("overs_bowled", "sum"),
        conceded=("runs_conceded", "sum"),
        highest=("runs", "max"),
    ).reset_index()

    g["batting_avg"] = (g["runs"] / g["matches"]).round(2)
    g["strike_rate"] = (g["runs"] / g["balls"] * 100).round(2)
    g["economy"] = (g["conceded"] / g["overs"].replace(0, np.nan)).round(2)
    g["boundary_runs"] = g["fours"] * 4 + g["sixes"] * 6
    g["boundary_pct"] = (g["boundary_runs"] / g["runs"] * 100).round(1)
    return g


def opponent_summary(df):
    g = df.groupby("opponent").agg(
        runs=("runs", "sum"),
        wickets=("wickets", "sum"),
        matches=("match_id", "nunique"),
    ).reset_index()
    g["runs_per_match"] = (g["runs"] / g["matches"]).round(1)
    return g


def recent_form(df, player, n=5):
    p = df[df["player"] == player].sort_values("date").tail(n)
    return p["runs"].mean() if len(p) else 0


if __name__ == "__main__":
    data = load_data()
    print(player_summary(data).sort_values("runs", ascending=False))