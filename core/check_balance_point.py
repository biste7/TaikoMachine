import requests
from eth_account import Account
from web3 import Web3
from fake_useragent import UserAgent
from config import RPC_URL
from utils import logger

web3 = Web3(Web3.HTTPProvider(RPC_URL))
if not web3.is_connected():
    raise Exception("Connection lost Ethereum node ")
ua = UserAgent()
def get_address(private_key):
    wallet_address = Account.from_key(private_key).address
    return wallet_address

def get_points(private_key):
    address = get_address(private_key)
    url = f"https://trailblazer.mainnet.taiko.xyz/s2/user/rank?address={address}"
    payload = {}
    headers = {
        'user-agent': ua.random
    }
    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        rank = data["rank"]
        total_score = data["totalScore"]
        logger.info(f"Score = {total_score} Rank = {rank} Wallet: {address}")
    except Exception as e:
        logger.error(f"Error : {e}")





