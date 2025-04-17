from flask import Flask, render_template, request
import datetime

app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(debug=True)
