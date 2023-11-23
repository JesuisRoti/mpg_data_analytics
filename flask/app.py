from flask import Flask, request, g
from routes import main_routes
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.register_blueprint(main_routes)


@app.before_request
def before_request():
    # Access query parameters as a dictionary
    args_dict = request.args.to_dict()

    # Store the args_dict in the Flask 'g' object
    g.args_dict = args_dict


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5001)
