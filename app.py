from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import json

app = Flask(__name__)
DATA_FILE = "startups.json"

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
    if not os.path.exists(DATA_FILE):
        return "No se han detectado startups aún. Ejecuta /test-alerta primero."

    with open(DATA_FILE, "r") as f:
        startups = json.load(f)
    return render_template("index.html", startups=startups)

@app.route("/test-alerta")
def test_alerta():
    startups = obtener_startups_ph()
    with open(DATA_FILE, "w") as f:
        json.dump(startups, f, indent=2, ensure_ascii=False)
    return f"✅ Startups actualizadas ({len(startups)} detectadas)."

@app.route("/reset-enviadas")
def reset_enviadas():
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    return "🧹 Historial de startups reiniciado."

if __name__ == "__main__":
    app.run(debug=True)
