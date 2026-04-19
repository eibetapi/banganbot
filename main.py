# =============================================================
# 19 MOTOR DE MONITORAMENTO (VERSÃO CORRIGIDA)
# =============================================================

async def monitor_loop():
    """
    Motor principal: Gerencia o ciclo de varredura e atualiza o painel.
    """
    # 1. Aguarda o Discord estar pronto
    await bot_discord.wait_until_ready()
    
    # 2. INICIALIZAÇÃO (Substituindo safe_boot por send_boot)
    # Esta é a correção para o erro da linha 874
    try:
        await send_boot() 
        print("[SISTEMA] Painel Arirang iniciado com sucesso.")
    except Exception as e:
        print(f"[BOOT ERROR] Falha na inicialização: {e}")

    # 3. Referência às variáveis globais para os contadores
    global total_tickets, total_buy, total_weverse, total_social
    global last_ticket_check, last_buy_check, last_weverse_check, last_social_check

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                # --- CICLO DE VARREDURA ---
                
                # Ticketmaster
                await check_ticketmaster(session)
                total_tickets += 1
                last_ticket_check = datetime.now()
                
                # BuyTicket
                await check_buyticket(session)
                total_buy += 1
                last_buy_check = datetime.now()

                # Weverse
                await check_weverse(session)
                total_weverse += 1
                last_weverse_check = datetime.now()

                # Redes Sociais
                await check_social(session)
                total_social += 1
                last_social_check = datetime.now()

                # --- ATUALIZAÇÃO DO PAINEL ---
                # Edita o post existente no Telegram e Discord
                await update_panel()

                # Intervalo de segurança entre ciclos
                await asyncio.sleep(30)

            except Exception as e:
                print(f"[MONITOR ERROR] Falha no ciclo: {e}")
                await asyncio.sleep(10)
