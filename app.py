from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID        = os.environ.get("CHAT_ID")
SECRET_KEY     = os.environ.get("TV_SECRET", "")

def send_telegram(text: str):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        return 500, "Missing TELEGRAM_TOKEN or CHAT_ID"
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    r = requests.post(url, json=payload, timeout=10)
    return r.status_code, r.text

@app.route("/", methods=["GET"])
def health():
    return jsonify({"ok": True, "service": "tv-telegram-webhook"}), 200

@app.route("/tv", methods=["POST"])
def tv():
    data = request.get_json(force=True, silent=True) or {}

    secret = data.get("secret", "")
    if SECRET_KEY and secret != SECRET_KEY:
        return jsonify({"ok": False, "error": "unauthorized"}), 401

    action = data.get("action", "N/A")
    ticker = data.get("ticker", "N/A")
    price  = data.get("price", "N/A")
    sl     = data.get("sl", "N/A")
    tp     = data.get("tp", "N/A")
    tf     = data.get("tf", "1m")
    reason = data.get("reason", "Break & Retest + Volume")
    tstr   = data.get("time", "N/A")

    text = (
        f"⚡ *Signal*: `{action}`\n"
        f"📊 *Symbol*: `{ticker}` ({tf})\n"
        f"💰 *Price*: `{price}`\n"
        f"🛡️ *SL*: `{sl}`   🎯 *TP*: `{tp}`\n"
        f"🧠 *Reason*: {reason}\n"
        f"🕒 *Time*: `{tstr}`"
    )
    code, resp = send_telegram(text)
    return jsonify({"ok": code == 200, "resp": resp}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

