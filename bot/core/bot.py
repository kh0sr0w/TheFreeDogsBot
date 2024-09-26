import asyncio
import aiohttp
import random
import hashlib
from time import time
from datetime import datetime, timezone, timedelta
from urllib.parse import unquote
from typing import Any, Dict
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from pyrogram import Client
from pyrogram.errors import Unauthorized, UserDeactivated, AuthKeyUnregistered
from pyrogram.raw.functions.messages import RequestWebView
from bot.utils.logger import log
from bot.utils.settings import config
from .headers import headers

# API endpoints
api_userProfile = 'https://api.freedogs.bot/miniapps/api/mine/getMineInfo'
api_gameProfile = 'https://api.freedogs.bot/miniapps/api/user_game_level/GetGameInfo'
api_tap = 'https://api.freedogs.bot/miniapps/api/user_game/collectCoin'
api_auth = 'https://api.freedogs.bot/miniapps/api/user/telegram_auth/'

# Hash generating function
def get_hash(collect_amount, collect_seq_no):
    salt = "7be2a16a82054ee58398c5edb7ac4a5a"
    concatenated_string = f"{collect_amount}{collect_seq_no}{salt}"
    return hashlib.md5(concatenated_string.encode()).hexdigest()

class CryptoBot:
    def __init__(self, tg_client: Client):
        self.session_name = tg_client.name
        self.tg_client = tg_client
        self.first_name = ''
        self.last_name = ''
        self.user_id = ''
        self.coin_balance = 0
        self.collect_seq_no = 0
        self.coin_pool_left = 0
        self.errors = 0
        self.authorized = False
        self.access_token = ''
        self.userToDayNowClick = 0
        self.userToDayMaxClick = 0


    async def get_tg_web_data(self, proxy: str | None) -> str:
        if proxy:
            proxy = Proxy.from_str(proxy)
            proxy_dict = dict(
                scheme=proxy.protocol,
                hostname=proxy.host,
                port=proxy.port,
                username=proxy.login,
                password=proxy.password
            )
        else:
            proxy_dict = None

        self.tg_client.proxy = proxy_dict

        try:
            if not self.tg_client.is_connected:
                try:
                    await self.tg_client.connect()
                except (Unauthorized, UserDeactivated, AuthKeyUnregistered) as error:
                    raise RuntimeError(str(error)) from error

            # Resolve the peer
            try:
                peer = await self.tg_client.resolve_peer('theFreeDogs_bot')
                # print(peer)
            except ValueError as error:
                log.error(f"{self.session_name} | Failed to resolve peer 'theFreeDogs_bot': {error}")
                return ''  # Return empty string to handle appropriately

            web_view = await self.tg_client.invoke(RequestWebView(
                peer= peer,
                bot= peer,
                platform='android',
                from_bot_menu=False,
                url='https://app.freedogs.bot/',
            ))
            auth_url = web_view.url
            tg_web_data = unquote(
                string=auth_url.split('tgWebAppData=', maxsplit=1)[1].split('&tgWebAppVersion', maxsplit=1)[0])

            return tg_web_data

        except RuntimeError as error:
            raise error

        except Exception as error:
            log.error(f"{self.session_name} | Authorization error: {error}")
            await asyncio.sleep(delay=3)
            return ''

    async def login(self, init_data: str) -> str | bool:
        try:
            log.info(f"{self.session_name} | Trying to login...")
            self.http_client.headers.pop('Authorization', None)
            # to get query data un comment the below code
            with open('query.txt', 'a') as file:
                file.write(init_data + '\n')

            json_data = {'initData': init_data}
            await self.http_client.options(api_auth, data=json_data)
            response = await self.http_client.post(api_auth, data=json_data)
            response.raise_for_status()
            response_json = await response.json()

            access_token = response_json.get("data", {}).get("token")

            if access_token:
                log.success(f"{self.session_name} | Login successful")
                return access_token
            else:
                log.error(f"{self.session_name} | Failed to fetch access token.")
                return False

        except aiohttp.ClientResponseError as error:
            if error.status == 401:
                self.authorized = False
            self.errors += 1
            log.error(f"{self.session_name} | Login http error: {error}")
            await asyncio.sleep(delay=3)
            return False

        except Exception as error:
            log.error(f"{self.session_name} | Login error: {error}")
            await asyncio.sleep(delay=3)
            return False

    async def get_user_profile(self) -> Dict[str, Any]:
        try:
            await self.http_client.options(api_userProfile)
            response = await self.http_client.get(api_userProfile)
            response.raise_for_status()
            response_json = await response.json()
            return response_json
        except aiohttp.ClientResponseError as error:
            if error.status == 401:
                self.authorized = False
            self.errors += 1
            log.error(f"{self.session_name} | User Profile data http error: {error}")
            await asyncio.sleep(delay=3)
            return {}
        except Exception as error:
            log.error(f"{self.session_name} | User Profile data error: {error}")
            await asyncio.sleep(delay=3)
            return {}

    async def get_game_profile(self) -> Dict[str, Any]:
        try:
            await self.http_client.options(api_gameProfile)
            response = await self.http_client.get(api_gameProfile)
            response.raise_for_status()
            response_json = await response.json()
            return response_json
        except aiohttp.ClientResponseError as error:
            if error.status == 401:
                self.authorized = False
            self.errors += 1
            log.error(f"{self.session_name} | Game Profile data http error: {error}")
            await asyncio.sleep(delay=3)
            return {}
        except Exception as error:
            log.error(f"{self.session_name} | Game Profile data error: {error}")
            await asyncio.sleep(delay=3)
            return {}

    async def tap(self, taps: int) -> Dict[str, Any]:
        try:
            hash_code = get_hash(taps, self.collect_seq_no)

            params = {
                "collectAmount": taps,
                "hashCode": hash_code,
                "collectSeqNo": self.collect_seq_no
            }

            await self.http_client.options(api_tap, data=params)
            response = await self.http_client.post(api_tap, data=params)
            response.raise_for_status()
            response_json = await response.json()

            return response_json
        except aiohttp.ClientResponseError as error:
            if error.status == 401:
                self.authorized = False
            self.errors += 1
            log.error(f"{self.session_name} | Taps error (Auth): {error}")
            await asyncio.sleep(delay=3)
            return {}
        except Exception as error:
            log.error(f"{self.session_name} | Taps error: {error}")
            await asyncio.sleep(delay=3)
            return {}

    async def check_proxy(self, proxy: Proxy) -> None:
        try:
            response = await self.http_client.get(url='https://httpbin.org/ip', timeout=aiohttp.ClientTimeout(5))
            ip = (await response.json()).get('origin')
            log.info(f"{self.session_name} | Proxy IP: {ip}")
        except Exception as error:
            log.error(f"{self.session_name} | Proxy: {proxy} | Error: {error}")

    async def run(self, proxy: str | None) -> None:
        access_token_created_time = 0
        proxy_conn = ProxyConnector().from_url(proxy) if proxy else None

        async with aiohttp.ClientSession(headers=headers, connector=proxy_conn) as http_client:
            self.http_client = http_client
            if proxy:
                await self.check_proxy(proxy=proxy)

            try:

                while True:
                    if self.errors >= config.ERRORS_BEFORE_STOP:
                        log.error(f"{self.session_name} | Bot stopped (too many errors)")
                        break

                    if not self.authorized:

                        tg_web_data = await self.get_tg_web_data(proxy=proxy)
                        if tg_web_data:
                            access_token = await self.login(init_data=tg_web_data)
                            if access_token:
                                self.authorized = True
                                self.access_token = access_token
                                self.http_client.headers['Authorization'] = 'Bearer ' + access_token
                                access_token_created_time = time()
                            else:
                                continue
                        else:
                            continue

                    # Token refresh handling
                    if time() - access_token_created_time >= 3600:
                        refresh_success = await self.login(init_data=tg_web_data)
                        if refresh_success:
                            self.http_client.headers['Authorization'] = 'Bearer ' + refresh_success
                            access_token_created_time = time()
                        else:
                            self.authorized = False
                            log.error(f"{self.session_name} | Token refresh failed, re-authenticating.")
                            continue

                    # Main tapping loop
                    if config.TAPS_ENABLED:
                        while True:
                            game_profile = await self.get_game_profile()
                            game_data = game_profile.get('data', {})
                            self.collect_seq_no = game_data.get('collectSeqNo', 0)
                            self.coin_pool_left = game_data.get('coinPoolLeft', 0)
                            self.coin_balance = game_data.get('currentAmount', 0)
                            self.userToDayNowClick = game_data.get('userToDayNowClick', 0)
                            self.userToDayMaxClick = game_data.get('userToDayMaxClick', 0)
                            
                            # If the user has reached the max clicks for today, sleep until 00:00 UTC
                            if self.userToDayNowClick >= 10000:
                                current_time = datetime.now(timezone.utc)
                                log.info(f"{self.session_name} | Max clicks reached for the day, waiting until 00:00 UTC.")
                                
                                # Calculate seconds until 00:00 UTC of the next day
                                next_reset_time = current_time.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
                                sleep_duration = (next_reset_time - current_time).total_seconds()

                                await asyncio.sleep(sleep_duration)
                            else:

                                taps = random.randint(config.TAPS_PER_SECOND[0], config.TAPS_PER_SECOND[1])
                                taps = min(taps, int(self.coin_pool_left))
                                # if taps <40, sleep 160 sec 
                                if taps < 40:
                                    log.info(f"{self.session_name} | Not enough taps available, sleep for 160 sec.")
                                    await asyncio.sleep(160)
                                    break
                                # if self.userToDayNowClick is >= 10000, sleep untill time is 00:00 in UTC, otherwise click

                                await self.tap(taps)

                                log.info(f"{self.session_name} | "
                                        f"Tapped {taps} times | Coin Pool Left: {int(self.coin_pool_left) - taps} | "
                                        f"Total coins: {int(self.coin_balance) + taps}")
                                await asyncio.sleep(delay=0.5)

                    await asyncio.sleep(delay=config.DEFAULT_RATE_LIMIT)

            except Exception as error:
                log.error(f"{self.session_name} | Run error: {error}")
            finally:
                if self.http_client:
                    await self.http_client.close()
                if self.tg_client.is_connected:
                    await self.tg_client.disconnect()
                    
async def run_bot(tg_client: Client, proxy: str | None):
    try:
        await CryptoBot(tg_client=tg_client).run(proxy=proxy)
        
    except RuntimeError as error:
        log.error(f"{tg_client.name} | Session error: {str(error)}")
