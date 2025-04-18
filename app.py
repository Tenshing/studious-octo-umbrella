import os
import requests
from flask import Flask, render_template
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

PH_TOKEN = os.getenv("PH_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Almacenamiento temporal de startups detectadas para evitar duplicados
startups_detectadas = set()


def obtener_startups_ph():
    url = "https://api.producthunt.com/v2/api/graphql"
    headers = {
        "Authorization": f"Bearer {PH_TOKEN}",
        "Content-Type": "application/json"
    }

    query = {
        "query": """
        {
          posts(order: VOTES, postedAfter: \"""" + datetime.now().strftime("%Y-%m-%d") + "T00:00:00Z\", first: 10) {
            edges {
              node {
                id
                name
                tagline
                createdAt
                website
                slug
                topics(first: 1) {
                  edges {
                    node {
                      name
                    }
                  }
                }
              }
            }
          }
        }
        """
    }

    response = requests.post(url, json=query, headers=headers)
    data = response.json()

    startups = []
    for post in data.get("data", {}).get("posts", {}).get("edges", []):
        node = post["node"]
        nombre = node["name"]
        if nombre in startups_detectadas:
            continue
        startups_detectadas.add(nombre)

        startups.append({
            "nombre": nombre,
            "sector": node["topics"]["edges"][0]["node"]["name"] if node["topics"]["edges"] else "Desconocido",
            "pais": "Desconocido",
            "fundacion": node["createdAt"][:4],
            "detectada": datetime.now().strftime("%Y-%m-%d"),
            "descripcion": node["tagline"],
            "enlace_ph": f"https://www.producthunt.com/posts/{node['slug']}",
            "enlace_cb": f"https://www.crunchbase.com/discover/organization.companies/field/organizations/num_employees_enum/{nombre.replace(' ', '-')}"
        })

        # Enviar alerta por Telegram
        enviar_alerta_telegram(startups[-1])

    return startups


def enviar_alerta_telegram(startup):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return

    mensaje = f"🚨 *NUEVA STARTUP DETECTADA* 🚀\n\n" \
              f"*Nombre:* {startup['nombre']}\n" \
              f"*Sector:* {startup['sector']}\n" \
              f"*Detectada:* {startup['detectada']}\n" \
              f"\n[Ver en Product Hunt]({startup['enlace_ph']}) | [Ver en Crunchbase]({startup['enlace_cb']})"

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensaje,
        "parse_mode": "Markdown"
    }

    try:
        requests.post(url, data=payload)
    except:
        pass


@app.route("/")
def index():
    startups = obtener_startups_ph()
    return render_template("index.html", startups=startups)


if __name__ == "__main__":
    app.run(debug=True)
