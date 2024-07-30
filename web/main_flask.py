import flask
from flask import Flask
from flask import request, make_response, redirect
import requests
import os
import jwt
import discord
import threading

import sqlite3

# --- Initialize the database ---
db_con = sqlite3.connect("users.db")
db_cur = db_con.cursor()
db_cur.execute(
    """CREATE TABLE IF NOT EXISTS users (userID VARCHAR, USERNAME VARCHAR, EMAIL VARCHAR, AVATAR VARCHAR, last_token 
    VARCHAR, refresh_token VARCHAR)""")
"""
0 userID: The user's ID that is stored in a JWT token
1 USERNAME: The user's discord username
2 EMAIL: The user's email connected to their discord account
3 AVATAR: The user's avatar connected to their discord account
4 last_token: The last token received by the website from discord's authentication
5 refresh_token: The token used to refresh the authentication
"""
db_cur.close()
db_con.commit()
db_con.close()

app = Flask(__name__, static_url_path='')

bot_secret = os.getenv("OAUTH_TOKEN")  # From the OAUTH page and NOT the bot page (spent way too long on this)
bot_id = os.getenv("BOT_ID")

jwt_token_signature = os.getenv('JWT_TOKEN_SIGNATURE')

AUTH_URL = os.getenv("URL_AUTH")

bot = discord.Bot


async def start_app(bot_):
    global bot
    bot = bot_

    app_thread = threading.Thread(target=app.run)
    app_thread.start()


async def get_data(endpoint, access_token):
    req_user = requests.get(f'https://discord.com/api/v10/{endpoint}',
                            headers={'Authorization': f'Bearer {access_token}'})
    return req_user


@app.route('/')
async def index():
    return flask.render_template('index.html',
                                 auth_url=AUTH_URL)


@app.route('/about')
async def about():
    return flask.render_template('about.html', )


@app.route('/auth/discord')
async def discord_login():
    con = sqlite3.connect("users.db")
    cur = con.cursor()
    data = {
        'code': request.args.get('code'),
        'grant_type': 'authorization_code',
        'redirect_uri': 'http://127.0.0.1:5000/auth/discord',
        'client_id': bot_id,
        'client_secret': bot_secret,
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    req = requests.post('https://discord.com/api/v10/oauth2/token', data=data,
                        headers=headers, auth=(bot_id, bot_secret))
    try:
        req_user = await get_data('users/@me', req.json()["access_token"])
    except KeyError:
        print(req.json())
        return redirect(AUTH_URL)
    req_user_json = req_user.json()

    jwt_encoded_id = jwt.encode(
        {'id': req_user_json['id'], }, key=jwt_token_signature, algorithm='HS256')

    # --- Set token in the browser ---
    resp = make_response(redirect('/panel'))
    resp.set_cookie('token', jwt_encoded_id)

    # --- Manage token and user in database ---

    res = cur.execute("""SELECT * FROM users WHERE userID IS ?""",
                      (jwt_encoded_id,))  # Search for user in the database
    fetch = res.fetchone()
    if fetch:
        if req_user_json['avatar'] != fetch[3]:
            cur.execute("""UPDATE users SET AVATAR = ? WHERE userID IS ?""", (req_user_json['AVATAR'], jwt_encoded_id))
        if req_user_json['email'] != fetch[2]:
            cur.execute("""UPDATE users SET email = ? WHERE userID IS ?""", (req_user_json['email'], jwt_encoded_id))
        if req_user_json['username'] != fetch[1]:
            cur.execute("""UPDATE users SET USERNAME = ? WHERE userID IS ?""",
                        (req_user_json['username'], jwt_encoded_id))
        cur.execute("""UPDATE users SET last_token = ? WHERE userID IS ?""",
                    (req.json()['access_token'], jwt_encoded_id))
        cur.execute("""UPDATE users SET refresh_token = ? WHERE userID IS ?""",
                    (req.json()['refresh_token'], jwt_encoded_id))
    else:
        cur.execute("""INSERT INTO users VALUES(?, ?, ?, ?, ?, ?)""",
                    (jwt_encoded_id, req_user_json['username'], req_user_json['email'], req_user_json['avatar'],
                     req.json()['access_token'], req.json()['refresh_token']))

    con.commit()
    cur.close()
    con.close()

    return resp


@app.route('/creator')
async def creator():
    return flask.render_template('creator.html')


@app.route('/panel')
async def panel():
    con = sqlite3.connect("users.db")
    cur = con.cursor()
    token = request.cookies.get('token')  # JWT token
    if not token:
        return redirect('/auth/discord')

    user_id = jwt.decode(str(token), key=jwt_token_signature, algorithms="HS256")['id']
    res = cur.execute("""SELECT * FROM users WHERE userID IS ?""",
                      (token,))  # Search for user in the database
    fetch = res.fetchone()

    req_user_guilds = await get_data('users/@me/guilds', fetch[4])

    json_user_guilds = req_user_guilds.json()
    user_guilds = []
    for guild in json_user_guilds:
        # noinspection PyTypeChecker
        for bot_guild in bot.guilds:
            if int(guild['id']) == int(bot_guild.id):  # Check if user is in any of the bot's guilds
                user_permissions = discord.Permissions(int(guild['permissions']))  # Thanks icewolfy! :)
                if user_permissions.manage_guild:
                    user_guilds.append(guild)

    cur.close()
    con.close()
    return flask.render_template('panel.html', username=fetch[1],
                                 avatar=f"https://cdn.discordapp.com/avatars/{user_id}/{fetch[3]}.png",
                                 shared_guilds=user_guilds)


async def refresh_token(token: str):
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': token
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    req = requests.post(f'https://discord.com/api/v10//oauth2/token', data=data, headers=headers,
                        auth=(bot_id, bot_secret))

    return req.json()


if __name__ == '__main__':
    app.run(debug=True)
