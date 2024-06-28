import flask
from flask import Flask
from flask import request
import requests
import os

app = Flask(__name__)

bot_secret = os.getenv("OAUTH_TOKEN")  # From the OAUTH page and NOT the bot page (spent way too long on this)
bot_id = os.getenv("BOT_ID")

print(bot_secret, bot_id)

@app.route('/')
async def hello_world():
    return flask.render_template('index.html',
                                 auth_url="https://discord.com/oauth2/authorize?client_id=1175578439202390086&response_type=code&redirect_uri=http%3A%2F%2F127.0.0.1%3A5000%2Flogin&scope=identify+guilds+email")


@app.route('/login')
async def login():
    data = {
        'code': request.args.get('code'),
        'grant_type': 'authorization_code',
        'redirect_uri': 'http://127.0.0.1:5000/login',
        'client_id': bot_id,
        'client_secret': bot_secret,
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    req = requests.post('https://discord.com/api/v10/oauth2/token', data=data,
                        headers=headers, auth=(bot_id, bot_secret))
    print(req.text)
    return req.text


if __name__ == '__main__':
    app.run()
