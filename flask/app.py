from flask import Flask, request, g
from routes import main_routes

app = Flask(__name__)

app.register_blueprint(main_routes)


@app.before_request
def before_request():
    # Access query parameters as a dictionary
    args_dict = request.args.to_dict()

    # Store the args_dict in the Flask 'g' object
    g.args_dict = args_dict


if __name__ == "__main__":
    app.run(debug=True)
