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

    # Texto resumido, scannable y optimizado para un solo DM en Instagram
    texto_mensaje = (
        "👋 ¡Hola! Qué alegría tu interés en nuestras cabañas en Laguna Bella, San Carlos. 🏡✨\n\n"
        "Actualmente alquilamos la cabaña Blue y la cabaña Bella. Aquí tienes los detalles principales:\n\n"
        "📍 UBICACIÓN: Laguna de San Carlos, Vía Principal KM 17 (Búscanos en Waze/Google Maps como 'Laguna Bella, San Carlos'). A 1h 40min de la ciudad y 30min de Coronado.\n\n"
        "🛏️ CABAÑAS: Cuentan con 2 camas (1 Queen y 1 doble deslizable), TV, cocina equipada (estufa, nevera pequeña, vajilla, utensilios, cafetera) y un espectacular Jacuzzi con hidromasaje. *Cabaña Blue incluye microondas.\n\n"
        "🌲 ACTIVIDADES CERCANAS: Lago a 10 min, balneario Río Teta a 7 min, sendero al Cerro Picacho (30-45 min caminando), playas y restaurantes a 30 min.\n\n"
        "💰 PRECIOS POR NOCHE:\n"
        "• 1 persona: $120\n"
        "• 2 personas: $125\n"
        "• 3 personas: $130\n"
        "• 4 personas: $135\n\n"
        "⏰ HORARIOS: Check-in máximo 3:00 PM | Check-out mínimo 12:00 PM (Horario flexible según disponibilidad).\n\n"
        "📲 RESERVAS Y PAGO: Puedes reservar en Airbnb o directo conmigo, Jorge Torres, al 📞 6250-1227. Aceptamos transferencia bancaria, Yappy y tarjeta de crédito.\n\n"
        "¿Tienes alguna pregunta adicional o te gustaría verificar disponibilidad para alguna fecha? 👇"
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
