import telebot
from decouple import config
import cohere
from flask import Flask, request
import time

# Variables de entorno
TELEGRAM_TOKEN = config("TELEGRAM_TOKEN")
COHERE_API_KEY = config("MODEL_API_KEY")
PORT = config("PORT", cast=int, default=5000)
PROMPT = config("PROMPT")


# Crear app de Flask
app = Flask(__name__)


# Ruta del webhook para recibir actualizaciones
@app.route("/" + TELEGRAM_TOKEN, methods=["POST"])
def receive_update():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200


# Ruta hacer ping de chequeo -> evita que se duerma el servicio web por inactividad
def check_health():
    return "OK", 200


# Inicializar el bot con el token de Telegram proporcionado
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Inicializar el cliente de Cohere para los prompts de IA
co = cohere.ClientV2(api_key=COHERE_API_KEY)
system_context = PROMPT


# Definir un gestor de mensajes para los comandos /start y /help.
@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.reply_to(
        message,
        """
    ¡Hola! Soy JoseAI, tu guía personal para conocer más sobre joselriascos, desarrollador web full stack.

    Aquí podrás descubrir su portafolio y conocer sus formas de contacto.

    Si te interesa la tecnología, el desarrollo web o simplemente conectar con un profesional apasionado, ¡este bot es el punto de partida perfecto!
    """,
    )


# Definir un gestor de mensajes para textos generales
@bot.message_handler(content_types=["text"])
def manage_text(message):
    text = message.text
    response = co.chat(
        model="command-r-plus-08-2024",
        messages=[
            {"role": "system", "content": system_context},
            {"role": "user", "content": text},
        ],
    )
    bot.reply_to(message, response.message.content[0].text)


# Configurar el webhook en Telegram al iniciar sesión
WEBHOOK_URL = config("WEBHOOK_URL")
webhook_url = f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}"

if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=webhook_url)
    app.run(host="0.0.0.0", port=PORT)
