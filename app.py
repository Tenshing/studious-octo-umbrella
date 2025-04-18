from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

app = Flask(__name__)

def leer_startups_enviadas():
    if not os.path.exists("enviadas.txt"):
        return set()
    with open("enviadas.txt", "r") as f:
        return set(line.strip() for line in f.readlines())

def registrar_startup(nombre):
    with open("enviadas.txt", "a") as f:
        f.write(nombre + "\n")

def enviar_alerta(nombre, sector, enlace, sitio_web):
    TOKEN = "7506722284:AAGd72I5TMnWVOyft0XdkARISQM2cRxzCfc"
    CHAT_ID = "6368490260"
    mensaje = f"🚨 NUEVA STARTUP DETECTADA 🚀\n\nNombre: {nombre}\nSector: {sector}\nSitio: {sitio_web}\nMás info: {enlace}"
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

def obtener_sitio_web(url_post):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url_post, headers=headers, timeout=10)
        soup = BeautifulSoup(r.content, "html.parser")
        link_tag = soup.find("a", attrs={"data-test": "post-visit-website-button"})
        if link_tag and link_tag.get("href"):
            return link_tag["href"]
    except:
        return "No encontrado"
    return "No encontrado"

def obtener_startups_ph():
    url = "https://www.producthunt.com"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, "html.parser")

    tarjetas = soup.find_all("a", href=True)
    startups = []

    for tag in tarjetas:
        href = tag["href"]
        if "/posts/" in href and tag.text.strip():
            nombre = tag.text.strip()
            enlace_post = "https://www.producthunt.com" + href
            sitio_web = obtener_sitio_web(enlace_post)
            startups.append({
                "nombre": nombre,
                "enlace": enlace_post,
                "sitio_web": sitio_web,
                "sector": "Por clasificar",
                "fecha": datetime.today().strftime("%Y-%m-%d"),
                "nivel": "🟢"
            })

    unicos = []
    nombres_vistos = set()
    for s in startups:
        if s["nombre"] not in nombres_vistos:
            unicos.append(s)
            nombres_vistos.add(s["nombre"])

    return unicos[:5]

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
        enviar_alerta(s["nombre"], s["sector"], s["enlace"], s["sitio_web"])
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
