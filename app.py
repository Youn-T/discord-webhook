from routes import app
import secrets

app.secret_key = secrets.token_hex(32)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)