from flask import Flask, render_template
import requests
import os

app = Flask(__name__)

# Función para leer startups ya notificadas
def leer_startups_enviadas():
    if not os.path.exists("enviadas.txt"):
        return set()
    with open("enviadas.txt", "r") as f:
        return set(line.strip() for line in f.readlines())

# Función para registrar nueva startup como enviada
def registrar_startup(nombre):
    with open("enviadas.txt", "a") as f:
        f.write(nombre + "\n")

# Función de alerta por Telegram
def enviar_alerta(nombre, sector, enlace):
    TOKEN = "7506722284:AAGd72I5TMnWVOyft0XdkARISQM2cRxzCfc"
    CHAT_ID = "6368490260"
    mensaje = f"🚨 NUEVA STARTUP DETECTADA 🚀\n\nNombre: {nombre}\nSector: {sector}\nMás info: {enlace}"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mensaje
    }

    try:
        response = requests.post(url, data=payload)
        print("✅ Respuesta de Telegram:", response.status_code, response.text)
    except Exception as e:
        print("❌ Error al enviar mensaje:", str(e))

# Simulación de startups detectadas
startups = [
    {
        "nombre": "DeepNova AI",
        "sector": "Inteligencia Artificial",
        "fecha": "2025-04-17",
        "enlace": "https://producthunt.com/posts/deepnova-ai",
        "nivel": "🔴"
    },
    {
        "nombre": "GreenCore Battery",
        "sector": "Energía",
        "fecha": "2025-04-17",
        "enlace": "https://producthunt.com/posts/greencore-battery",
        "nivel": "🟠"
    }
]

@app.route("/")
def index():
    return render_template("index.html", startups=startups)

@app.route("/test-alerta")
def test_alerta():
    enviadas = leer_startups_enviadas()
    nuevas = [s for s in startups if s["nombre"] not in enviadas]

    for s in nuevas:
        enviar_alerta(s["nombre"], s["sector"], s["enlace"])
        registrar_startup(s["nombre"])

    if nuevas:
        return f"Se enviaron {len(nuevas)} nuevas alertas a Telegram"
    else:
        return "No hay startups nuevas para enviar"

@app.route("/reset-enviadas")
def reset_enviadas():
    if os.path.exists("enviadas.txt"):
        os.remove("enviadas.txt")
    return "Registro de startups notificadas reiniciado."

if __name__ == "__main__":
    app.run(debug=True)
