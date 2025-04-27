from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, random, base64, json, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class CryplexAi:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "application/json",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "chrome-extension://mpneoffefkhpfimnfmikkfgehgdahcdc",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "none",
            "User-Agent": FakeUserAgent().random
        }
        self.BASE_API = "https://app.cryplex.ai/apiv2"
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Auto Ping {Fore.BLUE + Style.BRIGHT}Cryplex AI - BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    async def load_proxies(self, use_proxy_choice: int):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.get("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt") as response:
                        response.raise_for_status()
                        content = await response.text()
                        with open(filename, 'w') as f:
                            f.write(content)
                        self.proxies = content.splitlines()
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = f.read().splitlines()
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, account):
        if account not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[account] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[account]

    def rotate_proxy_for_account(self, account):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[account] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def decode_token(self, token: str):
        try:
            header, payload, signature = token.split(".")
            decoded_payload = base64.urlsafe_b64decode(payload + "==").decode("utf-8")
            parsed_payload = json.loads(decoded_payload)
            address = parsed_payload["address"]
            
            return address
        except Exception as e:
            return None
        
    def generate_payload(self, token: str, model_chunks: dict):
        try:
            entries = list(model_chunks.items())
            id, base64data = random.choice(entries)
            data_length = len(base64data)
            start = random.randint(0, data_length - 2)
            end = start + 1 + random.randint(0, data_length - start - 1)
            sliced_data = base64data[start:end]

            payload = {
                "data":sliced_data,
                "model_using":"Spark",
                "id":id,
                "start":start,
                "end":end,
                "__ssoToken":token
            }

            return payload
        except Exception as e:
            return None
    
    def mask_account(self, account):
        mask_account = account[:6] + '*' * 6 + account[-6:]
        return mask_account
    
    def print_message(self, account, proxy, color, message):
        self.log(
            f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} {account} {Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT} Proxy: {Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
            f"{color + Style.BRIGHT} {message} {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
        )

    def print_question(self):
        while True:
            try:
                print("1. Run With Monosans Proxy")
                print("2. Run With Private Proxy")
                print("3. Run Without Proxy")
                proxy_choice = int(input("Choose [1/2/3] -> ").strip())

                if proxy_choice in [1, 2, 3]:
                    proxy_type = (
                        "Run With Monosans Proxy" if proxy_choice == 1 else 
                        "Run With Private Proxy" if proxy_choice == 2 else 
                        "Run Without Proxy"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{proxy_type} Selected.{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

            nodes_count = 0
            if proxy_choice in [1, 2]:
                while True:
                    try:
                        nodes_count = int(input("How Many Nodes Do You Want to Run For Each Account? -> ").strip())
                        if nodes_count > 0:
                            break
                        else:
                            print(f"{Fore.RED+Style.BRIGHT}Please enter a positive number.{Style.RESET_ALL}")
                    except ValueError:
                        print(f"{Fore.RED+Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

            return nodes_count, proxy_choice

    async def start_node(self, token: str, address: str, count: int, proxy=None, retries=5):
        url = f"https://app.cryplex.ai/apiv2/node/Start"
        data = json.dumps({"__ssoToken":token})
        headers = {
            **self.headers,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(self.mask_account(address), proxy, Fore.WHITE, f"Node {count} "
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT} Start Failed: {Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )

    async def sync_node(self, token: str, address: str, model_chunks: dict, count: int, proxy=None, retries=5):
        url = f"{self.BASE_API}/node/SyncFile"
        data = json.dumps(self.generate_payload(token, model_chunks))
        headers = {
            **self.headers,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(self.mask_account(address), proxy, Fore.WHITE, f"Node {count} "
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT} Sync File Failed: {Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )
            
    async def process_perform_node(self, token: str, address: str, count: int, use_proxy: bool):
        proxy = self.get_next_proxy_for_account(f"{address}_{count}") if use_proxy else None
        start = None
        while start is None:
            start = await self.start_node(token, address, count, proxy)
            if not start:
                await asyncio.sleep(5)
                continue
            
            self.print_message(self.mask_account(address), proxy, Fore.WHITE, f"Node {count}"
                f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                f"{Fore.GREEN + Style.BRIGHT}Started Successfully{Style.RESET_ALL}"
            )

            model_chunks = start.get("res", {}).get("modelChunks", {})
            
            while True:
                sync = await self.sync_node(token, address, model_chunks, count, proxy)
                if sync and sync.get("isSucc"):
                    self.print_message(self.mask_account(address), proxy, Fore.WHITE, f"Node {count}"
                        f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                        f"{Fore.GREEN + Style.BRIGHT}Sync File Successfully{Style.RESET_ALL}"
                    )

                await asyncio.sleep(30)

    async def process_accounts(self, token: str, address: str, nodes_count: int, use_proxy: bool):
        tasks = []
        if use_proxy:
            for i in range(nodes_count):
                count = i + 1
                tasks.append(asyncio.create_task(self.process_perform_node(token, address, count, use_proxy)))
        else:
            count = 1
            tasks.append(asyncio.create_task(self.process_perform_node(token, address, count, use_proxy)))

        await asyncio.gather(*tasks)
        
    async def main(self):
        try:
            with open('tokens.txt', 'r') as file:
                tokens = [line.strip() for line in file if line.strip()]

            nodes_count, use_proxy_choice = self.print_question()

            use_proxy = False
            if use_proxy_choice in [1, 2]:
                use_proxy = True

            self.clear_terminal()
            self.welcome()
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(tokens)}{Style.RESET_ALL}"
            )

            if use_proxy:
                await self.load_proxies(use_proxy_choice)

            self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)

            while True:
                tasks = []
                for token in tokens:
                    if token:
                        address = self.decode_token(token)

                        if address:
                            tasks.append(asyncio.create_task(self.process_accounts(token, address, nodes_count, use_proxy)))

                await asyncio.gather(*tasks)
                await asyncio.sleep(10)

        except FileNotFoundError:
            self.log(f"{Fore.RED}File 'tokens.txt' Not Found.{Style.RESET_ALL}")
            return
        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        bot = CryplexAi()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Cryplex AI - BOT{Style.RESET_ALL}                                       "                              
        )