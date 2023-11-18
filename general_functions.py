"""
This file contains functions that are both used by flask app and the scripting app
"""
import json
import requests
import pandas as pd
import numpy as np
from flask import abort

from unidecode import unidecode


def cleaning(dirty_df: pd.DataFrame):
    df_stats = pd.DataFrame(stat for stat in dirty_df["stats"].values)

    # Get important columns from the original DF
    # Aggregating data from columns to create the full name of the player
    df_stats["playerFullName"] = dirty_df.agg(
        lambda x: f"{x['lastName']} {x['firstName'] or ''}", axis=1
    )
    # Remove accented characters
    df_stats["playerFullName"] = df_stats["playerFullName"].apply(
        lambda x: unidecode(x)
    )
    df_stats["position"] = dirty_df["position"].replace(
        {1: "G", 2: "D", 3: "M", 4: "A"}
    )
    df_stats["pid"] = dirty_df["id"]
    df_stats["participation"] = np.round(
        df_stats["totalPlayedMatches"] / df_stats["totalMatches"] * 100, 2
    )
    df_stats["quotation"] = dirty_df["quotation"]

    # Drop useless ones and NA ratings. Also converting as integer to avoid weird display in dataframe
    df_stats = df_stats.drop(
        ["nextMatch", "quotationTrend", "averagePointsTrend"], axis=1
    )
    df_stats = df_stats.dropna(subset=["averageRating", "averagePoints"])
    df_stats = df_stats.astype(
        {
            "averagePoints": "int32",
            "totalGoals": "int32",
            "totalStartedMatches": "int32",
            "totalPlayedMatches": "int32",
        }
    )

    return df_stats


def base_request(top_number: int = 10, ranking_criteria: str = "averagePoints"):
    """
    Calls basic mpg data, cleans it and returns it
    :arg top_number: the number of player wanted from the dataframe (aka top 10 best players)
    :param ranking_criteria: col name from the dataframe that will be used to rank players
    :return: complete dataframe
    """
    base_url = (
        "https://api.mpg.football/api/data/championship-players-pool/2?season=2023"
    )
    res = requests.get(base_url, verify=False)
    jdata = res.json()

    pd.set_option("float_format", "{:.2f}".format)

    df = pd.DataFrame(player for player in jdata["poolPlayers"])
    clean_df = cleaning(df)
    if ranking_criteria not in clean_df.columns.values:
        abort(
            403,
            f"The ranking criteria has to be none or a column in the dataframe: {clean_df.columns.values}",
        )
    return top_pos(clean_df, top_number, ranking_criteria)


def prettify_json(dataf: pd.DataFrame):
    """
    Function to create a clean response for the flask api, converts dataframe to a pretty json
    :param dataf: original dataframe
    :return: pretty json
    """
    df_json = dataf.to_json(orient="records", indent=2, force_ascii=False)

    return json.loads(df_json)


def top_pos(dataf: pd.DataFrame, numb: int, ranking_criteria: str = "averagePoints"):
    """
    Restrict the dataset to a certain number of top players based on one customizable criteria.
    :param dataf: player dataframe cleaned
    :param numb: number of players to return
    :param ranking_criteria: col name from the dataframe that will be used to rank players
    :return: dataframe containing top players ranked by the criteria
    """
    top_points_by_pos = (
        dataf[dataf["participation"] > 75]
        .groupby("position")
        .apply(lambda group: group.nlargest(numb, [ranking_criteria, "averagePoints"]))
    )
    return top_points_by_pos


def top_forward(top_players: pd.DataFrame):
    return top_players[top_players["position"] == "A"]


def top_backward(top_players: pd.DataFrame):
    return top_players[top_players["position"] == "D"]


def top_midfielder(top_players: pd.DataFrame):
    return top_players[top_players["position"] == "M"]


def top_goal_keeper(top_players: pd.DataFrame):
    return top_players[top_players["position"] == "G"]
