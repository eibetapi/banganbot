# =========================
# 21 ALERT ENGINE (ROTEAMENTO INTELIGENTE)
# =========================

ALERT_LOCK = asyncio.Lock()

async def send_discord(channel_id, message):
    """
    Função auxiliar para enviar mensagens para canais específicos do Discord.
    Resolve o erro 'send_discord is not defined'.
    """
    try:
        # Garante que o ID seja um inteiro
        channel = bot_discord.get_channel(int(channel_id))
        if channel:
            await channel.send(message)
        else:
            print(f"[DISCORD ERROR] Canal {channel_id} não encontrado. Verifique se o Bot está no servidor.")
    except Exception as e:
        print(f"[DISCORD SEND ERROR] Falha ao enviar para o canal {channel_id}: {e}")

async def send_alert(alert_type, message):
    """
    Envia alertas para Telegram e Discord de forma sincronizada e categorizada.
    Trata o erro 'Chat not found' no Telegram de forma silenciosa.
    """
    async with ALERT_LOCK:
        # --- TELEGRAM (CANAL OFICIAL) ---
        if bot_ticket:
            try:
                # Verifica se o CHAT_ID existe antes de tentar enviar
                if CHAT_ID:
                    await bot_ticket.send_message(
                        chat_id=CHAT_ID,
                        text=message,
                        parse_mode="Markdown"
                    )
            except Exception as e:
                # Caso o erro 'Chat not found' persista, ele será logado aqui sem travar o bot
                print(f"[TELEGRAM ALERT ERROR] Verifique o CHAT_ID ou se o bot é admin: {e}")

        # --- DISCORD (ROTEAMENTO POR CANAL ESPECÍFICO) ---
        try:
            loop = asyncio.get_running_loop()
            
            # Categorização de Ingressos
            if alert_type in ["ticket", "reposicao", "nova_data", "revenda", "agenda"]:
                loop.create_task(send_discord(DISCORD_TICKETS_CHANNEL_ID, message))

            # Categorização Weverse
            elif alert_type in ["weverse_post", "weverse_live", "weverse_news", "weverse_media"]:
                loop.create_task(send_discord(DISCORD_WEVERSE_CHANNEL_ID, message))

            # Categorização Redes Sociais
            elif alert_type in ["instagram_post", "instagram_reels", "instagram_stories", "instagram_live", "tiktok_post", "tiktok_live"]:
                loop.create_task(send_discord(DISCORD_SOCIAL_CHANNEL_ID, message))

            # Notícias Gerais / Fallback
            else:
                if 'DISCORD_NEWS_CHANNEL_ID' in globals():
                    loop.create_task(send_discord(DISCORD_NEWS_CHANNEL_ID, message))
                
        except Exception as e:
            print(f"[DISCORD ROUTING ERROR] Falha no roteamento do alerta {alert_type}: {e}")
