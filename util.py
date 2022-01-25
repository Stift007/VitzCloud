import requests

class Badge:
    def __init__(self,name,img) -> None:
        self.name = name
        self.img = img
        self.docs_uri = f'https://docs.vitznode.repl.co/badges/'

badges = {'Gründer':Badge('Gründer','/cdn/badge/founder.png'),'Website-Moderator':Badge('Website-Moderator','/cdn/badge/mod.png'),'Verifizierter Benutzer der ersten Stunde':Badge('Verifizierter Benutzer der ersten Stunde','/cdn/badge/certified-staff.png'),'Bughunter':Badge('Bughunter','/cdn/badge/bugbuster.png'),'Developer':Badge('Developer','/cdn/badge/developer.png')}

class Course:
    def __init__(self,name,endpoint):
        self.name = name
        self.url_for = f'/course/{endpoint}'

def generate_badge(name):
    return badges[name]

random_names = [
    'electro','pancake','spoil','nuts','pancakeeater','muncher','clone','git','hub','master','hackerman'
]

class DiscordOAuth2:
    client_id = "829764119708041236"
    client_secret = "JXaTpA4VvULzOI90DlCSy1Hlu_qv6NPT"
    redirect_uri = "http://45.85.219.137:80/callback/discord"
    discord_login_url = "https://discord.com/api/oauth2/authorize?client_id=829764119708041236&redirect_uri=http%3A%2F%2F45.85.219.137%3A80%2Fcallback%2Fdiscord&response_type=code&scope=identify%20email"
    discord_token_url = "https://discord.com/api/oauth2/token"
    discord_api_url = "https://discord.com/api"
    scope = "identify%20email"
    @staticmethod
    def get_token(code):
        payload = {
            "client_id": DiscordOAuth2.client_id,
            "client_secret":DiscordOAuth2.client_secret,
            "grant_type": "authorization_code",
            "code":code,
            "redirect_uri":DiscordOAuth2.redirect_uri,
            "scope":DiscordOAuth2.scope
        }

        resp = requests.post(url=DiscordOAuth2.discord_token_url,data=payload).json()
        return resp.get("access_token")

    @staticmethod
    def get_user(token):
        url = DiscordOAuth2.discord_api_url+"/users/@me"
        headers = {
            "Authorization":f"Bearer {token}"
        }
        resp = requests.get(url=url,headers=headers).json()
        return resp

    