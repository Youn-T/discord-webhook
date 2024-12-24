import json
from flask import Flask, Response, redirect, render_template, request, session, url_for
import requests
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

API_ENDPOINT = 'https://discord.com/api/v10'
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
BOT_TOKEN = os.getenv('BOT_TOKEN')
REDIRECT_URI = 'http://192.168.1.18/'

def exchange_code(code):
    """
    échange le code d'authentification contre un token
    """
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    r = requests.post('%s/oauth2/token' % API_ENDPOINT, data=data, headers=headers, auth=(CLIENT_ID, CLIENT_SECRET))
    r.raise_for_status()
    return r.json()

@app.route('/')
def home():
    try:
        # récupération des différents paramètres 
        code = request.args.get('code')
        server_id = request.args.get('id')
        webhook_id = request.args.get('webhook_id')      
        print(webhook_id)
        auth_response = authFlow(code) # gère l'authentification de l'utilisateur
        if auth_response:
            return auth_response
                
        guilds_owned, icons = showGuilds() # affiche les serveurs de l'utilisateur
                                
        webHooks = None
        if server_id:
            webHooks = showGuildWebHooks(guilds_owned, server_id)
            if type(webHooks) == Response:
                return webHooks
        print("pas normal")
        if (webHooks and webhook_id):
            print(1)
            print(webHooks[int(webhook_id)][3])
            return render_template("index.html", guilds=icons,webHooks=webHooks,webhook=webHooks[int(webhook_id)][3])
        elif (webHooks):
            print(1)
            return render_template("index.html", guilds=icons,webHooks=webHooks)
        else:
            print(3)
            return render_template("index.html", guilds=icons)
            
    except:
        print("error !")
    #     # return redirect("https://discord.com/oauth2/authorize?client_id=1317851690136764487&response_type=code&redirect_uri=http%3A%2F%2F192.168.1.18%2F&scope=guilds")
    return render_template("index.html")

@app.route('/send', methods=['POST'])
def send():
    try:
        url = request.form.get('webhook-url')
        message = request.form.get('message')
        print(url," - ", message)
        
        res = requests.post(url, data={"content":message})
        
        print(res.status_code, " - ", res.content)
    except:
        print("an error occured sending the message")
        
    return redirect(url_for("home"))

@app.route('/server_clicked')

def serverClicked():
    print("SERVER CLICKED !")
    
def authFlow(code):
    # si il n'y a pas de token d'accès dans l'url (c'est le cas lorsque l'user a autorisé l'app via l'Oauth2) ET que le token n'est pas stocké
    if code == None and "access_token" not in session: 
        print("code is None redirecting ...")
        return redirect("https://discord.com/oauth2/authorize?client_id=1317851690136764487&response_type=code&redirect_uri=http%3A%2F%2F192.168.1.18%2F&scope=guilds")

    # si il y a un code dans l'url et que le token n'est pas stocké
    elif "access_token" not in session:
        tokenForm = exchange_code(code)
        print(tokenForm["access_token"])
        try:
            session["access_token"] = str(tokenForm["access_token"])
            return redirect("http://192.168.1.18") # à modifier 
        except:
            print("error saving id")
            
def fetchGuilds():
    """
    récupère les serveurs de l'utilisateur
    """
    headers = {
        "Authorization": f"Bearer {session["access_token"]}"
    }
    
    url = "https://discord.com/api/users/@me/guilds"
    
    return requests.get(url=url, headers=headers)

def showGuilds():
    guilds = fetchGuilds()
    guilds_owned = []
    icons=[]
    id = 0
    for guild in guilds.json():
        if (guild["owner"]):
            guilds_owned.append(guild)
            # res = requests.get(f"https://discord.com/api/v10/guilds/{guild["id"]}/webhooks", headers=headers)
            # print(res.json())
            if (guild["icon"]):
                icons.append([id,f"https://cdn.discordapp.com/icons/{guild["id"]}/{guild["icon"]}.png?size=64"])
            else:
                icons.append([id,f"{getFirstLetter(guild['name'])}"])
            id += 1
    return guilds_owned, icons 

def showGuildWebHooks(guilds_owned : list, server_id : int):
    targetedGuild = guilds_owned[int(server_id)]
    guilds = getBotGuilds()
    if any(guild["id"] == targetedGuild['id'] for guild in guilds): # vérifie si le bot est dans le serveur
        guildWebHooks = getGuildWebHooks(targetedGuild['id'])
        webHooks = []
        id = 0
        for res in guildWebHooks:
            if (res['type'] == 1 and 'url' in res): # vérifie si c'est un webhook pour envoyer des messages
                avatar = getWebHookAvatar(res)
                print(json.dumps(guildWebHooks, indent=4))
                webHooks.append([id, res['name'], avatar, res['url']])
                id += 1
        return webHooks
            
    else:                    
        return redirect(f"https://discord.com/oauth2/authorize?client_id=1317851690136764487&permissions=536870912&integration_type=0&scope=bot&guild_id={targetedGuild['id']}&disable_guild_select=true&redirect_uri=http%3A%2F%2F192.168.1.18%2F")
                
def getBotGuilds():
    headers = {
        "Authorization": f"Bot {BOT_TOKEN}"
    }
    response = requests.get("https://discord.com/api/v10/users/@me/guilds", headers=headers)
    if response.status_code == 200:
        return response.json()
    
def getGuildWebHooks(guild_id):
    headers = {
        "Authorization": f"Bot {BOT_TOKEN}"
    }
    return requests.get(f"https://discord.com/api/v10/guilds/{guild_id}/webhooks", headers=headers).json()

def getWebHookAvatar(avatarRes) -> str:
    avatar = "'/static/images/default logo.png'"
    if (avatarRes['avatar']):
        avatar=f"https://cdn.discordapp.com/avatars/{avatarRes['id']}/{avatarRes['avatar']}.png?size=64"
    return avatar
        
def getFirstLetter(word: str) -> str:
    lst = word.split()
    return ''.join([ wrd[0] for wrd in lst ])