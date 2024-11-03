import time
import requests
from eth_account import Account
from web3 import Web3, HTTPProvider


from constants import weth_abi
from utils import logger
from config import RPC_URL, contract, cycles, eth_count


def create_web3_with_proxy(proxy, rpc_url):

    ip, port, login, password = proxy.split(":")
    proxy_url = f"http://{login}:{password}@{ip}:{port}"


    session = requests.Session()
    session.proxies = {
        "http": proxy_url,
        "https": proxy_url
    }


    provider = HTTPProvider(rpc_url, session=session)
    web3_instance = Web3(provider)



    if not web3_instance.is_connected():
        raise Exception("Connection lost to Ethereum node")

    return web3_instance


def get_address(private_key):
    wallet_address = Account.from_key(private_key).address
    return wallet_address


def get_nonce(web3, wallet_address):
    try:
        nonce = web3.eth.get_transaction_count(wallet_address)
        return nonce
    except (requests.exceptions.Timeout, TimeoutError, requests.exceptions.ConnectionError):
        return get_nonce(web3, wallet_address)
    except requests.exceptions.HTTPError as error:
        if '[429]' in str(error.response) or '[502]' in str(error.response):
            return get_nonce(web3, wallet_address)
        raise error


def get_gas_price(web3):
    gas_price = web3.eth.gas_price
    return gas_price


def wrap_eth(web3, weth_contract, amount_in_eth, private_key):
    transaction = weth_contract.functions.deposit().build_transaction({
        'from': get_address(private_key),
        'value': web3.to_wei(amount_in_eth, 'ether'),
        'nonce': get_nonce(web3, get_address(private_key)),
        'gasPrice': int(get_gas_price(web3) * 1.01)
    })

    transaction.update({
        'gas': web3.eth.estimate_gas(transaction),
    })

    signed_txn = web3.eth.account.sign_transaction(transaction, private_key=private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
    logger.info(f"Send transaction ETH in WETH. Hash: {web3.to_hex(tx_hash)}")
    return tx_hash


def unwrap_weth(web3, weth_contract, amount_in_weth, private_key):
    transaction = weth_contract.functions.withdraw(
        web3.to_wei(amount_in_weth, 'ether')
    ).build_transaction({
        'from': get_address(private_key),
        'nonce': get_nonce(web3, get_address(private_key)),
        'gasPrice': int(get_gas_price(web3) * 1.01)
    })

    gas_estimate = web3.eth.estimate_gas(transaction)
    transaction.update({
        'gas': gas_estimate,
    })

    signed_txn = web3.eth.account.sign_transaction(transaction, private_key=private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
    logger.info(f"Send transaction WETH in ETH. Hash: {web3.to_hex(tx_hash)}")
    return tx_hash


def check_hash(web3, hashes):
    try:
        web3.eth.wait_for_transaction_receipt(hashes)
        logger.success(f"Transaction complete {web3.to_hex(hashes)}")
    except Exception as e:
        logger.info(f"Transaction pending {str(e)}")
        check_hash(web3, hashes)


def perform_wrap_unwrap_cycles(private_key, proxy, rpc_url=RPC_URL, start_cycle=0):

    web3 = create_web3_with_proxy(proxy, rpc_url)
    weth_contract = web3.eth.contract(address=contract, abi=weth_abi)

    for i in range(start_cycle, cycles):
        logger.info(f"Cycle {i + 1} of {cycles}:")

        try:
            logger.info(f"WRAP {eth_count} ETH in WETH...")
            wrap_tx_hash = wrap_eth(web3, weth_contract, eth_count, private_key)
            check_hash(web3, wrap_tx_hash)
            time.sleep(5)
        except Exception as e:
            logger.error(f"Error WRAP ETH in WETH: {str(e)}")
            perform_wrap_unwrap_cycles(private_key, proxy, rpc_url, start_cycle=i)
            return

        try:
            logger.info(f"UNWRAP {eth_count} WETH in ETH...")
            unwrap_tx_hash = unwrap_weth(web3, weth_contract, eth_count, private_key)
            check_hash(web3, unwrap_tx_hash)
            time.sleep(5)
        except Exception as e:
            logger.error(f"Error UNWRAP WETH in ETH: {str(e)}")
            perform_wrap_unwrap_cycles(private_key, proxy, rpc_url, start_cycle=i)
            return
