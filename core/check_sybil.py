import requests
from eth_account import Account
from fake_useragent import UserAgent
from utils import logger

def get_address(private_key):
    wallet_address = Account.from_key(private_key).address
    return wallet_address

def sybil_check(private_key, proxy=None):

    ip, port, login, password = proxy.split(":")
    proxy_url = f"http://{login}:{password}@{ip}:{port}"

    ua = UserAgent()
    address = get_address(private_key)
    url = f"https://trailblazer.mainnet.taiko.xyz/s2/user/rank?address={address}"
    headers = {
        'user-agent': ua.random
    }

    proxies = {
        "http": proxy_url,
        "https": proxy_url
    } if proxy_url else None

    try:

        response = requests.get(url, headers=headers, proxies=proxies)
        response.raise_for_status()
        data = response.json()
        sybil = data.get("blacklisted", "N/A")
        logger.info(f"Wallet: {address} Sybil: {sybil}")
    except requests.RequestException as e:
        logger.error(f"Error : {e}")

