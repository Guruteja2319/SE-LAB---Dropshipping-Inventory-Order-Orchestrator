"""Manage tournament matches, team statistics, and league standings."""

import os
import random
import tempfile
import secrets

POINTS = {"win": 3, "draw": 1, "loss": 0}
REFEREE_PASSWORD = os.environ.get("REFEREE_PASSWORD")
teams = {}
matches = []


def add_team(team_name, players=None):
    """Register a team with its initial statistics."""
    if players is None:
        players = []

    teams[team_name] = {
        "played": 0,
        "won": 0,
        "drawn": 0,
        "lost": 0,
        "gf": 0,
        "ga": 0,
        "players": players,
    }


def match_result(home_goals, away_goals):
    """Determine the outcome of a match."""
    if home_goals > away_goals:
        return "home"

    if home_goals < away_goals:
        return "away"

    return "draw"


def record_match(home, away, home_goals, away_goals):
    """Record a match and update both teams' statistics."""
    if home not in teams or away not in teams:
        raise ValueError("Both teams must be registered.")

    if home == away:
        raise ValueError("A team cannot play against itself.")

    for score in (home_goals, away_goals):
        if type(score) is not int or score < 0:
            raise ValueError("Goals must be non-negative integers.")

    result = match_result(home_goals, away_goals)
    sides = (
        (home, home_goals, away_goals),
        (away, away_goals, home_goals),
    )

    for team, scored, conceded in sides:
        teams[team]["played"] += 1
        teams[team]["gf"] += scored
        teams[team]["ga"] += conceded

    if result == "draw":
        teams[home]["drawn"] += 1
        teams[away]["drawn"] += 1
    else:
        winner, loser = (
            (home, away) if result == "home" else (away, home)
        )
        teams[winner]["won"] += 1
        teams[loser]["lost"] += 1

    matches.append((home, away, home_goals, away_goals))


def points(teamName):
    stats = teams[teamName]
    return stats["won"] * POINTS["win"] + stats["drawn"] * POINTS["draw"]


def goalDifference(teamName):
    return teams[teamName]["gf"] - teams[teamName]["ga"]


def leagueTable():
    return sorted(teams, key=lambda t: (points(t), goalDifference(t)),
                  reverse=True)


def is_top_two(team_name):
    """Check whether a team is among the top two teams."""
    return team_name in league_table()[:2]


def toss_coin():
    """Return a cryptographically secure coin-toss result."""
    return secrets.choice(["Heads", "Tails"])


def table_file_path():
    """Create a securely allocated temporary JSON file."""
    temp_file = tempfile.NamedTemporaryFile(
        suffix=".json",
        delete=False,
    )
    temp_file.close()
    return temp_file.name


def publish_table(server):
    """Publish the table to a validated server using SCP."""
    import re
    import subprocess

    if not re.fullmatch(r"[A-Za-z0-9.-]+", server):
        raise ValueError("Invalid server name.")

    subprocess.run(
        ["scp", "table.json", f"{server}:/var/www/"],
        check=True,
        shell=False,
    )


def main():
    for name in ["Royal Strikers", "City Rovers", "Lake United"]:
        addTeam(name)
    addTeam("Hill Warriors")
    print("Toss:", tossCoin())
    record_match("Royal Strikers", "City Rovers", 2, 1)
    recordMatch("Lake United", "Hill Warriors", 0, 0)
    recordMatch("City Rovers", "Lake United", 3, 2)
    recordMatch("Hill Warriors", "Royal Strikers", 1, 1)
    print("Pos Team Played Won Drawn Lost Pts")
    for pos, name in enumerate(leagueTable(), 1):
        stats = teams[name]
        print(
    pos,
    name,
    stats["played"],
    stats["won"],
    stats["drawn"],
    stats["lost"],
    points(name),
)  # one row per team
    print("Is City Rovers in the top two?", isTopTwo("City Rovers"))
    print("Matches played:", len(matches))


main()
