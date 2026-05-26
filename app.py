from flask import Flask, request
import requests
import os

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

@app.route("/webhook", methods=["GET"])
def verify():
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if token == VERIFY_TOKEN:
        return challenge

    return "Token inválido", 403


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    print(data)

    try:
        for entry in data["entry"]:
            for change in entry["changes"]:

                if change["field"] == "comments":

                    comentario = change["value"]["text"]
                    comment_id = change["value"]["id"]

                    responder_comentario(comment_id)

    except Exception as e:
        print(e)

    return "ok", 200


def responder_comentario(comment_id):

    url = f"https://graph.facebook.com/v25.0/{comment_id}/replies"

    requests.post(url, data={
        "message": "📩 Te enviamos un mensaje privado con más información.",
        "access_token": ACCESS_TOKEN
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
