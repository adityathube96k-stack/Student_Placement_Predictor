from flask import Flask, render_template, jsonify
from config import Config
from database.db import test_connection

app = Flask(__name__)
app.config.from_object(Config)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({
        "status": "success",
        "message": "Student_Placement_Predictor backend is running"
    })


@app.route("/db-test")
def db_test():
    connected, message = test_connection()

    return jsonify({
        "database": "connected" if connected else "not_connected",
        "message": message
    }), 200 if connected else 500


if __name__ == "__main__":
    app.run(debug=True)