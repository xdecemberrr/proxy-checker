import asyncio
import ctypes
import functools
import os

from aiohttp import ClientSession, ClientTimeout
from aiohttp_socks import ProxyConnector
from tasksio import TaskPool

RESET = "\u001b[0m"
GREEN = "\u001b[32;1m"
CYAN = "\u001b[36;1m"


class Proxied:
    def __init__(self, proxytype: str, timeout: int) -> None:
        self.proxytype = proxytype
        self.timeout = ClientTimeout(timeout)

        self.working = []
        self.invalid = 0

    def _title_updater(self) -> None:
        while len(self.working) + self.invalid != len(self.proxies):
            ctypes.windll.kernel32.SetConsoleTitleW(
                f"[Proxy Checker] - Checking | Checked: "
                f"{len(self.working) + self.invalid}/{len(self.proxies)}"
                f" | Working: {len(self.working)} | Not Working {self.invalid}"
            )

    async def _check(self, proxy: str) -> None:
        try:
            async with ClientSession(
                timeout=self.timeout,
                connector=ProxyConnector.from_url(f"{self.proxytype}://{proxy}"),
            ) as session:
                async with session.get("https://api.ipify.org/"):
                    self.working.append(proxy)
                    print(f"{GREEN}[{RESET}WORKING{GREEN}] {proxy} {RESET}")
        except Exception:
            self.invalid += 1

    async def start(self) -> None:
        with open("proxies.txt", encoding="utf-8") as f:
            self.proxies = [i.strip() for i in f]

        loop.run_in_executor(None, functools.partial(self._title_updater))

        async with TaskPool(1_000) as pool:
            for proxy in self.proxies:
                await pool.put(self._check(proxy))

        if len(self.working) > 1:
            with open(f"working-{self.proxytype}.txt", "w") as f:
                f.write("\n".join(self.working))

        print(f"\n{CYAN}[{RESET}+{CYAN}]{RESET} Done checking")
        os.system("pause >NUL")


if __name__ == "__main__":
    os.system("cls && title [Proxy Checker] - github.com/xdecemberrr")

    proxytype = input(
        f"{CYAN}[{RESET}1{CYAN}] HTTP\n"
        f"{CYAN}[{RESET}2{CYAN}] SOCKS4\n"
        f"{CYAN}[{RESET}3{CYAN}] SOCKS5\n\n"
        f"{CYAN}[{RESET}>{CYAN}]{RESET} "
    )

    print()

    if proxytype not in ("1", "2", "3"):
        print(f"{CYAN}[{RESET}!{CYAN}]{RESET} Invalid proxy type")
        os.system("pause >NUL")
        os._exit(0)

    proxytype = {"1": "http", "2": "socks4", "3": "socks5"}[proxytype]

    try:
        timeout = int(input(f"{CYAN}[{RESET}>{CYAN}]{RESET} Timeout: "))
    except ValueError:
        print(f"{CYAN}[{RESET}!{CYAN}]{RESET} Invalid timeout")
        os.system("pause >NUL")
        os._exit(0)

    print()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(Proxied(proxytype, timeout).start())
