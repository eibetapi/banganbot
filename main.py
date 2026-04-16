import asyncio
import time
import requests
import hashlib
from datetime import datetime
from bs4 import BeautifulSoup
import os
import re

import discord

from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from flask import Flask
from threading import Thread

# =========================
# KEEP ALIVE
# =========================

app = Flask(__name__)

@app.route('/')
def home():
    return "Bots rodando"

def run_web():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    Thread(target=run_web).start()

# =========================
# CONFIG
# =========================

BOT_TOKEN_TICKET = os.getenv("BOT_TOKEN_TICKET")
BOT_TOKEN_BLUE = os.getenv("BOT_TOKEN_BLUE")

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID", "0"))

CHAT_ID = -1003972186058
ADMIN_ID = 1407508561

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})

# =========================
# DISCORD
# =========================

intents = discord.Intents.default()
intents.message_content = True

discord_client = discord.Client(intents=intents)

async def discord_send(msg):
    try:
        channel = discord_client.get_channel(DISCORD_CHANNEL_ID)
        if channel:
            await channel.send(msg)
    except:
        pass

@discord_client.event
async def on_ready():
    print("Discord conectado")
    await discord_send("👾•°•°• Wootteo ligando os motores•°•°•👾")

@discord_client.event
async def on_message(message):
    if message.author == discord_client.user:
        return

    content = message.content.lower().strip()

    if content == "/teste":
        await message.channel.send(TESTE_TEXT)

    elif content == "/status":
        await message.channel.send(STATUS_TEXT())

    elif content == "/painel":
        await message.channel.send("👾 Painel ativado👾")

# =========================
# STATE
# =========================

last_state = {}

tour_last_hash = None
tour_last_event = None

check_ticket = 0
check_blue = 0

panel_message_id = None
panel_chat_id = None

start_time = time.time()

br_rank = {
    "São Paulo": 0,
    "Rio de Janeiro": 0,
    "Curitiba": 0,
    "Belo Horizonte": 0,
    "Brasília": 0,
}

# =========================
# UPTIME
# =========================

def get_uptime():
    s = int(time.time() - start_time)
    return f"{s//3600}h {(s%3600)//60}m {s%60}s"

# =========================
# FETCH
# =========================

def fetch(url):
    try:
        return session.get(url, timeout=10).text
    except:
        return None

# =========================
# TOUR PARSER (MANTIDO SIMPLES MAS FUNCIONAL)
# =========================

def parse_tour(html):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)

    date_match = re.search(r"\d{1,2}/\d{1,2}/\d{4}", text)
    city_match = re.search(r"[A-Z][a-z]+,\s?[A-Z]{2}", text)

    date = "N/A"
    city = "N/A"
    days_left = "N/A"

    if date_match:
        try:
            dt = datetime.strptime(date_match.group(), "%m/%d/%Y")
            date = dt.strftime("%m/%d/%Y")
            days_left = (dt - datetime.now()).days
        except:
            pass

    if city_match:
        city = city_match.group()

    return {
        "date": date,
        "city": city,
        "days_left": days_left
    }

# =========================
# ALERT TOUR (NÃO MEXIDO)
# =========================

async def alert_tour(data):
    msg = f"""💜AGENDA TOUR UPDATE💜
📅 Data: {data['date']}
🏙️ Cidades: {data['city']}
🌎 Países: USA
"""
    await discord_send(msg)

# =========================
# ALERT TICKET (LAYOUT PRESERVADO)
# =========================

async def alert_ticket(url, data):
    text = f"""🔥ALERTA DE REPOSIÇÃO 🔥
🔗Link: {url}
📍Setor: {data.get('setor','N/A')}
🎫Categoria: {data.get('categorias','N/A')}
🎟️Tipo: {data.get('tipo','N/A')}
📦Status: {data.get('status','N/A')}

🎁ALERTA DE NOVA DATA🎁 
📅Data: {data.get('date','N/A')} 
🔗Link: {url} 
📍Setor: {data.get('setor','N/A')} 
🎫Categoria: {data.get('categorias','N/A')} 
🎟️Tipo: {data.get('tipo','N/A')} 
📦Status: {data.get('status','N/A')} 
📊Qtd: {data.get('quantidade','N/A')}
"""
    await discord_send(text)

# =========================
# ALERT BLUE
# =========================

async def alert_blue(url, data):
    text = f"""🔵REVENDA BLUE🔵
🔗Link: {url}
📍Setor: {data.get('setor','N/A')}
💰Valor: {data.get('valor','N/A')}
🎫Categoria: {data.get('categorias','N/A')}
🎟️Tipo: {data.get('tipo','N/A')}
📦Status: {data.get('status','N/A')}
"""
    await discord_send(text)

# =========================
# BOOT
# =========================

async def send_boot():
    msg = "👾•°•°• Wootteo ligando os motores•°•°•👾"
    await discord_send(msg)

    await bot_ticket.send_message(chat_id=CHAT_ID, text=msg)
    await bot_blue.send_message(chat_id=CHAT_ID, text=msg)
    await bot_ticket.send_message(chat_id=ADMIN_ID, text=msg)

# =========================
# COMMANDS
# =========================

TESTE_TEXT = """🌊TESTE🌊
📅Data: 13/06
🔗Link: https://ibighit.com/en/bts/tour/
📍Setor: Porão da Big Hit
🎫Categoria: Army
🎟️Tipo: OT7
📦Status: disponível
📊Qtd: 07
"""

STATUS_TEXT = lambda: f"""🟢🔮STATUS WOOTTEO🔮
⏰ Uptime: {get_uptime()}
📊 Ticket Checks: {check_ticket}
📊 Blue Checks: {check_blue}
"""

async def teste(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(TESTE_TEXT)
    await discord_send(TESTE_TEXT)

async def status(update: Update, context: Context