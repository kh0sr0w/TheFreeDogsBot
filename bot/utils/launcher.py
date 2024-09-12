import os
import glob
import asyncio
import argparse
from itertools import cycle

from pyrogram import Client
from better_proxy import Proxy
from bot.utils.settings import config
from bot.utils.logger import logger
from bot.core.bot import run_bot
from bot.utils.registrator import register_sessions


start_text = """
 _____ _            _____                ____                    ____        _   
|_   _| |__   ___  |  ___| __ ___  ___  |  _ \  ___   __ _ ___  | __ )  ___ | |_ 
  | | | '_ \ / _ \ | |_ | '__/ _ \/ _ \ | | | |/ _ \ / _` / __| |  _ \ / _ \| __| 
  | | | | | |  __/ |  _|| | |  __/  __/ | |_| | (_) | (_| \__ \ | |_) | (_) | |_ 
  |_| |_| |_|\___| |_|  |_|  \___|\___| |____/ \___/ \__, |___/ |____/ \___/ \__| 
                                                     |___/     © Kh0sr0w Bots ...
                                                                                 
Select an action:

    1. Run clicker
    2. Create session
"""

def get_session_names() -> list[str]:
    return sorted(
        os.path.splitext(os.path.basename(file))[0]
        for file in glob.glob("sessions/*.session")
    )

def get_proxies() -> list[Proxy]:
    if config.USE_PROXY_FROM_FILE:
        with open("bot/config/proxies.txt", encoding="utf-8-sig") as file:
            return [Proxy.from_str(row.strip()).as_url for row in file]
    return []

async def get_tg_clients() -> list[Client]:
    session_names = get_session_names()
    if not session_names:
        raise FileNotFoundError("No session files found.")
    return [
        Client(
            name=session_name,
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            workdir="sessions/",
            plugins=dict(root="bot/plugins"),
        )
        for session_name in session_names
    ]

async def run_tasks(tg_clients: list[Client]):
    proxies = get_proxies()
    proxies_cycle = cycle(proxies) if proxies else None
    tasks = [
        asyncio.create_task(
            run_bot(tg_client=tg_client, proxy=next(proxies_cycle) if proxies_cycle else None)
        )
        for tg_client in tg_clients
    ]
    await asyncio.gather(*tasks)

async def process() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--action", type=int, help="Action to perform")
    args = parser.parse_args()
    
    logger.info(f"Detected {len(get_session_names())} sessions | {len(get_proxies())} proxies")
    print(start_text)
    action = args.action or input("> ")
    while action not in {"1", "2"}:
        logger.warning("Action must be 1 or 2")
        action = input("> ")

    if action == "2":
        await register_sessions()
    elif action == "1":
        tg_clients = await get_tg_clients()
        await run_tasks(tg_clients=tg_clients)
