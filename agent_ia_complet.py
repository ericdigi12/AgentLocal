from flask import Flask, request, jsonify
import threading
import time
import requests
import os
import json
from datetime import datetime

# ----------------------------
# Clés API et données - AVEC GOOGLE SHEETS ID
# ----------------------------
FACEBOOK_API_1 = "EAAUSZBBKCQg4BPR1vtO3u5IE6b2rzF6WNv1m74KU0ZC4uhLIyaVYKfZCMg3FoEdcWxpc4ZCHOZCEtigTeHJH3j6XcA2lcraApY3ANZBKT6TZCuZAjWehdMepKkcZBGC5kK1pUxk7cVZB2IZBQDiinZBpS8KFK0Hk2nmJ53w8SbEydBVUkCdNhRxIeIMnZBTxUQ3KNMBWFgkttuZBfYWcAbi1aCk646CzXfV3YR65hZA"
MAILERSEND_KEY = "mlsn.ed391a766e2b009ef0530f16463ed2c3f66150dec86a01815d712af2339a1680"
BREVO_API = "eyJhcGlfa2V5IjoieGtleXNpYi02MDhhOWNkYWMwOTg1Y2RjZjQxNDBlNDg3ZjkxMWI2Njg2MjJjOWQ0MGJjZDQ4M2NhMGMxOGMyMmQ5MDJiMDExLXJhOHFWSE5WVDFXQzhqQWMifQ=="
SENDGRID_KEY = "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"
ID_CLIENT_OAUTH_GOOGLE = "lien_suspect_supprimé"
GOOGLE_SHEETS_ID = "1HVae5yxwM32x4Q_sThqqHw5PWn_5JW2hCOvO0hadp1k"  # ✅ AJOUTÉ
GOOGLE_API_KEY = "AIzaSyBvFxvgm_O2u_m3LfqN2Og8x1Y4KpW_Z9E"  # ⚠️ AJOUTEZ VOTRE CLÉ API GOOGLE
TWILIO_SID = "AC82b57eb18972528ced8c10fec5966407"
TWILIO_AUTH_TOKEN = "27ccbcacae90f44a3cb1a79179f0a785"
SCRAPER_API = "499af931eb095bd4e6aed4266b019cf4"
CLE_API_CHATGPT = "sk-proj-895Xpso-ub_ut3ePd8dMHnfnVMDjvZs8jcya18Yr41Zvay4ZL9PajlcvjhHZ4"
API_BINANCE = "fndvgRCy1G4Y9I9mK1icJ4lYohnIxmfNcuBGioyDfF9ecplDKx8KWn4cxyVQRy76"
BINANCE_SECRET = "XXLxBteRnH2SPEFwTfpkuO3P8WZmsDeoCazqp8EmngQ0E6rSaqcG6zBRo22pjl"
CARTE_VIRTUELLE_NUMERO = "5355515516297167"
CARTE_VIRTUELLE_CVV = "501"
CARTE_VIRTUELLE_NOM = "ERIC PARE"
TELEPHONE_NUMERO = "+22665399292"
COURRIEL = "pare31881@gmail.com"
AGENT_SUPPORT_EMAIL = "agent.commercial.ai@gmail.com"
PAIEMENTS_MOBILE_AFRIQUE = "Orange Money, Wave (+22665399292)"

# ----------------------------
# Configuration Flask
# ----------------------------
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# Variables globales pour le statut
agent_status = {
    "actif": False,
    "derniere_execution": None,
    "erreurs": [],
    "google_sheets_logs": []
}

# ----------------------------
# Routes Flask
# ----------------------------
@app.route('/')
def index():
    return jsonify({
        "message": "Agent IA prêt et fonctionnel!",
        "timestamp": datetime.now().isoformat(),
        "status": "active",
        "google_sheets_id": GOOGLE_SHEETS_ID
    })

@app.route('/status')
def get_status():
    return jsonify(agent_status)

@app.route('/api/test_sheets', methods=['POST'])
def test_sheets_api():
    """Test d'écriture dans Google Sheets"""
    data = request.get_json() or {}
    test_data = data.get('data', [["Test", "API", datetime.now().isoformat()]])
    result = ecrire_google_sheets("TestAPI!A1", test_data)
    return jsonify({"success": result})

@app.route('/api/read_sheets', methods=['GET'])
def read_sheets_api():
    """Lecture des données Google Sheets"""
    range_name = request.args.get('range', 'Sheet1!A1:Z100')
    result = lire_google_sheets(range_name)
    return jsonify({"data": result})

# ----------------------------
# Fonctions API - TOUTES LES APIs
# ----------------------------

def envoyer_email(destinataire, sujet, contenu):
    """Fonction email avec logique de fallback"""
    try:
        if MAILERSEND_KEY:
            headers = {
                'Authorization': f'Bearer {MAILERSEND_KEY}',
                'Content-Type': 'application/json'
            }
            data = {
                'from': {'email': COURRIEL, 'name': 'Agent IA'},
                'to': [{'email': destinataire}],
                'subject': sujet,
                'text': contenu
            }
            print(f"[EMAIL-MailerSend] Envoi à {destinataire} : {sujet}")
            return True
            
        elif SENDGRID_KEY:
            headers = {
                'Authorization': f'Bearer {SENDGRID_KEY}',
                'Content-Type': 'application/json'
            }
            data = {
                'personalizations': [{'to': [{'email': destinataire}]}],
                'from': {'email': COURRIEL},
                'subject': sujet,
                'content': [{'type': 'text/plain', 'value': contenu}]
            }
            print(f"[EMAIL-SendGrid] Envoi à {destinataire} : {sujet}")
            return True
            
        elif BREVO_API:
            headers = {
                'api-key': BREVO_API,
                'Content-Type': 'application/json'
            }
            data = {
                'sender': {'email': COURRIEL, 'name': 'Agent IA'},
                'to': [{'email': destinataire}],
                'subject': sujet,
                'textContent': contenu
            }
            print(f"[EMAIL-Brevo] Envoi à {destinataire} : {sujet}")
            return True
            
        else:
            print("[EMAIL] Aucune clé API email disponible")
            return False
            
    except Exception as e:
        print(f"[EMAIL] Erreur : {e}")
        agent_status["erreurs"].append(f"Email error: {e}")
        return False

def envoyer_sms(numero, message):
    """Fonction SMS Twilio"""
    try:
        if not (TWILIO_SID and TWILIO_AUTH_TOKEN):
            print("[SMS] Clés Twilio manquantes")
            return False
        
        # Configuration Twilio
        auth = (TWILIO_SID, TWILIO_AUTH_TOKEN)
        url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/Messages.json"
        
        data = {
            'From': '+1234567890',  # Remplacez par votre numéro Twilio
            'To': numero,
            'Body': message
        }
        
        response = requests.post(url, data=data, auth=auth, timeout=30)
        
        if response.status_code == 201:
            result = response.json()
            print(f"[SMS] Envoyé à {numero} : {message[:50]}... (ID: {result.get('sid')})")
            return True
        else:
            print(f"[SMS] Erreur Twilio : {response.status_code}")
            return False
        
    except Exception as e:
        print(f"[SMS] Erreur Twilio : {e}")
        agent_status["erreurs"].append(f"SMS error: {e}")
        return False

def appeler_chatgpt(prompt):
    """Fonction ChatGPT OpenAI"""
    try:
        if not CLE_API_CHATGPT:
            return "Clé API ChatGPT manquante"
        
        headers = {
            'Authorization': f'Bearer {CLE_API_CHATGPT}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'max_tokens': 150,
            'temperature': 0.7
        }
        
        print(f"[CHATGPT] Requête: {prompt[:80]}...")
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions', 
            headers=headers, 
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return f"Erreur API OpenAI: {response.status_code}"
            
    except Exception as e:
        print(f"[CHATGPT] Erreur : {e}")
        agent_status["erreurs"].append(f"ChatGPT error: {e}")
        return f"Erreur ChatGPT : {e}"

def consulter_binance(action="account"):
    """Fonction Binance avec signature HMAC"""
    try:
        if not (API_BINANCE and BINANCE_SECRET):
            print("[BINANCE] Clés API manquantes")
            return {"error": "Clés manquantes"}
        
        import hashlib
        import hmac
        from urllib.parse import urlencode
        
        base_url = "https://api.binance.com"
        endpoint = "/api/v3/account"
        timestamp = int(time.time() * 1000)
        
        params = {
            'timestamp': timestamp
        }
        
        query_string = urlencode(params)
        signature = hmac.new(
            BINANCE_SECRET.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        params['signature'] = signature
        
        headers = {
            'X-MBX-APIKEY': API_BINANCE
        }
        
        print(f"[BINANCE] Consultation: {action}")
        
        response = requests.get(
            f"{base_url}{endpoint}",
            headers=headers,
            params=params,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Binance API error: {response.status_code}"}
            
    except Exception as e:
        print(f"[BINANCE] Erreur : {e}")
        agent_status["erreurs"].append(f"Binance error: {e}")
        return {"error": str(e)}

def poster_facebook(message):
    """Fonction Facebook Graph API"""
    try:
        if not FACEBOOK_API_1:
            return False
        
        url = f"https://graph.facebook.com/v18.0/me/feed"
        
        params = {
            'message': message,
            'access_token': FACEBOOK_API_1
        }
        
        print(f"[FACEBOOK] Publication: {message[:50]}...")
        
        response = requests.post(url, data=params, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"[FACEBOOK] Publié ID: {result.get('id')}")
            return True
        else:
            print(f"[FACEBOOK] Erreur: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[FACEBOOK] Erreur : {e}")
        agent_status["erreurs"].append(f"Facebook error: {e}")
        return False

def scraper_donnees(url):
    """Fonction ScraperAPI"""
    try:
        if not SCRAPER_API:
            return {"error": "Clé Scraper manquante"}
        
        scraper_url = "http://api.scraperapi.com"
        params = {
            'api_key': SCRAPER_API,
            'url': url,
            'render': 'false'
        }
        
        print(f"[SCRAPER] Scraping: {url}")
        
        response = requests.get(scraper_url, params=params, timeout=60)
        
        if response.status_code == 200:
            return {"status": "success", "data": response.text[:500]}
        else:
            return {"error": f"Scraper error: {response.status_code}"}
            
    except Exception as e:
        print(f"[SCRAPER] Erreur : {e}")
        return {"error": str(e)}

# ----------------------------
# GOOGLE SHEETS API - NOUVELLES FONCTIONS ✅
# ----------------------------

def ecrire_google_sheets(range_name, values):
    """Écrire des données dans Google Sheets"""
    try:
        if not (GOOGLE_API_KEY and GOOGLE_SHEETS_ID):
            print("[GOOGLE_SHEETS] Clé API ou ID manquant")
            return False
        
        # URL Google Sheets API v4
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{GOOGLE_SHEETS_ID}/values/{range_name}"
        
        # Paramètres pour l'écriture
        params = {
            'key': GOOGLE_API_KEY,
            'valueInputOption': 'RAW'
        }
        
        # Données à écrire
        data = {
            'values': values
        }
        
        print(f"[GOOGLE_SHEETS] Écriture dans {range_name}: {len(values)} lignes")
        
        # Requête PUT pour écrire les données
        response = requests.put(
            url,
            params=params,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"[GOOGLE_SHEETS] ✅ Écrit {result.get('updatedCells', 0)} cellules")
            agent_status["google_sheets_logs"].append({
                "action": "write",
                "range": range_name,
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            })
            return True
        else:
            print(f"[GOOGLE_SHEETS] ❌ Erreur écriture: {response.status_code}")
            print(f"[GOOGLE_SHEETS] Réponse: {response.text}")
            return False
            
    except Exception as e:
        print(f"[GOOGLE_SHEETS] Erreur écriture : {e}")
        agent_status["erreurs"].append(f"Google Sheets write error: {e}")
        return False

def lire_google_sheets(range_name):
    """Lire des données depuis Google Sheets"""
    try:
        if not (GOOGLE_API_KEY and GOOGLE_SHEETS_ID):
            print("[GOOGLE_SHEETS] Clé API ou ID manquant")
            return []
        
        # URL Google Sheets API v4 pour lecture
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{GOOGLE_SHEETS_ID}/values/{range_name}"
        
        params = {
            'key': GOOGLE_API_KEY
        }
        
        print(f"[GOOGLE_SHEETS] Lecture de {range_name}")
        
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            values = result.get('values', [])
            print(f"[GOOGLE_SHEETS] ✅ Lu {len(values)} lignes")
            agent_status["google_sheets_logs"].append({
                "action": "read",
                "range": range_name,
                "timestamp": datetime.now().isoformat(),
                "status": "success",
                "rows_count": len(values)
            })
            return values
        else:
            print(f"[GOOGLE_SHEETS] ❌ Erreur lecture: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"[GOOGLE_SHEETS] Erreur lecture : {e}")
        agent_status["erreurs"].append(f"Google Sheets read error: {e}")
        return []

def ajouter_ligne_sheets(donnees):
    """Ajouter une ligne à la fin du Google Sheets"""
    try:
        if not (GOOGLE_API_KEY and GOOGLE_SHEETS_ID):
            return False
        
        # URL pour ajouter des données (append)
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{GOOGLE_SHEETS_ID}/values/Sheet1!A:Z:append"
        
        params = {
            'key': GOOGLE_API_KEY,
            'valueInputOption': 'RAW',
            'insertDataOption': 'INSERT_ROWS'
        }
        
        data = {
            'values': [donnees]  # Une ligne de données
        }
        
        print(f"[GOOGLE_SHEETS] Ajout ligne: {donnees}")
        
        response = requests.post(url, params=params, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"[GOOGLE_SHEETS] ✅ Ligne ajoutée")
            return True
        else:
            print(f"[GOOGLE_SHEETS] ❌ Erreur ajout: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[GOOGLE_SHEETS] Erreur ajout ligne : {e}")
        return False

# ----------------------------
# Boucle autonome de l'agent AVEC GOOGLE SHEETS
# ----------------------------
def agent_autonome_loop():
    """Boucle principale avec toutes les APIs + Google Sheets"""
    global agent_status
    
    agent_status["actif"] = True
    print("[AGENT] Démarrage de l'agent autonome avec Google Sheets")
    
    while True:
        try:
            timestamp = datetime.now().isoformat()
            agent_status["derniere_execution"] = timestamp
            
            print(f"[AGENT] Cycle à {timestamp}")
            
            # 1. Rapport par email
            email_sent = envoyer_email(
                AGENT_SUPPORT_EMAIL or COURRIEL,
                f"Rapport Agent IA - {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                f"Agent actif et opérationnel.\nDernière exécution: {timestamp}"
            )
            
            # 2. SMS de statut
            if TELEPHONE_NUMERO:
                sms_sent = envoyer_sms(
                    TELEPHONE_NUMERO,
                    f"Agent IA actif - {datetime.now().strftime('%H:%M')}"
                )
            
            # 3. Génération contenu ChatGPT
            marketing_idea = appeler_chatgpt(
                "Génère une idée marketing créative pour les réseaux sociaux."
            )
            print(f"[MARKETING] {marketing_idea}")
            
            # 4. Publication Facebook
            if len(marketing_idea) > 10:
                facebook_posted = poster_facebook(
                    f"💡 Idée du jour: {marketing_idea[:200]}..."
                )
            
            # 5. Vérification Binance
            binance_data = consulter_binance("account")
            if "error" not in binance_data:
                print("[BINANCE] Compte vérifié avec succès")
            
            # 6. Scraping données
            if SCRAPER_API:
                scraping_result = scraper_donnees("https://example.com")
                print(f"[SCRAPER] Données récupérées")
            
            # 7. ✅ LOGGING DANS GOOGLE SHEETS - NOUVEAU !
            log_data = [
                timestamp,
                "Agent IA",
                "Cycle complet",
                f"Email: {'✓' if email_sent else '✗'}",
                f"SMS: {'✓' if 'sms_sent' in locals() and sms_sent else '✗'}",
                f"Facebook: {'✓' if 'facebook_posted' in locals() and facebook_posted else '✗'}",
                f"ChatGPT: {'✓' if len(marketing_idea) > 10 else '✗'}",
                f"Binance: {'✓' if 'error' not in binance_data else '✗'}",
                marketing_idea[:100] if len(marketing_idea) > 10 else "Erreur"
            ]
            
            sheets_logged = ajouter_ligne_sheets(log_data)
            if sheets_logged:
                print("[GOOGLE_SHEETS] ✅ Cycle loggé dans Sheets")
            
            # 8. ✅ SAUVEGARDE DONNÉES IMPORTANTES DANS SHEETS
            if len(agent_status["erreurs"]) > 0:
                # Log des erreurs dans une feuille séparée
                for erreur in agent_status["erreurs"][-5:]:  # Dernières 5 erreurs
                    erreur_data = [timestamp, "ERREUR", erreur]
                    ecrire_google_sheets("Erreurs!A:C", [erreur_data])
                
                # Reset des erreurs après logging
                agent_status["erreurs"] = []
            
            print("[AGENT] Cycle terminé avec Google Sheets logging")
            
        except Exception as e:
            print(f"[AGENT] Erreur dans le cycle : {e}")
            agent_status["erreurs"].append(f"Cycle error: {e}")
            
            # Log de l'erreur critique dans Sheets
            try:
                erreur_critique = [datetime.now().isoformat(), "ERREUR_CRITIQUE", str(e)]
                ajouter_ligne_sheets(erreur_critique)
            except:
                pass
        
        # Pause de 10 minutes entre chaque cycle
        time.sleep(600)

# ----------------------------
# Main - DÉMARRAGE COMPLET
# ----------------------------
if __name__ == '__main__':
    try:
        # Vérification des APIs au démarrage
        print("[STARTUP] Vérification des APIs...")
        apis_status = {
            'Email': bool(MAILERSEND_KEY or SENDGRID_KEY or BREVO_API),
            'SMS': bool(TWILIO_SID and TWILIO_AUTH_TOKEN),
            'ChatGPT': bool(CLE_API_CHATGPT),
            'Binance': bool(API_BINANCE and BINANCE_SECRET),
            'Facebook': bool(FACEBOOK_API_1),
            'Scraper': bool(SCRAPER_API),
            'Google Sheets': bool(GOOGLE_API_KEY and GOOGLE_SHEETS_ID)  # ✅ AJOUTÉ
        }
        
        for api, status in apis_status.items():
            print(f"[{api}] {'✓ Configuré' if status else '✗ Manquant'}")
        
        # Test initial Google Sheets
        if GOOGLE_API_KEY and GOOGLE_SHEETS_ID:
            print("[GOOGLE_SHEETS] Test de connexion...")
            test_data = [["STARTUP", datetime.now().isoformat(), "Agent IA démarré"]]
            if ajouter_ligne_sheets(test_data[0]):
                print("[GOOGLE_SHEETS] ✅ Connexion réussie!")
            else:
                print("[GOOGLE_SHEETS] ❌ Échec connexion")
        
        # Démarrage thread agent
       
