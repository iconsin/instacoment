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

    print("========== WEBHOOK RECIBIDO ==========")
    print(data)

    try:

        for entry in data.get("entry", []):

            for change in entry.get("changes", []):

                if change.get("field") == "comments":

                    value = change.get("value", {})

                    comentario = value.get("text")
                    comment_id = value.get("id")

                    from_data = value.get("from", {})
                    user_id = from_data.get("id")
                    username = from_data.get("username")

                    print(f"Comentario recibido: {comentario}")
                    print(f"Usuario: {username}")
                    print(f"User ID: {user_id}")
                    print(f"Comment ID: {comment_id}")

                    # Evitar responder a comentarios propios
                    if username == "enlagunabella":
                        print("Comentario propio ignorado.")
                        continue

                    # Responder comentario público
                    responder_comentario(comment_id)

                    # Enviar DM automático
                    enviar_dm(user_id)

    except Exception as e:
        print("ERROR:")
        print(str(e))

    return "ok", 200


def responder_comentario(comment_id):

    print("Respondiendo comentario...")

    url = f"https://graph.facebook.com/v25.0/{comment_id}/replies"

    payload = {
        "message": "📩 Te enviamos un mensaje privado con más información.",
        "access_token": ACCESS_TOKEN
    }

    response = requests.post(url, data=payload)

    print("RESPUESTA COMENTARIO:")
    print(response.text)


def enviar_dm(user_id):

    print("Enviando DM...")

    IG_USER_ID = os.getenv("IG_USER_ID")

    url = f"https://graph.facebook.com/v25.0/{IG_USER_ID}/messages"

    payload = {
        "recipient": {
            "id": user_id
        },
        "message": {
            "text": "👋 Hola, gracias por comentar nuestra publicación.\n\n🏡 Con gusto te enviaremos toda la información."
        }
    }

    params = {
        "access_token": ACCESS_TOKEN
    }

    response = requests.post(
        url,
        json=payload,
        params=params
    )

    print("RESPUESTA DM:")
    print(response.text)


@app.route("/")
def home():
    return "Bot Instagram funcionando."


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
