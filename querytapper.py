import aiohttp
import asyncio
import hashlib
import logging
import random
from datetime import datetime, timezone, timedelta
import urllib.parse, json
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Configure logging to display on the screen with color
logging.basicConfig(level=logging.INFO, format='%(message)s')

def get_hash(collect_amount, collect_seq_no):
    salt = "7be2a16a82054ee58398c5edb7ac4a5a"
    concatenated_string = f"{collect_amount}{collect_seq_no}{salt}"
    return hashlib.md5(concatenated_string.encode()).hexdigest()

async def get_mine_info(session, init_token):
    url = "https://api.freedogs.bot/miniapps/api/mine/getMineInfo"
    headers = {
        "Authorization": f"Bearer {init_token}",
        "Accept": "application/json, text/plain, */*",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Referer": "https://app.freedogs.bot/",
        "Origin": "https://app.freedogs.bot",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
    }

    try:
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientResponseError as e:
        logging.error(f"{Fore.RED}Failed to get Mine Info: {e.status} - {e.message}{Style.RESET_ALL}")
    except Exception as e:
        logging.error(f"{Fore.RED}Failed to get Mine Info: {e}{Style.RESET_ALL}")
    return None

async def get_game_info(session, init_token):
    url = "https://api.freedogs.bot/miniapps/api/user_game_level/GetGameInfo"
    headers = {
        "Authorization": f"Bearer {init_token}",
        "Accept": "application/json, text/plain, */*",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Referer": "https://app.freedogs.bot/",
        "Origin": "https://app.freedogs.bot",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
    }

    try:
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientResponseError as e:
        logging.error(f"{Fore.RED}Failed to get Game Info: {e.status} - {e.message}{Style.RESET_ALL}")
    except Exception as e:
        logging.error(f"{Fore.RED}Failed to get Game Info: {e}{Style.RESET_ALL}")
    return None

async def perform_tap(session, init_token, collect_amount):
    game_info = await get_game_info(session, init_token)
    if not game_info:
        logging.error(f"{Fore.RED}Failed to retrieve game info.{Style.RESET_ALL}")
        return

    collect_seq_no = game_info['data'].get('collectSeqNo')
    if collect_seq_no is None:
        logging.error(f"{Fore.RED}Collect sequence number is missing.{Style.RESET_ALL}")
        return

    hash_code = get_hash(collect_amount, collect_seq_no)

    url = "https://api.freedogs.bot/miniapps/api/user_game/collectCoin"
    headers = {
        "Authorization": f"Bearer {init_token}",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "application/json, text/plain, */*",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Referer": "https://app.freedogs.bot/",
        "Origin": "https://app.freedogs.bot",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
    }

    params = {
        "collectAmount": collect_amount,
        "hashCode": hash_code,
        "collectSeqNo": collect_seq_no
    }

    try:
        async with session.post(url, headers=headers, data=params) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientResponseError as e:
        logging.error(f"{Fore.RED}Failed to perform tap: {e.status} - {e.message}{Style.RESET_ALL}")
    except Exception as e:
        logging.error(f"{Fore.RED}Failed to perform tap: {e}{Style.RESET_ALL}")
    return None

async def fetch_access_token(session, init_data):
    url = "https://api.freedogs.bot/miniapps/api/user/telegram_auth/"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "application/json, text/plain, */*",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Referer": "https://app.freedogs.bot/",
        "Origin": "https://app.freedogs.bot",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36"
    }
    body = {
        "initData": init_data
    }

    try:
        async with session.post(url, headers=headers, data=body) as response:
            response.raise_for_status()
            data = await response.json()
            return data.get("data", {}).get("token")
    except aiohttp.ClientResponseError as e:
        logging.error(f"{Fore.RED}Request failed: {e.status} - {e.message}{Style.RESET_ALL}")
    except Exception as e:
        logging.error(f"{Fore.RED}Request failed: {e}{Style.RESET_ALL}")
    return None

def read_query():
    try:
        with open('query.txt', 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        logging.error(f"{Fore.RED}Query file not found.{Style.RESET_ALL}")
    return []

async def account_worker(init_data, index):
    async with aiohttp.ClientSession() as session:
        token = await fetch_access_token(session, init_data)
        if not token:
            logging.error(f"{Fore.RED}============== [ Query ID at - {index + 1} ] is invalid =============={Style.RESET_ALL}")
            return

        total_collected = 0
        username = json.loads(urllib.parse.unquote(urllib.parse.parse_qs(init_data)['user'][0]))['username']
        logging.info(f"{Fore.GREEN}🚀 Starting for user: {username}{Style.RESET_ALL}")
        while True:
            mine_info = await get_mine_info(session, token)
            if not mine_info:
                logging.error(f"{Fore.RED}Failed to retrieve mine info.{Style.RESET_ALL}")
                break

            game_info = await get_game_info(session, token)
            if not game_info:
                logging.error(f"{Fore.RED}Failed to retrieve game info.{Style.RESET_ALL}")
                break

            coin_pool_left = int(game_info['data'].get('coinPoolLeft', 0))
            available_balance = int(game_info['data'].get('currentAmount', 0))
            userToDayNowClick = int(game_info['data'].get('userToDayNowClick', 0))
            userToDayMaxClick = int(game_info['data'].get('userToDayMaxClick', 0))


            # If the user has reached the max clicks for today, sleep until 00:00 UTC
            if userToDayNowClick >= userToDayMaxClick:
                current_time = datetime.now(timezone.utc)
                logging.info(f"{username} | Max clicks reached for the day, waiting until 00:00 UTC.")
                
                # Calculate seconds until 00:00 UTC of the next day
                next_reset_time = current_time.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
                sleep_duration = (next_reset_time - current_time).total_seconds()

                await asyncio.sleep(sleep_duration)
            else:
                taps = min(random.randint(80, 100), int(coin_pool_left))
                if taps > 40:
                    result = await perform_tap(session, token, taps)
                    if result and result.get("code") == 0 and result.get("data", {}).get("collectStatus"):
                        total_collected += taps

                        await asyncio.sleep( random.uniform(1, 3))

                        logging.info(f"{Fore.CYAN}{datetime.now().strftime('%d-%b-%y %H:%M')} | {Fore.MAGENTA}Account: {username} | {Fore.GREEN}Tapped {Fore.YELLOW}{taps} times | {Fore.GREEN}Coin Pool Left: {coin_pool_left - taps} | {Fore.BLUE}Total coins: {available_balance}{Style.RESET_ALL}")
                    else:
                        logging.warning(f"{Fore.RED}Account {username}, failed to collect coins.{Style.RESET_ALL}")
                else:
                    logging.info(f"{Fore.YELLOW}Account {username}, waiting for coin pool to fill up. Sleeping for 3 minutes.{Style.RESET_ALL}")

                    await asyncio.sleep(180)  # Wait for 3 minutes before retrying

async def main():
    queries = read_query()

    tasks = []
    for index, init_data in enumerate(queries):
        task = asyncio.create_task(account_worker(init_data, index))
        tasks.append(task)

        await asyncio.sleep(random.uniform(1, 3))

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
