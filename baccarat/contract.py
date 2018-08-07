import os 
import json 
import time 
import threading

from web3 import (
    Web3, 
    HTTPProvider,
)
from web3.utils.events import( 
    get_event_data
)

from docs import (
    conf,
)

class Contract(threading.Thread):
    def __init__(self, room_id):
        self._room_id = room_id
        self._abi = self.get_abi()
        self._web3 = Web3(HTTPProvider(conf.contract_http_provider))
        self._address = self._web3.toChecksumAddress(conf.contrac['contract_address'])
        self._contract = self._web3.eth.contract(address=self._address, abi=self._abi)
        self._event_filter = self.create_filter()
        super().__init__(target=self.receive_event, args=(1))

    def get_abi(self):
        with open(conf.contract['abi_file'], 'r') as fd:
            contract_defination = json.load(fd)
        return contract_defination['abi']

    def get_receipt(self, txHash):
        return self._web3.eth.waitForTransactionReceipt(txHash)

    def handle_event(self, event):
         raise NotImplementedError('handle_event method must implement')

    def receive_event(self, poll_interval):
        while True:
            for event in self._event_filter.get_new_entries():
                self.handle_event(event)
            time.sleep(poll_interval)


class ContractDeal(Contract):
    
    def create_filter(self):
        return self._contract.events.Deal.createFilter(
                   fromBlock = 'latest',
                   argument_filters = {'room_id':self._room_id}
               )

    def handle_event(self, event):
        receipt = self.get_receipt(event['transactionHash'])
        receipt = self._contract.events.Deal().processReceipt(receipt)
        data = receipt[0]['args']

    def deal(self):
        txHash = self._contract.functions.deal(self._room_id).transact({
            'from': conf.contract['account'],
            'gas': conf.contract['gas']
        })
        receipt = self.get_receipt(txHash)
        if receipt['status'] == 0:
            return True
        return False

class ContractShuffle(Contract):

    def handle_event(self, event):
        receipt = self.get_receipt(event['transactionHash'])
        receipt = self._contract.events.Shuffle().processReceipt(receipt)
        data = receipt[0]['args']

    def shuffle(self, room_id):
        txHash = self._contract.functions.shuffle(room_id).transact({
            'from': account,
            'gas': gas
        })
        receipt = self.get_receipt(txHash)
        if receipt['status'] == 0:
            return True
        return False


