from solana.rpc.api import Client
from solders.keypair import Keypair

PUB_KEY = "6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt"
PRIV_KEY = "1111111111111111111111111111111PPm2a2NNZH2EFJ5UkEjkH9Fcxn8cvjTmZDKQQisyLDmA"
BUY_AMOUNT = 0.01
RPC = "https://greatest-sly-vineyard.solana-mainnet.quiknode.pro/542a1f30a7db18a8035b8dc689275d23432cc35f/"
client = Client(RPC)
payer_keypair = Keypair.from_base58_string(PRIV_KEY)
