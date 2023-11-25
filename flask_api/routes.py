import pandas as pd
from flask import Blueprint, abort, g

from general_functions import (
	base_request,
	prettify_json,
	top_forward,
	top_backward,
	top_goal_keeper,
	top_midfielder,
)

main_routes = Blueprint("main", __name__)


@main_routes.route("/")
def main():
	"""
	Just a test route to check if the api is working

	:return:
	"""
	return "True"


@main_routes.route("/top_forward")
def r_top_forward():
	"""
	Endpoint to get the top forwards

	:return: json object with the top forwards
	"""
	args_dict = g.get("args_dict", {})

	try:
		top_number = int(args_dict.get("top_number"))
	except:
		abort(403, "top_number arg must be defined in the request an be an integer")
	else:
		clean_df = base_request(
			int(top_number), args_dict.get("ranking_criteria", "averagePoints")
		)
		result = top_forward(clean_df)
		return prettify_json(result)


@main_routes.route("/top_backward")
def r_top_backward():
	"""
	Endpoint to get the top defenders

	:return: json object with the top defenders
	"""
	args_dict = g.get("args_dict", {})

	try:
		top_number = int(args_dict.get("top_number"))
	except:
		abort(403, "top_number arg must be defined in the request an be an integer")
	else:
		clean_df = base_request(
			int(top_number), args_dict.get("ranking_criteria", "averagePoints")
		)
		result = top_backward(clean_df)
		return prettify_json(result)


@main_routes.route("/top_goal")
def r_top_goal():
	"""
	Endpoint to get the top goalkeepers

	:return: json object with the top goalkeepers
	"""
	args_dict = g.get("args_dict", {})

	try:
		top_number = int(args_dict.get("top_number"))
	except:
		abort(403, "top_number arg must be defined in the request an be an integer")
	else:
		clean_df = base_request(
			int(top_number), args_dict.get("ranking_criteria", "averagePoints")
		)
		result = top_goal_keeper(clean_df)
		return prettify_json(result)


@main_routes.route("/top_midfielder")
def r_top_midfielder():
	"""
	Endpoint to get the top midfielders

	:return: json object with the top midfielders
	"""
	args_dict = g.get("args_dict", {})

	try:
		top_number = int(args_dict.get("top_number"))
	except:
		abort(403, "top_number arg must be defined in the request an be an integer")
	else:
		clean_df = base_request(
			int(top_number), args_dict.get("ranking_criteria", "averagePoints")
		)
		result = top_midfielder(clean_df)
		return prettify_json(result)


@main_routes.route("/top_players")
def r_top_players():
	"""
	Endpoint to get the top players depending on the position requested in the args.
	If no position is requested, the top forwards are returned.

	:return: json object with the top players
	"""
	args_dict = g.get("args_dict", {})
	try:
		top_number = int(args_dict.get("top_number"))
	except:
		abort(403, "top_number arg must be defined in the request an be an integer")
	else:
		clean_df = base_request(
			int(top_number), args_dict.get("ranking_criteria", "averagePoints")
		)
		position_wanted = []
		if args_dict.get("position"):
			for position in args_dict.get("position").split(","):
				match position:
					case "A":
						position_wanted.append(top_forward(clean_df))
					case "D":
						position_wanted.append(top_backward(clean_df))
					case "M":
						position_wanted.append(top_midfielder(clean_df))
					case "G":
						position_wanted.append(top_goal_keeper(clean_df))
		if position_wanted:
			result = pd.concat(position_wanted)
		else:
			result = top_forward(clean_df)
		return prettify_json(result)
