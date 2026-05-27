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
    print("Enviando DM de producción...")
    url = "https://graph.facebook.com/v25.0/me/messages"

    # Texto compacto (Menos de 1000 caracteres) manteniendo toda la información vital
    texto_mensaje = (
        "👋 ¡Hola! Qué alegría tu interés en Laguna Bella, San Carlos. 🏡✨\n"
        "Alquilamos las cabañas Blue y Bella. Aquí tienes los detalles:\n\n"
        "📍 UBICACIÓN: Laguna de San Carlos, KM 17. Búscanos en Waze/Google Maps como 'Laguna Bella, San Carlos' (a 1h 40m de la ciudad, 30m de Coronado).\n\n"
        "🛏️ CABAÑAS: Tienen 2 camas (1 Queen y 1 doble deslizable), TV, terraza con asador y hamacas y espectacular vista al mar y montañas, Jacuzzi con hidromasaje y cocina equipada (estufa, nevera pequeña, vajilla, cubiertos, vasos, tazas, cafetera). \n\n"
        "🌲 ALREDEDORES: Lago (10 min), Río Teta (7 min), sendero al Cerro Picacho (30-45 min caminando), playas y súpermercados a 30 min.\n\n"
        "💰 PRECIOS:\n"
        "• 1 persona: $120 | 2 personas: $125\n"
        "• 3 personas: $130 | 4 personas: $135\n\n"
        "📲 RESERVAS: En Airbnb o directo con Jorge Torres al 📞 6250-1227 (Yappy, transferencia o tarjeta).\n\n"
        "¿Te gustaría verificar disponibilidad para alguna fecha? 👇"
    )

    payload = {
        "recipient": {
            "id": user_id
        },
        "message": {
            "text": texto_mensaje
        }
    }

    params = {
        "access_token": ACCESS_TOKEN
    }

    response = requests.post(url, json=payload, params=params)
    print("RESPUESTA DM API:")
    print(response.text)


@app.route("/")
def home():
    return "Bot Instagram funcionando."


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
