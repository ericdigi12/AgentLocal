from flask import Flask, request, jsonify, render_template_string
import threading
import time
import os

# ----------------------------
# Clés API (exemple ou via variables d'environnement)
# ----------------------------
CLE_API_CHATGPT = os.environ.get("CLE_API_CHATGPT", "sk-exemple")
TELEPHONE_NUMERO = os.environ.get("TELEPHONE_NUMERO", "+22665399292")
COURRIEL = os.environ.get("COURRIEL", "pare31881@gmail.com")
AGENT_SUPPORT_EMAIL = os.environ.get("AGENT_SUPPORT_EMAIL", "agent.commercial.ai@gmail.com")

# ----------------------------
# Flask App
# ----------------------------
app = Flask(__name__)

# ----------------------------
# Page web unique (template inline)
# ----------------------------
HTML_PAGE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Agent IA Interactif</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 30px; }
        #chat { border: 1px solid #ccc; padding: 10px; height: 300px; overflow-y: scroll; margin-bottom: 10px; }
        input, button { padding: 10px; font-size: 16px; }
    </style>
</head>
<body>
    <h1>Agent IA Interactif</h1>
    <div id="chat"></div>
    <input type="text" id="prompt" placeholder="Écris ton prompt ici..." size="50">
    <button onclick="sendPrompt()">Envoyer</button>

    <script>
        async function sendPrompt() {
            const prompt = document.getElementById('prompt').value;
            if (!prompt) return;

            const chatDiv = document.getElementById('chat');
            chatDiv.innerHTML += `<div><b>Vous:</b> ${prompt}</div>`;

            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt })
            });
            const data = await response.json();
            chatDiv.innerHTML += `<div><b>Agent:</b> ${data.response}</div>`;
            chatDiv.scrollTop = chatDiv.scrollHeight;
            document.getElementById('prompt').value = '';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    prompt = data.get("prompt", "")
    if not prompt:
        return jsonify({"error": "Prompt manquant"}), 400
    response = appeler_chatgpt(prompt)
    return jsonify({"response": response})

# ----------------------------
# Fonctions simulées pour API
# ----------------------------
def appeler_chatgpt(prompt):
    print(f"[CHATGPT] prompt={prompt[:80]}...")
    return f"Réponse simulée pour : {prompt}"

def envoyer_email(destinataire, sujet, contenu):
    print(f"[EMAIL] {destinataire}: {sujet}")
    return True

def envoyer_sms(numero, message):
    print(f"[SMS] {numero}: {message}")
    return True

# ----------------------------
# Boucle autonome (optionnelle)
# ----------------------------
def agent_autonome_loop():
    while True:
        print("[AGENT] Tick autonome")
        envoyer_email(AGENT_SUPPORT_EMAIL, "Rapport", "Agent actif")
        envoyer_sms(TELEPHONE_NUMERO, "Agent actif")
        time.sleep(60)

# ----------------------------
# Main
# ----------------------------
if __name__ == '__main__':
    t = threading.Thread(target=agent_autonome_loop, daemon=True)
    t.start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
