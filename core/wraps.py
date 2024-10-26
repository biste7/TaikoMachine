import time

from eth_account import Account
from web3 import Web3

from constants import weth_abi
from utils import logger
from config import RPC_URL, contract, cycles, eth_count
import requests.exceptions

web3 = Web3(Web3.HTTPProvider(RPC_URL))

if not web3.is_connected():
    raise Exception("Connection lost Ethereum node ")

def get_address(private_key):
    wallet_address = Account.from_key(private_key).address
    return wallet_address

def get_nonce(wallet_address, private_key):
    try:
        nonce = web3.eth.get_transaction_count(wallet_address)
        return nonce
    except (requests.exceptions.Timeout, TimeoutError, requests.exceptions.ConnectionError):
        return get_nonce(wallet_address, private_key)
    except requests.exceptions.HTTPError as error:
        if '[429]' in str(error.response) or '[502]' in str(error.response):
            return get_nonce(wallet_address, private_key)

        raise error




weth_contract = web3.eth.contract(address=contract, abi=weth_abi)


def get_gas_price():
    gas_price = web3.eth.gas_price
    print(f"Gas price: {web3.from_wei(gas_price, 'gwei')} Gwei")
    return gas_price


def wrap_eth(amount_in_eth, private_key):
    transaction = weth_contract.functions.deposit().build_transaction({
        'from': get_address(private_key),
        'value': web3.to_wei(amount_in_eth, 'ether'),
        'nonce': web3.eth.get_transaction_count(get_address(private_key)),
        'gasPrice': int(web3.eth.gas_price * 1.01)

    })

    transaction.update({
        'gas': web3.eth.estimate_gas(transaction),
    })

    signed_txn = web3.eth.account.sign_transaction(transaction, private_key=private_key)

    tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
    logger.info(f"Send transaction ETH in WETH. Hash: {web3.to_hex(tx_hash)}")
    return tx_hash


def unwrap_weth(amount_in_weth, private_key):

    transaction = weth_contract.functions.withdraw(
        web3.to_wei(amount_in_weth, 'ether')
    ).build_transaction({
        'from': get_address(private_key),
        'nonce': web3.eth.get_transaction_count(get_address(private_key)),
        'gasPrice': int(web3.eth.gas_price * 1.01)
    })

    gas_estimate = web3.eth.estimate_gas(transaction)

    transaction.update({
        'gas': gas_estimate,
    })

    signed_txn = web3.eth.account.sign_transaction(transaction, private_key=private_key)

    tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
    logger.info(f"Send transaction WETH in ETH. Hash: {web3.to_hex(tx_hash)}")
    return tx_hash


def check_hash(hashes):
    try:
        web3.eth.wait_for_transaction_receipt(hashes)
        logger.success(f"Transaction complete {web3.to_hex(hashes)}")
    except Exception as e:
        logger.info(f"Transaction pending {str(e)}")
        check_hash(hashes)

def perform_wrap_unwrap_cycles(private_key):

    for i in range(cycles):
        logger.info(f"Cycle {i + 1} of {cycles}:")


        try:
            logger.info(f"WRAP {eth_count} ETH in WETH...")
            wrap_tx_hash = wrap_eth(eth_count, private_key)

            check_hash(wrap_tx_hash)
            time.sleep(5)
        except Exception as e:
            logger.error(f"Error WRAP ETH in WETH: {str(e)}")
            perform_wrap_unwrap_cycles(private_key)
            #break


        try:
            logger.info(f"UNWRAP {eth_count} WETH in ETH...")
            unwrap_tx_hash = unwrap_weth(eth_count, private_key)

            check_hash(unwrap_tx_hash)
            time.sleep(5)
        except Exception as e:
            logger.error(f"Error UNWRAP WETH in ETH: {str(e)}")
            perform_wrap_unwrap_cycles(private_key)
            #break
