# Import dependencies
from constants import *
import os
from dotenv import load_dotenv
import subprocess
import json
from eth_account import Account
from bit import PrivateKeyTestnet
from web3 import Web3
from web3.middleware import geth_poa_middleware
from bit.network import NetworkAPI

load_dotenv()

# Fallback mnemonic environment variable
mnemonic = os.getenv("MNEMONIC")

def derive_wallets(mnemonic, coin, numderive):
    command = f"./hd-wallet-derive/hd-wallet-derive.php -g --mnemonic='{mnemonic}' --coin='{coin}'  --numderive='{numderive}' --cols=path,address,privkey,pubkey --format=json"

    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    p_status = p.wait()
    keys = json.loads(output)

    return print(keys)

def coins():

    coin_dict = {
        'btc-test' : derive_wallets(mnemonic, BTCTEST, 3),
        'eth' : derive_wallets(mnemonic, ETH, 3)
    }
    
    return coin_dict

def priv_key_to_account(coin, priv_key):
    
    if coin == ETH:
        
        return Account.privateKeyToAccount(priv_key)
    elif coin == BTCTEST:
        return PrivateKeyTestnet(priv_key)

def create_tx(coin, account, to, amount):
    if coin == ETH:
        gasEstimate = w3.eth.estimateGas({"from": account.address, "to": to, "value": w3.toWei(amount,'ether')})
        return {
            "from": account.address,
            "to": to,
            "value": w3.toWei(amount,'ether') ,
            "gas": gasEstimate,
            "gasPrice": w3.eth.gasPrice,
            "nonce": w3.eth.getTransactionCount(account.address)
            }
    elif coin == BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(to, amount, BTC)])

def send_tx(coin, account, to, amount):

    raw_tx = create_tx(coin, account, to, amount)
    signed_tx = account.sign_transaction(raw_tx)

    if coin == ETH:
        return w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    elif coin == BTCTEST:
        return NetworkAPI.broadcast_tx_testnet(signed_tx)
