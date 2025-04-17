from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup
from datetime import datetime
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

# Función para enviar alerta por Telegram
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
        print("✅ Telegram:", response.status_code, response.text)
    except Exception as e:
        print("❌ Error al enviar mensaje:", str(e))

# Scraping desde Product Hunt
def obtener_startups_ph():
    url = "https://www.producthunt.com/"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, "html.parser")

    productos = soup.select("ul li div div > a[href*='/posts/']")
    nombres = []
    for p in productos:
        nombre = p.text.strip()
        enlace = "https://www.producthunt.com" + p.get("href")
        if nombre and enlace:
            nombres.append({
                "nombre": nombre,
                "enlace": enlace,
                "sector": "Por clasificar",
                "fecha": datetime.today().strftime("%Y-%m-%d"),
                "nivel": "🟢"
            })
    return nombres[:5]  # Solo los primeros 5 para evitar sobrecarga

@app.route("/")
def index():
    startups = obtener_startups_ph()
    return render_template("index.html", startups=startups)

@app.route("/test-alerta")
def test_alerta():
    enviadas = leer_startups_enviadas()
    startups = obtener_startups_ph()
    nuevas = [s for s in startups if s["nombre"] not in enviadas]

    for s in nuevas:
        enviar_alerta(s["nombre"], s["sector"], s["enlace"])
        registrar_startup(s["nombre"])

    if nuevas:
        return f"🔔 Se enviaron {len(nuevas)} nuevas alertas a Telegram"
    else:
        return "✅ No hay startups nuevas por ahora"

@app.route("/reset-enviadas")
def reset_enviadas():
    if os.path.exists("enviadas.txt"):
        os.remove("enviadas.txt")
    return "🧹 Historial de startups reiniciado."

if __name__ == "__main__":
    app.run(debug=True)
