import flask
from flask import Flask
from flask import request, make_response, redirect
import requests
import os
import jwt

import sqlite3

# --- Initialize the database ---
db_con = sqlite3.connect("users.db")
db_cur = db_con.cursor()
db_cur.execute("""CREATE TABLE IF NOT EXISTS users (userID VARCHAR, USERNAME VARCHAR, EMAIL VARCHAR, AVATAR VARCHAR)""")
db_cur.close()
db_con.commit()
db_con.close()

app = Flask(__name__)

bot_secret = os.getenv("OAUTH_TOKEN")  # From the OAUTH page and NOT the bot page (spent way too long on this)
bot_id = os.getenv("BOT_ID")

jwt_token_signature = os.getenv('JWT_TOKEN_SIGNATURE')

AUTH_URL = "https://discord.com/oauth2/authorize?client_id=1175578439202390086&response_type=code&redirect_uri=http%3A%2F%2F127.0.0.1%3A5000%2Fauth%2Fdiscord&scope=guilds+identify+email"


@app.route('/')
async def hello_world():
    return flask.render_template('index.html',
                                 auth_url=AUTH_URL)


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
        req_user = requests.get('https://discord.com/api/v10/users/@me',
                                headers={'Authorization': f'Bearer {req.json()["access_token"]}'})
    except KeyError:
        return redirect(AUTH_URL)
    req_user_json = req_user.json()

    print(req_user_json)

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
    else:
        cur.execute("""INSERT INTO users VALUES(?, ?, ?, ?)""", (jwt_encoded_id, req_user_json['username'], req_user_json['email'], req_user_json['avatar']))

    con.commit()
    cur.close()
    con.close()

    return resp


@app.route('/panel')
async def panel():
    pass


if __name__ == '__main__':
    app.run()
