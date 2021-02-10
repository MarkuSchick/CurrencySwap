"""Run a Schelling (1969, :cite:`Schelling69`) segregation
model and store a list with locations by type at each cycle.

The scripts expects that a model name is passed as an
argument. The model name must correspond to a file called
``[model_name].json`` in the "IN_MODEL_SPECS" directory.

"""
import json

import numpy as np
import pandas as pd
import web3
from web3 import Web3

from src.config import BLD
from src.config import SRC



depends_on = {
            "metadata": SRC / "model_specs" / "SwapContract.json",
            "transaction_data": SRC / "original_data" / "transactions.csv"
              }

def load_metadata():
    metadata = json.loads(depends_on["metadata"].read_text(encoding="utf-8"))
    abi = metadata['abi']
    bytecode = metadata['bytecode']
    return abi, bytecode

def connect2infura():
    infura_id = "0313885158454bc89fbc6e3d1092b185"
    w3 = Web3(Web3.HTTPProvider(f'https://kovan.infura.io/v3/{infura_id}'))
    return w3

def connect_contract():
    abi, bytecode = load_metadata()
    w3 = connect2infura()


def load_transactions():
    df = pd.read_csv(depends_on["transaction_data"])
    return df

if __name__ == "__main__":
    abi, bytecode = load_metadata()
    df = load_transactions()
    dfcontracts = df["ContractAddress"].dropna() 
    w3 = connect2infura()
    abi, bytecode = load_metadata()
    for address in dfcontracts:
        #myContract = w3.eth.contract(address=Web3.toChecksumAddress(address), abi=abi)
        bytecodeAddress = w3.eth.get_code(Web3.toChecksumAddress(address))        
        if bytecodeAddress.hex() == bytecode:
            print(address)


