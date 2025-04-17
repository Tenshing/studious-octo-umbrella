from flask import Flask, render_template
import requests
import datetime

app = Flask(__name__)

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
    requests.post(url, data=payload)

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

# Alerta automática al iniciar (simulación)
for startup in startups:
    enviar_alerta(startup["nombre"], startup["sector"], startup["enlace"])

@app.route("/")
def index():
    return render_template("index.html", startups=startups)

if __name__ == "__main__":
    app.run(debug=True)
