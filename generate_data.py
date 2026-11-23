import os
import numpy as np
import pandas as pd

np.random.seed(42)

players = {
    "Rohit": {"team": "Mumbai", "role": "Batsman"},
    "Virat": {"team": "Delhi", "role": "Batsman"},
    "Hardik": {"team": "Baroda", "role": "All-rounder"},
    "Bumrah": {"team": "Gujarat", "role": "Bowler"},
    "Jadeja": {"team": "Saurashtra", "role": "All-rounder"},
    "Gill": {"team": "Punjab", "role": "Batsman"},
    "Rahul": {"team": "Karnataka", "role": "Batsman"},
    "Siraj": {"team": "Hyderabad", "role": "Bowler"},
}
opponents = ["Australia", "England", "Pakistan", "South Africa", "New Zealand"]

rows = []
for match_id in range(1, 31):
    date = pd.Timestamp("2026-01-01") + pd.Timedelta(days=match_id * 3)
    opponent = np.random.choice(opponents)
    for player, profile in players.items():
        role = profile["role"]
        if role in ("Batsman", "All-rounder"):
            balls = np.random.randint(5, 60)
            runs = int(balls * np.random.uniform(0.6, 1.8))
            fours = min(runs // 4, np.random.randint(0, 9))
            sixes = min(runs // 6, np.random.randint(0, 5))
        else:
            runs, balls, fours, sixes = 0, 0, 0, 0

        if role in ("Bowler", "All-rounder"):
            overs = int(np.random.choice([0, 2, 3, 4]))
            wickets = int(np.random.randint(0, 4)) if overs > 0 else 0
            conceded = int(overs * np.random.uniform(5, 11))
        else:
            overs, wickets, conceded = 0, 0, 0

        rows.append([match_id, date, opponent, player, profile["team"], role, runs, balls,
                     fours, sixes, overs, wickets, conceded])

df = pd.DataFrame(rows, columns=[
    "match_id", "date", "opponent", "player", "team", "role", "runs",
    "balls_faced", "fours", "sixes", "overs_bowled", "wickets", "runs_conceded"])

os.makedirs("data", exist_ok=True)
df.to_csv("data/matches.csv", index=False)
print("Data ban gaya!", df.shape)
print(df.head())
