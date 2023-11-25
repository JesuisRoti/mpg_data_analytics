"""
This file contains functions that are both used by flask_api app and the scripting app
"""
import json
import requests
import pandas as pd
import numpy as np
import sqlite3
from flask import abort

from unidecode import unidecode


def cleaning(dirty_df: pd.DataFrame):
	"""
	Cleans the dataframe from useless columns and add some new ones
	:param dirty_df: Dataframe containing data from the mpg api with full stats.
	:return: clean dataframe with only the columns we want
	"""

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
	df_stats['averageRating'] = df_stats['averageRating'].round(2)
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
	:return: pd.DataFrame('averageRating' 'averagePoints' 'totalGoals' 'totalMatches', 'totalStartedMatches' 'totalPlayedMatches' 'playerFullName' 'position', 'pid' 'participation' 'quotation')
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
	Function to create a clean response for the flask_api api, converts dataframe to a pretty json
	:param dataf: original dataframe
	:return: pretty json
	"""
	df_json = dataf.to_json(orient="records", indent=2, force_ascii=False)

	return json.loads(df_json)


def top_pos(dataf: pd.DataFrame, numb: int, ranking_criteria: str = "averagePoints"):
	"""
	Restrict the dataset to a certain number of top players based on one customizable criteria.

	Also adds the mercato pick rate for each player based on the database. Done like this to avoid making a request for
	each player. Instead, it is done as a periodic task. The issue could be that some players are not in the database this
	is why the for loop is here.

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
	pids = top_points_by_pos["pid"].values
	con = sqlite3.connect('flask_api/players_data/players_database.db')

	cur = con.cursor()

	mercato_pr_list = []
	for pid in pids:
		cur.execute("SELECT COALESCE(mercato_pr, 0) FROM players WHERE id = ?", (pid,))
		result = cur.fetchone()
		if result:
			mercato_pr_list.append(result[0])
		else:
			mercato_pr_list.append(0)
	con.close()
	top_points_by_pos["mercatoPR"] = mercato_pr_list
	return top_points_by_pos


def top_forward(top_players: pd.DataFrame):
	"""
	Filter the dataframe to only keep the forwards

	:param top_players: Original dataframe containing all the players
	:return: filtered dataframe
	"""
	return top_players[top_players["position"] == "A"]


def top_backward(top_players: pd.DataFrame):
	"""
	Filter the dataframe to only keep the defenders

	:param top_players: Original dataframe containing all the players
	:return: filtered dataframe
	"""
	return top_players[top_players["position"] == "D"]


def top_midfielder(top_players: pd.DataFrame):
	"""
	Filter the dataframe to only keep the midfielders

	:param top_players: Original dataframe containing all the players
	:return: filtered dataframe
	"""
	return top_players[top_players["position"] == "M"]


def top_goal_keeper(top_players: pd.DataFrame):
	"""
	Filter the dataframe to only keep the goalkeepers

	:param top_players: Original dataframe containing all the players
	:return: filtered dataframe
	"""
	return top_players[top_players["position"] == "G"]


def add_extra_info(player_dataframe: pd.DataFrame):
	"""
	This function will request mpg for more data about specific players

	:param player_dataframe: dataframe containing basic information about top players
	:return: big json object containing all data for all the players in the dataframe
	"""
	players_id = player_dataframe["pid"]
	url = "https://api.mpg.football/api/data/championship-player-stats/"
	players_full_stats_obj = {}

	for player in players_id.values:
		try:
			res = requests.get(f"{url}{player}/2023", timeout=300)
			data = res.json()
		except:
			print("Error during get request")
		else:
			players_full_stats_obj[player] = data
	return players_full_stats_obj


def clean_extra_data(fs_players: dict, original_dataframe: pd.DataFrame):
	"""
	Function to clean and select valuables json attributes for players in the extra data received.
	Extra data often means the specific data retrieved for one player from add_extra_info function.

	:param fs_players: full stats players dictionary
	:param original_dataframe: dataframe containing basic information about top players
	:return: dataframe
	"""
	df_fs_players = pd.DataFrame(fs_players).transpose()
	df_fs_players = df_fs_players["championships"]
	mercato_pick_rates = []
	for i in df_fs_players:
		# retrieve the main key
		key = list(i.keys())[0]
		main_stats = i[key]
		mercato_pick_rates.append(main_stats.get("mercatoPickRate", 0))

	try:
		original_dataframe["mercatoPR"] = mercato_pick_rates
	except Exception as e:
		print(e)
	return original_dataframe
