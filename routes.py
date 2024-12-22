from flask import Flask, redirect, render_template, request, session, url_for
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
            
        showGuilds() # affiche les serveurs de l'utilisateur
                
        if server_id != None:
            guild_s = guilds_owned[int(server_id)]
            headers = {
                "Authorization": f"Bot {BOT_TOKEN}"
            }
            response = requests.get("https://discord.com/api/v10/users/@me/guilds", headers=headers)
            
            if response.status_code == 200:
                guilds = response.json()
                if any(guild["id"] == guild_s['id'] for guild in guilds):
                    response = requests.get(f"https://discord.com/api/v10/guilds/{guild_s['id']}/webhooks", headers=headers)
                    webHooks = []
                    id = 0
                    for res in response.json():
                        if (res['type'] == 1):
                            avatar = ""
                            if (res['avatar'] == None):
                                avatar="'/static/images/default logo.png'"
                            else:
                                avatar=f"https://cdn.discordapp.com/avatars/{res['id']}/{res['avatar']}.png?size=64"
                            webHooks.append([id, res['name'], avatar])
                            id += 1
                    return render_template("index.html", guilds=icons, webHooks=webHooks)
                    
                else:                    
                    return redirect(f"https://discord.com/oauth2/authorize?client_id=1317851690136764487&permissions=536870912&integration_type=0&scope=bot&guild_id={guild_s['id']}&disable_guild_select=true&redirect_uri=http%3A%2F%2F192.168.1.18%2F")
                    
                    
        
        return render_template("index.html", guilds=icons)
        
    except:
        print("error !")
        # return redirect("https://discord.com/oauth2/authorize?client_id=1317851690136764487&response_type=code&redirect_uri=http%3A%2F%2F192.168.1.18%2F&scope=guilds")
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
            icons.append([id,f"https://cdn.discordapp.com/icons/{guild["id"]}/{guild["icon"]}.png?size=64"])
            id += 1