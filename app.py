from flask import Flask, render_template
import datetime

app = Flask(__name__)

# Simulación de startups extraídas desde Product Hunt
startups = [
    {
        "nombre": "NovaGraph AI",
        "sector": "Inteligencia Artificial",
        "fecha_fundacion": "2024",
        "pais": "Estados Unidos",
        "fecha_deteccion": datetime.date.today().isoformat(),
        "enlace_producthunt": "https://www.producthunt.com/posts/novagraph-ai"
    },
    {
        "nombre": "EcoCharge Labs",
        "sector": "Energía",
        "fecha_fundacion": "2023",
        "pais": "Alemania",
        "fecha_deteccion": datetime.date.today().isoformat(),
        "enlace_producthunt": "https://www.producthunt.com/posts/ecocharge-labs"
    }
]

@app.route("/")
def index():
    return render_template("index.html", startups=startups)

if __name__ == "__main__":
    app.run(debug=True)
