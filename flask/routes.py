from flask import Blueprint, request, abort, g
import pandas as pd

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
	return "True"


@main_routes.route("/top_forward")
def r_top_forward():
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
	args_dict = g.get("args_dict", {})

	try:
		top_number = int(request.args.get("top_number"))
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
	args_dict = g.get("args_dict", {})

	try:
		top_number = int(request.args.get("top_number"))
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
	args_dict = g.get("args_dict", {})
	try:
		top_number = int(request.args.get("top_number"))
	except:
		abort(403, "top_number arg must be defined in the request an be an integer")
	else:
		clean_df = base_request(
			int(top_number), args_dict.get("ranking_criteria", "averagePoints")
		)
		position_wanted = []
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
