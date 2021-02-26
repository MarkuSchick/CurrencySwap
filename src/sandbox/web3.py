"""
Test getting EURO/USD price from chainlink

from web3 import Web3


def load_metadata():
    _abi = '[{"inputs":[],"name":"decimals","outputs":[{"internalType"
    :"uint8","name":"","type":"uint8"}],"stateMutability":"view","type"
    :"function"},{"inputs":[],"name":"description","outputs":[{"internalType":
    "string","name":"","type":"string"}],"stateMutability":"view","type":"function"
    },{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":
    "getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},
    {"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256",
    "name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt",
    "type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],
    "stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs"
    :[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256",
    "name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":
    "uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType"
    :"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":
    "function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256",
    "name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
    return _abi


def connect2infura():
    infura_id = "0313885158454bc89fbc6e3d1092b185"
    _w3 = Web3(Web3.HTTPProvider(f"https://kovan.infura.io/v3/{infura_id}"))
    return _w3


def connect_contract(w3, address, _abi):
    return w3.eth.contract(address=addr, abi=_abi)


def get_lasted_EURO_price(_contract):
    return _contract.functions.latestRoundData().call()


if __name__ == "__main__":
    addr = "0x9326BFA02ADD2366b30bacB125260Af641031331"
    abi = load_metadata()
    w3 = connect2infura()
    contract = connect_contract(w3, addr, abi)
    latestData = get_lasted_EURO_price(contract)
    print(latestData)
"""
