import pandas as pd
import requests
import sqlite3
import sys
import os
sys.path.append(os.getcwd())

from flask import Flask, request, g
from flask_cors import CORS
from flask_celeryext import FlaskCeleryExt
from utils.general_functions import add_extra_info, clean_extra_data
from celery.schedules import crontab
from flask_api.routes import main_routes


app = Flask(__name__)
CORS(app)

flask_port = 5001

# Celery config
app.config['BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

# Celery beat config
app.config['beat_schedule'] = {
    'mercato_pick_rates': {
        'task': 'flask_api.app.mercato_pick_rates',
        'schedule': crontab(hour="0", minute="0"),
    }
}

# Initialize Celery
ext = FlaskCeleryExt(app)
celery = ext.celery

# Register routes
app.register_blueprint(main_routes)

def get_db():
	"""
	Connect to the database.

	:return: return the database connection
	"""
	db = getattr(g, '_database', None)
	if db is None:
		db = g._database = sqlite3.connect('flask_api/players_data/players_database.db')
	return db

@app.teardown_appcontext
def close_connection(exception):
	"""
	Close the database connection at the end of the request.

	:param exception:
	:return:
	"""
	db = getattr(g, '_database', None)
	if db is not None:
		db.close()

@app.before_request
def before_request():
	# Access query parameters as a dictionary
	args_dict = request.args.to_dict()

	# Check if the top_number is not too high, since celery task is only recording the top 25
	if args_dict.get("top_number") and int(args_dict.get("top_number")) > 25:
		args_dict["top_number"] = "25"

	# Store the args_dict in the Flask 'g' object
	g.args_dict = args_dict

@celery.task(name="flask_api.app.mercato_pick_rates")
def mercato_pick_rates():
	"""
	This task will request the top 25 players for each position and store them in the database.
	Done as a celery task because it requests one time per player the mpg api therefore not usable as a route.

	Runs every night at 00:00.

	:return: nothing
	"""
	con = sqlite3.connect("flask_api/players_data/players_database.db")
	cur = con.cursor()
	res = requests.get(f"http://localhost:{flask_port}/top_players?top_number=25&position=A,M,D,G")
	jdata = res.json()
	players_df = pd.DataFrame(player for player in jdata)
	extra_stats_bf = add_extra_info(players_df)
	players_df = clean_extra_data(extra_stats_bf, players_df)

	for index, row in players_df.iterrows():
		cur.execute("INSERT OR REPLACE INTO players (id, mercato_pr) VALUES (?, ?)", (row['pid'], row['mercatoPR']))
	con.commit()
	con.close()

if __name__ == "__main__":
	app.run(host="0.0.0.0", debug=False, port=flask_port)
