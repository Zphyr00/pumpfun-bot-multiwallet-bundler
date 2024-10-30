import requests
import time
import os
from config import BUY_AMOUNT, RPC, PRIV_KEY
from pump_fun import buy_spamtx, sell_spamtx
import time
from colored import Fore, Back, Style
import random
from solders.keypair import Keypair
from solana.rpc.api import Client
from spl.token.instructions import create_associated_token_account, get_associated_token_address
from solana.rpc.types import TokenAccountOpts
from spl.token.client import Token
from solders.pubkey import Pubkey #type: ignore
import threading



bought_tokens = []
client = Client(RPC)

def get_new_tokens():
    endpoint_new_tokens = "https://client-api-2-74b1891ee9f9.herokuapp.com/coins?offset=0&limit=20&sort=created_timestamp&order=DESC&includeNsfw=true"
    endpoint_trades = "https://client-api-2-74b1891ee9f9.herokuapp.com/trades/%mint%?limit=20&offset=0"
    
    r = requests.get(url=endpoint_new_tokens)
    data = r.json()
    
    for coin in data:
        timestamp = coin["created_timestamp"]
        new_token = coin["mint"]
        website = coin["website"]
        telegram = coin["telegram"]
        twitter = coin["twitter"]

        curr_timestamp = round(time.time() * 1000)
        if curr_timestamp - timestamp <= 8 * 1000 and telegram != None:
            return new_token
    
    return ""


def shouldSell(token_address):
    endpoint_trades = f"https://client-api-2-74b1891ee9f9.herokuapp.com/trades/{token_address}?limit=2&offset=0"
    trades_info = requests.get(endpoint_trades).json()
    for trade in trades_info:
        if trade["is_buy"] == False:
            return True
    return False

#####

#####

def find_data(data, field):
    if isinstance(data, dict):
        if field in data:
            return data[field]
        else:
            for value in data.values():
                result = find_data(value, field)
                if result is not None:
                    return result
    elif isinstance(data, list):
        for item in data:
            result = find_data(item, field)
            if result is not None:
                return result
    return None


def get_token_balance(base_mint: str, pub_key):
    try:

        headers = {"accept": "application/json", "content-type": "application/json"}

        payload = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "getTokenAccountsByOwner",
            "params": [
                str(pub_key),
                {"mint": str(base_mint)},
                {"encoding": "jsonParsed"},
            ],
        }
        
        response = requests.post(RPC, json=payload, headers=headers)
        ui_amount = find_data(response.json(), "uiAmount")
        return float(ui_amount)
    except Exception as e:
        return None
    

def withdrawTokens_thread(token, dest_address, pub_address, payer_keypair):
    try:
        account_data = client.get_token_accounts_by_owner(pub_address, TokenAccountOpts(token))
        source_token_account = account_data.value[0].pubkey
        source_token_account_instructions = None
    except:
        source_token_account = get_associated_token_address(pub_address, token)
        source_token_account_instructions = create_associated_token_account(pub_address, pub_address, token)
    
    try:
        account_data = client.get_token_accounts_by_owner(dest_address, TokenAccountOpts(token))
        dest_token_account = account_data.value[0].pubkey
        dest_token_account_instructions = None
    except:
        dest_token_account = get_associated_token_address(dest_address, token)
        dest_token_account_instructions = create_associated_token_account(pub_address, dest_address, token)
    
    transaction_finalized = False
    while transaction_finalized == False:
        token_balance = get_token_balance(token, pub_address)  
        if token_balance != None and token_balance >= 0.001:
            try:
                spl_client = Token(conn=client, pubkey=token, program_id=Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), payer=payer_keypair)
                transaction = spl_client.transfer(source=source_token_account, dest=dest_token_account, owner=payer_keypair, amount=int(float(token_balance)*1000000), multi_signers=None, opts=None, recent_blockhash=None)
                tx_sign = transaction.value
                time.sleep(20)
                tx_status = client.get_signature_statuses([tx_sign]).value[0].confirmation_status
                if "finalized" in str(tx_status).lower():
                    transaction_finalized = True
                    print(f"{Fore.green}[!] Succesfully sent " + str(token_balance) +" from " + str(pub_address))
                    return
                else:
                    print(f"{Fore.yellow}[x] Transfer failed " + str(token_balance) +" from " + str(pub_address))
            except Exception as e:
                pass
        else:
            return
        
    else:
        return

def withdrawTokens(token, dest_address):
    pks = []
    with open("data/pks.txt", "r", encoding="utf-8") as f:
        read_pks = f.read().split("\n")
    for pk in read_pks:
        pk = pk.replace("\n", "").replace(" ", "").replace("\r", "").strip()
        if len(pk) > 5:
            pks.append(pk)

    os.system("cls")
    print(f"\t{Fore.white}{Back.magenta} --- Withdraw Tokens ---\n")
    print(f"{Style.reset}", end="")
    threads = []
    for pk in pks:
        payer_keypair = Keypair.from_base58_string(pk)
        pub_address = payer_keypair.pubkey()
        t = threading.Thread(target=withdrawTokens_thread, args=(token, dest_address, pub_address, payer_keypair))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
    
    print(f"{Style.reset}\nAll tokens have been transfered.\nPress [ENTER] to return")
    input()



def printBalance():
    pks = []
    with open("data/pks.txt", "r", encoding="utf-8") as f:
        read_pks = f.read().split("\n")
    for pk in read_pks:
        pk = pk.replace("\n", "").replace(" ", "").replace("\r", "").strip()
        if len(pk) > 5:
            pks.append(pk)

    total_balance = 0.0
    os.system("cls")
    print(f"\t{Fore.white}{Back.green} --- SOL Balance ---\n")
    print(f"{Style.reset}", end="")
    for pk in pks:
        payer_keypair = Keypair.from_base58_string(pk)
        pub_address = payer_keypair.pubkey()
        balance = client.get_balance(pub_address).value / 1000000000
        print(str(pub_address) + "\t" + str(balance) + " SOL")
        total_balance += balance
    
    print("\nTotal Balance: " + str(total_balance) + " SOL\nPress [ENTER] to return")
    input()



def spamTxBuy(token):
    BUMP = True

    pks = []
    with open("data/pks.txt", "r", encoding="utf-8") as f:
        read_pks = f.read().split("\n")
    for pk in read_pks:
        pk = pk.replace("\n", "").replace(" ", "").replace("\r", "").strip()
        if len(pk) > 5:
            pks.append(pk)

    os.system("cls")
    print(f"\t{Fore.white}{Back.green} --- TX Spammer ---\n")
    print(f"{Style.reset}", end="")

    while len(pks) >= 1:
        wallet_pk = random.choice(pks)
        payer_keypair = Keypair.from_base58_string(wallet_pk)
        balance = client.get_balance(payer_keypair.pubkey()).value / 1000000000
        
        if BUMP == True:
            buy_amount = random.uniform(0.011, 0.018)
        elif balance > 1.1:
            buy_amount = 1.0
        elif balance >= 0.02:
            buy_amount = random.uniform(0.0101, 0.02)
        else:
            buy_amount = balance - 0.005
            pks.remove(wallet_pk)
        
        t = threading.Thread(target=buy_spamtx, args=(payer_keypair, token, buy_amount, 20))
        t.start()
        time.sleep(random.uniform(1, 2))

    print("\nDone! Press [ENTER] to return")
    input()

def spamTxSell(token):
    pks = []
    with open("data/pks.txt", "r", encoding="utf-8") as f:
        read_pks = f.read().split("\n")
    for pk in read_pks:
        pk = pk.replace("\n", "").replace(" ", "").replace("\r", "").strip()
        if len(pk) > 5:
            pks.append(pk)

    os.system("cls")
    print(f"\t{Fore.white}{Back.green} --- TX Spammer ---\n")
    print(f"{Style.reset}", end="")

    while len(pks) >= 1:
        wallet_pk = random.choice(pks)
        payer_keypair = Keypair.from_base58_string(wallet_pk)
        t = threading.Thread(target=sell_spamtx, args=(payer_keypair, token, 20))
        t.start()
        time.sleep(1)
        #time.sleep(random.uniform(0.5, 3.5))

    print("\nDone! Press [ENTER] to return")
    input()
    

def main():
    while True:
        os.system("cls")
        print(f"\t{Fore.white}{Back.cyan} --- Pump.Fun Tool ---\n")
        print(f"{Style.reset}0. Print Address & Balance")
        print(f"{Style.reset}1. Spam Buy TX")
        print(f"{Style.reset}2. Spam Sell TX")
        print(f"{Style.reset}3. Withdraw Tokens")
        print(f"{Style.reset}\nChoose: ", end="")
        choose = int(input().replace("\r", "").replace(" ", "").replace("\n", ""))

        if choose == 1 or choose == 2 or choose == 3:
            print(f"{Style.reset}Mint Address: ", end="")
            token = str(input().replace("\r", "").replace(" ", "").replace("\n", ""))

        if choose == 0:
            printBalance()
        elif choose == 1:
            spamTxBuy(token)
        elif choose == 2:
            spamTxSell(token)
        elif choose == 3:
            print(f"{Style.reset}[-] Destination Address: ", end="")
            dest_address = str(input().replace("\r", "").replace(" ", "").replace("\n", ""))
            withdrawTokens(Pubkey.from_string(token), Pubkey.from_string(dest_address))

if __name__ == "__main__":
    main()
    

