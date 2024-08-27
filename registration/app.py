from crypt import methods
from multiprocessing import synchronize
from flask import Flask, jsonify, make_response, render_template, request, Response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import sqlalchemy
import hashlib
from sqlalchemy.sql import text
from flask_socketio import SocketIO, send, emit
from time import time
from statistics import mean
from datetime import datetime
from time import sleep

app = Flask(__name__)
CORS(app)

db_name = "sensor_reg.db"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_name
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["FLASK_ENV"] = "development"
app.config["SECRET_KEY"] = "banana"
app.config["DEBUG"] = True
db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

users = {}

class Devices(db.Model):
    email = db.Column("EMAIL", db.Text, primary_key=True)
    dev_id = db.Column("DEV_ID", db.Text, primary_key=False)
    location = db.Column("LOCATION", db.Text, primary_key=False)
    verified = db.Column("VERIFIED", db.Integer, primary_key=False)
    geo_id = db.Column("GEO_ID", db.Text, primary_key=False)

    def __init__(self, email, dev_id):
        self.email = email
        self.dev_id = dev_id


db.create_all()


@app.route("/", methods=["POST", "GET"])
def serveHTML():
    return render_template("register.html")


@app.route("/register", methods=["POST", "GET"])
def deviceLookup():
    dev = ""
    if request.method == "POST":

        print("THIS:", request.form)

        userEmail = request.form["userEmail"]
        dev_uuid = request.form["uuid"]
        location = request.form["location"]
        dev = Devices.query.filter_by(email=userEmail).first()

        if dev is not None:
            if dev.dev_id == dev_uuid:
                dev.location = location
                dev.geo_id = hashlib.sha256(
                    dev.email.encode("utf-8")
                    + dev.dev_id.encode("utf-8")
                    + dev.location.encode("utf-8")
                ).hexdigest()
                dev.verified = 0
                db.session.commit()
                return make_response(jsonify({"geo_id": dev.geo_id}), 200)

            else:
                return "Nope"


@app.route("/register/<path:sensor_id>", methods=["POST", "GET"])
def devLoc(sensor_id):
    print(request)
    dev = Devices.query.filter_by(dev_id=sensor_id).first()
    print(dev.geo_id)
    if request.method == "POST":
        geo_id = request.form["id"]

        if geo_id == dev.geo_id:
            return "Registration complete!"
        else:
            return "Something went wrong, please try again"

    return "Hello there"

@socketio.on("reg", namespace="/register")
def receive_username(username):
    print(request.sid)
    users[request.sid] = {
        "dev_id": username["dev_id"],
        "email": username["email"],
        "loc": username["loc"],
        "start": [],
        "stop": [],
        "counter": 0,
        "latency": -1,
    }
    print("Username added!", request.sid)

    dev = ""

    print(request.method)
    # if request.method == "POST":

    # userEmail = request.form["userEmail"]
    # dev_uuid = request.form["uuid"]
    # location = request.form["location"]
    dev = Devices.query.filter_by(email=users[request.sid]["email"]).first()

    if dev is not None:
        if dev.dev_id == users[request.sid]["dev_id"]:
            dev.location = users[request.sid]["loc"]
            dev.geo_id = hashlib.sha256(http
                + dev.dev_id.encode("utf-8")
                + dev.location.encode("utf-8")
            ).hexdigest()
            dev.verified = 0
            db.session.commit()
            # make_response(jsonify({"geo_id": dev.geo_id}), 200)

        # else:
            # return "Nope"

    start = time()
    users[request.sid]["start"].append(start)
    emit("ping", "Hello, Clarice", room=request.sid)

def esp_element_diff_to_csv(nodes):
    with open("L_sen.csv", "a") as this:
        for i in range(0, len(nodes) - 1):
            this.write(str(nodes[i + 1] - nodes[i]) + ",")

esp_cnt = 0
esp_stamp_set = []
@socketio.on("esp8266")
def pong_esp(username):
    global esp_cnt
    global esp_stamp_set
    esp_stamp_set.append(datetime.now().timestamp())
    emit("esp8266_listen","", room=request.sid)
    # print(request.sid)
    # print(datetime.now().timestamp())

    esp_cnt += 1

    if esp_cnt >= 11:
        esp_cnt = 0
        print(esp_stamp_set)
        esp_element_diff_to_csv(esp_stamp_set)
        esp_stamp_set.clear()
        sleep(30)



def element_diff_to_csv(nodes):
    with open("L_rd.csv", "a") as this:
        for i in range(0, len(nodes) - 1):
            this.write(str(nodes[i + 1] - nodes[i]) + ",")

cnt = 0
stamp_set = []
@socketio.on("ping_measure")
def ping_js():
    global cnt
    global stamp_set
    stamp_set.append(datetime.now().timestamp())
    emit("pong_measure","", room=request.sid)

    cnt += 1

    if cnt >= 11:
        cnt = 0
        print(stamp_set)
        element_diff_to_csv(stamp_set)
        stamp_set.clear()
        sleep(30)


# @socketio.on("pong_measure")
# def pong_js(username):
#     print(request.sid)


@socketio.on("pong", namespace="/register")
def receive_username(username):
    print("STOP")
    stop = time()
    users[request.sid]["stop"].append(stop)

    if users[request.sid]["counter"] != 4:
        start = time()
        users[request.sid]["start"].append(start)
        emit("ping", "Hello, Clarice", room=request.sid)
        users[request.sid]["counter"] += 1
    else:
        users[request.sid]["counter"] = 0
        users[request.sid]["latency"] = mean(users[request.sid]["stop"]) - mean(
            users[request.sid]["start"]
        )
        users[request.sid]["stop"].clear()
        users[request.sid]["start"].clear()

        dev = Devices.query.filter_by(email=users[request.sid]["email"]).first()

        emit("id", dev.geo_id, room=request.sid)
        print(users)


if __name__ == "__main__":
    # socketio.run(app, port=5001, host="0.0.0.0")
    socketio.run(app, port=5002, host="0.0.0.0")
    # app.run(host="0.0.0.0.", port=1995, ssl_context=("cert.pem", "key.pem"), debug=True)
