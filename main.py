import datetime

import io
import dateparser
import pytz
import requests
from flask import Flask, Response, make_response, send_file
import json

app = Flask(__name__)


@app.errorhandler(404)
def page_not_found(e):
    return ""


@app.errorhandler(500)
def error(e):
    return ""


@app.route("/prioq", methods=["GET"])
def prioq():
    if requests.get("https://api.2b2t.dev/prioq").text.replace("[", "").replace("]", "").split(",")[2].replace('"',
                                                                                                               "") == "null":
        return "优先列队目前无需等待"
    else:
        return "优先列队目前需等待 " + \
               requests.get("https://api.2b2t.dev/prioq").text.replace("[", "").replace("]", "").split(",")[
                   2].replace('"', "")


@app.route("/normalq", methods=["GET"])
def normaoQ():
    v = requests.get("https://2b2t.io/api/queue?last=true").text
    if v.replace("[[", "").replace("]]", "").split(",")[1].replace('"', "") == "null":
        return "普通列队目前没有队列"
    else:
        return "普通列队目前拥有 " + \
               v.replace("[[", "").replace("]]", "").split(",")[
                   1].replace('"', "") + " 名玩家在排队"


@app.route("/stats/<username>", methods=["GET"])
def stats(username):
    info = requests.get(f"https://api.2b2t.dev/stats?username={username}")
    if info.text == "[]":
        return "玩家名不可用"
    else:
        try:
            info = info.json()[0]
        except Exception as e:
            return "玩家名不可用"
        message = f"玩家名字: {info['username']}\n游玩次数: {info['joins']}\n击杀次数: {info['kills']}\n死亡次数: {info['deaths']}\nUUID: {info['uuid']}"
        return message


@app.route("/seen/<username>", methods=["GET"])
def seen(username):
    info = requests.get(f"https://api.2b2t.dev/seen?username={username}")
    if info.text == "[]":
        return "玩家名不可用"
    else:

        try:
            info = info.json()[0]
            seen_time = info["seen"]
        except Exception as e:
            return "玩家名不可用"

        date = dateparser.parse(f"{seen_time} EDT")
        date = date.timestamp()
        t = datetime.datetime.fromtimestamp(int(date), pytz.timezone('Asia/Shanghai')).strftime(
            '%Y-%m-%d %H:%M:%S')
        return f"{username} 的上次游玩时间\n北京时间 {t}"


@app.route("/lastdeath/<username>", methods=["GET"])
def last_death(username):
    info = requests.get(f"https://api.2b2t.dev/stats?lastdeath={username}")
    if info.text == "[]":
        return "玩家名不可用或该玩家没有被其他玩家击杀过"
    else:
        try:
            info = info.json()[0]
            seen_time = info["date"] + " " + info["time"]
        except Exception as e:
            return "查询发生错误"

        date = dateparser.parse(f"{seen_time} EDT")
        date = date.timestamp()
        t = datetime.datetime.fromtimestamp(int(date), pytz.timezone('Asia/Shanghai')).strftime(
            '%Y-%m-%d %H:%M:%S')
        return f"{username} 的上次死亡时间\n北京时间 {t}\n死亡消息: {info['message']}"


@app.route("/lastkill/<username>", methods=["GET"])
def last_kill(username):
    info = requests.get(f"https://api.2b2t.dev/stats?lastkill={username}")
    if info.text == "[]":
        return "玩家名不可用或该玩家没有击杀过其他玩家"
    else:
        try:
            info = info.json()[0]
            seen_time = info["date"] + " " + info["time"]
        except Exception as e:
            return "查询发生错误"

        date = dateparser.parse(f"{seen_time} EDT")
        date = date.timestamp()
        t = datetime.datetime.fromtimestamp(int(date), pytz.timezone('Asia/Shanghai')).strftime(
            '%Y-%m-%d %H:%M:%S')
        return f"{username} 的上次击杀时间\n北京时间 {t}\n击杀消息: {info['message']}"


@app.route("/livestatus", methods=["GET"])
def tps():
    un_read = requests.get("https://api.2b2t.dev/status").text
    un_read = un_read[1:len(un_read) - 1]
    split_index = un_read.index("]")
    server_info = un_read[0:split_index + 1]

    online_players = un_read[split_index + 2:len(un_read) - 1]
    online_players = online_players[1:len(online_players)]

    server_info = server_info[1:len(server_info) - 1].replace('"', "")
    online_players = json.loads(online_players)
    tps, player_count, ping, uptime = server_info.split(",")

    final_out = {
        "tps": float(tps),
        "player_count": int(player_count),
        "online_players": []
    }

    for u in online_players:
        final_out["online_players"].append({"username": u, "uuid": online_players[u]["uuid"]})

    return final_out


if __name__ == '__main__':
    app.run(port = 80)
