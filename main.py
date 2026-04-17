import asyncio
import time
import requests
import hashlib
from bs4 import BeautifulSoup
import os
import re
from datetime import datetime

from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from flask import Flask
from threading import Thread

# =========================
# KEEP ALIVE
# =========================

app_web = Flask(__name__)

@app_web.route('/')
def home():
    return "Bots rodando"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app_web.run(host="0.0.0.0", port=port)

def keep_alive():
    Thread(target=run_web, daemon=True).start()


# =========================
# CONFIG
# =========================

CHAT_ID = -1003972186058

start_time = time.time()

bot_ticket = None

panel_message_id = None
panel_chat_id = CHAT_ID

check_ticket = 0
check_blue = 0

last_ticket_check = time.time()
last_blue_check = time.time()


# =========================
# LINKS (NÃO REMOVER)
# =========================

TICKET_LINKS = [
    "https://www.ticketmaster.com.br/event/venda-geral-bts-world-tour-arirang-28-10",
    "https://www.ticketmaster.com.br/event/venda-geral-bts-world-tour-arirang-30-10",
    "https://www.ticketmaster.com.br/event/venda-geral-bts-world-tour-arirang-31-10"
]

BLUE_LINKS = [
    "https://buyticketbrasil.com/evento/bts-2026-world-tour-arirang"
]


# =========================
# AGENDA FIXA
# =========================

AGENDA = [
("25/04/2026", "Tampa", "EUA", "20:00"),
    ("26/04/2026", "Tampa", "EUA", "20:00"),
    ("28/04/2026", "Tampa", "EUA", "20:00"),
    ("02/05/2026", "El Paso", "EUA", "20:00"),
    ("03/05/2026", "El Paso", "EUA", "20:00"),
    ("07/05/2026", "Cidade do México", "México", "20:00"),
    ("09/05/2026", "Cidade do México", "México", "20:00"),
    ("10/05/2026", "Cidade do México", "México", "20:00"),
    ("16/05/2026", "Stanford", "EUA", "20:00"),
    ("17/05/2026", "Stanford", "EUA", "20:00"),
    ("19/05/2026", "Stanford", "EUA", "20:00"),
    ("23/05/2026", "Las Vegas", "EUA", "20:00"),
    ("24/05/2026", "Las Vegas", "EUA", "20:00"),
    ("27/05/2026", "Las Vegas", "EUA", "20:00"),
    ("28/05/2026", "Las Vegas", "EUA", "20:00"),
    ("12/06/2026", "Busan", "Coreia do Sul", "20:00"),
    ("13/06/2026", "Busan", "Coreia do Sul", "20:00"),
    ("26/06/2026", "Madri", "Espanha", "20:00"),
    ("27/06/2026", "Madri", "Espanha", "20:00"),
    ("01/07/2026", "Bruxelas", "Bélgica", "20:00"),
    ("02/07/2026", "Bruxelas", "Bélgica", "20:00"),
    ("06/07/2026", "Londres", "Reino Unido", "20:00"),
    ("07/07/2026", "Londres", "Reino Unido", "20:00"),
    ("11/07/2026", "Munique", "Alemanha", "20:00"),
    ("12/07/2026", "Munique", "Alemanha", "20:00"),
    ("17/07/2026", "Saint-Denis", "França", "20:00"),
    ("18/07/2026", "Saint-Denis", "França", "20:00"),
    ("01/08/2026", "East Rutherford", "EUA", "20:00"),
    ("02/08/2026", "East Rutherford", "EUA", "20:00"),
    ("02/10/2026", "Bogotá", "Colômbia", "20:00"),
    ("03/10/2026", "Bogotá", "Colômbia", "20:00"),
    ("07/10/2026", "Lima", "Peru", "20:00"),
    ("09/10/2026", "Lima", "Peru", "20:00"),
    ("10/10/2026", "Lima", "Peru", "20:00"),
    ("14/10/2026", "Santiago", "Chile", "20:00"),
    ("16/10/2026", "Santiago", "Chile", "20:00"),
    ("17/10/2026", "Santiago", "Chile", "20:00"),
    ("21/10/2026", "Buenos Aires", "Argentina", "20:00"),
    ("23/10/2026", "Buenos Aires", "Argentina", "20:00"),
    ("24/10/2026", "Buenos Aires", "Argentina", "20:00"),
    ("28/10/2026", "São Paulo", "Brasil", "20:00"),
    ("30/10/2026", "São Paulo", "Brasil", "20:00"),
    ("31/10/2026", "São Paulo", "Brasil", "20:00"),
    ("19/11/2026", "Kaohsiung", "Taiwan", "20:00"),
    ("21/11/2026", "Kaohsiung", "Taiwan", "20:00"),
    ("22/11/2026", "Kaohsiung", "Taiwan", "20:00"),
    ("03/12/2026", "Banguecoque", "Tailândia", "20:00"),
    ("05/12/2026", "Banguecoque", "Tailândia", "20:00"),
    ("06/12/2026", "Banguecoque", "Tailândia", "20:00"),
    ("12/12/2026", "Kuala Lumpur", "Malásia", "20:00"),
    ("13/12/2026", "Kuala Lumpur", "Malásia", "20:00"),
    ("17/12/2026", "Singapura", "Singapura", "20:00"),
    ("19/12/2026", "Singapura", "Singapura", "20:00"),
    ("20/12/2026", "Singapura", "Singapura", "20:00"),
    ("22/12/2026", "Singapura", "Singapura", "20:00"),
    ("26/12/2026", "Jacarta", "Indonésia", "20:00"),
    ("27/12/2026", "Jacarta", "Indonésia", "20:00"),
    ("12/02/2027", "Melbourne", "Austrália", "20:00"),
    ("13/02/2027", "Melbourne", "Austrália", "20:00"),
    ("20/02/2027", "Sydney", "Austrália", "20:00"),
    ("21/02/2027", "Sydney", "Austrália", "20:00"),
    ("04/03/2027", "Hong Kong", "China", "20:00"),
    ("06/03/2027", "Hong Kong", "China", "20:00"),
    ("07/03/2027", "Hong Kong", "China", "20:00"),
    ("13/03/2027", "Manila", "Filipinas", "20:00"),
    ("14/03/2027", "Manila", "Filipinas", "20:00")
]


# =========================
# CONTROLE
# =========================

boot_lock = True


# =========================
# UTIL
# =========================

def get_uptime():
    s = int(time.time() - start_time)
    return f"{s//3600}h {(s%3600)//60}m {s%60}s"

def resolve_status(found):
    return "DISPONÍVEL" if found else "ESGOTADO"

def clean(v):
    return v if v and str(v).strip() else "ESGOTADO"

def days_left(date_str):
    try:
        d = datetime.strptime(date_str, "%d/%m/%Y")
        delta = (d - datetime.now()).days
        return max(delta, 0)
    except:
        return "..."

def minutes_since(ts):
    return int((time.time() - ts) / 60)

def get_next_show():
    now = datetime.now()
    for item in AGENDA:
        try:
            date_str = item[0]  
            # Monta o Local combinando Cidade e País
            city_info = f"{item[1]}, {item[2]}" 
            time_str = item[3]  

            # Compara a data e o horário atual com o início do show
            dt_show = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M")

            # Se o momento atual ainda não chegou no horário do show, esse é o próximo
            if dt_show > now:
                return date_str, city_info, days_left(date_str)
        except:
            continue
    return "Continua…", "---", "0"



# =========================
# 1. MENSAGEM DE RESET / RECONNECT
# =========================

async def send_boot():
    global boot_lock, panel_message_id, panel_chat_id
    boot_lock = True

    await bot_ticket.send_message(chat_id=CHAT_ID, text="🛸•°•Wootteo entrando em rota°•°🛸")

    # Ordem obrigatória: Garantir painel atualizado ou novo fixado após reset
    create_new = True
    if panel_message_id:
        try:
            await update_panel()
            create_new = False
        except:
            create_new = True

    if create_new:
        msg = await bot_ticket.send_message(
            chat_id=CHAT_ID,
            text="👾 PAINEL DE CONTROLE 👾\n\nInicializando..."
        )
        panel_message_id = msg.message_id
        try:
            await bot_ticket.pin_chat_message(chat_id=CHAT_ID, message_id=panel_message_id, disable_notification=True)
        except Exception as e:
            print(f"Erro ao fixar: {e}")

    boot_lock = False
    await update_panel()


# =========================
# 2. PAINEL FIXADO
# =========================

async def update_panel():
    global panel_message_id
    if not panel_message_id: return

    data, city, dias = get_next_show()
    dias_br = days_left("28/10/2026")

    text = f"""🔴*⊙⊝⊜ ARIRANG TOUR ⊙⊝⊜*🔴

✈️ *PRÓXIMAS DATAS*

🎫 *Data:* {data}
📍 *Local:* {city}
🔔 Faltam {dias} dias.

⏳Faltam {dias_br} dias para o BTS no Brasil.

🟡 Ticketmaster
acessos realizado: {check_ticket} | último rastreio há {minutes_since(last_ticket_check)} min
🔵 Buyticket
acessos realizado: {check_blue} | último rastreio há {minutes_since(last_blue_check)} min
"""
    try:
        await bot_ticket.edit_message_text(chat_id=panel_chat_id, message_id=panel_message_id, text=text, parse_mode="Markdown")
    except:
        pass


# =========================
# 3. ALERTAS OFICIAIS (ORDEM: REPOSIÇÃO, NOVAS DATAS, REVENDA, AGENDA)
# =========================

async def ticket_reposicao(url, key, found):
    # Travas obrigatórias para Brasil
    if any(x in str(key) for x in ["28/10", "30/10", "31/10"]):
        msg = f"""🔥*ALERTA DE REPOSIÇÃO*🔥
📅 *Data:* {clean(key)}
🔗 *Link:* {url}
📍 *Setor:* ESGOTADO
🎫 *Categoria:* ESGOTADO
🛡️ *Tipo:* ESGOTADO
✅ *Status:* {resolve_status(found)}
"""
        await bot_ticket.send_message(chat_id=CHAT_ID, text=msg)


async def ticket_nova_data(url, key, found):
    if any(x in str(key) for x in ["28/10", "30/10", "31/10"]) or "Brasil" in str(key):
        msg = f"""🎁*ALERTA DE NOVA DATA*🎁
📅 *Data:* {clean(key)}
🔗 *Link:* {url}
📍 *Setor:* ESGOTADO
🎫 *Categoria:* ESGOTADO
🛡️ *Tipo:* ESGOTADO
📊 *Quantidade:* ESGOTADO
✅ *Status:* {resolve_status(found)}
"""
        await bot_ticket.send_message(chat_id=CHAT_ID, text=msg)


async def blue_revenda(url, key, found):
    if any(x in str(key) for x in ["28/10", "30/10", "31/10"]):
        msg = f"""🔵*REVENDA BLUE*🔵
📅 *Data:* {clean(key)}
🔗 *Link:* {url}
📍 *Setor:* ESGOTADO
💰 *Valor:* ESGOTADO
🎫 *Categoria:* ESGOTADO
🛡️ *Tipo:* ESGOTADO
✅ *Status:* {resolve_status(found)}
"""
        await bot_ticket.send_message(chat_id=CHAT_ID, text=msg)


async def agenda_update(data):
    country = str(data.get('country', ''))
    city = str(data.get('city', ''))
    if "Brasil" in country or "Paulo" in city or "Brasil" in str(data):
        msg = f"""💜*AGENDA NOVAS DATAS*💜
📅 *Data:* {clean(data.get('date'))}
🏙️ *Cidade:* {clean(data.get('city'))}
🌎 *País:* {clean(data.get('country'))}
⚠️*Mais informações em breve!*
"""
        await bot_ticket.send_message(chat_id=CHAT_ID, text=msg)


# =========================
# 4. ALERTAS DE TESTE (ORDEM CRONOLÓGICA BRASIL)
# =========================

async def test_reposicao(url, key, found):
    msg = f"""⚠️**TESTE**⚠️

🔥*ALERTA DE REPOSIÇÃO*🔥
📅 *Data:* {clean(key)}
🔗 *Link:* {url}
📍 *Setor:* ESGOTADO
🎫 *Categoria:* ESGOTADO
🛡️ *Tipo:* ESGOTADO
✅ *Status:* {resolve_status(found)}
"""
    await bot_ticket.send_message(chat_id=CHAT_ID, text=msg)


async def test_nova_data(url, key, found):
    msg = f"""⚠️**TESTE**⚠️

🎁*ALERTA DE NOVA DATA*🎁
📅 *Data:* {clean(key)}
🔗 *Link:* {url}
📍 *Setor:* ESGOTADO
🎫 *Categoria:* ESGOTADO
🛡️ *Tipo:* ESGOTADO
📊 *Quantidade:* ESGOTADO
✅ *Status:* {resolve_status(found)}
"""
    await bot_ticket.send_message(chat_id=CHAT_ID, text=msg)


async def test_blue(url, key, found):
    msg = f"""⚠️**TESTE**⚠️

🔵*REVENDA BLUE*🔵
📅 *Data:* {clean(key)}
🔗 *Link:* {url}
📍 *Setor:* ESGOTADO
💰 *Valor:* ESGOTADO
🎫 *Categoria:* ESGOTADO
🛡️ *Tipo:* ESGOTADO
✅ *Status:* {resolve_status(found)}
"""
    await bot_ticket.send_message(chat_id=CHAT_ID, text=msg)


async def test_agenda(data):
    msg = f"""⚠️**TESTE**⚠️

💜*AGENDA NOVAS DATAS*💜
📅 *Data:* {clean(data.get('date'))}
🏙️ *Cidade:* {clean(data.get('city'))}
🌎 *País:* {clean(data.get('country'))}
⚠️*Mais informações em breve!*
"""
    await bot_ticket.send_message(chat_id=CHAT_ID, text=msg)


# =========================
# 5. COMANDOS (PV)
# =========================

async def handle_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    if update.message.chat.type != "private": return

    text = update.message.text.lower()

    if "/teste" in text:
        # Ordem Cronológica: 28, 30 e 31
        await test_reposicao(TICKET_LINKS[0], "28/10/2026", True)
        await test_nova_data(TICKET_LINKS[1], "30/10/2026", True)
        await test_reposicao(TICKET_LINKS[2], "31/10/2026", True)
        await test_blue(BLUE_LINKS[0], "28/10/2026", True)
        await test_agenda({"date": "28/10/2026", "city": "São Paulo", "country": "Brasil"})


# =========================
# 6. LOOPS
# =========================

async def monitor():
    global check_ticket, check_blue, last_ticket_check, last_blue_check
    while True:
        if not boot_lock:
            check_ticket += 1
            check_blue += 1
            last_ticket_check = time.time()
            last_blue_check = time.time()
        await asyncio.sleep(30)

async def panel_loop():
    while True:
        if not boot_lock: await update_panel()
        await asyncio.sleep(5)


# =========================
# 7. MAIN
# =========================

async def main():
    global bot_ticket
    keep_alive()

    token = os.getenv("BOT_TOKEN_TICKET")
    if not token: return

    app = ApplicationBuilder().token(token).build()
    bot_ticket = app.bot

    app.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.TEXT, handle_commands))

    await app.initialize()
    await app.start()
    await bot_ticket.delete_webhook(drop_pending_updates=True)
    
    await send_boot()

    asyncio.create_task(monitor())
    asyncio.create_task(panel_loop())

    await app.updater.start_polling()
    
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())


