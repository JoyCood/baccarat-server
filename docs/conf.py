room_size = 8
HOST = ''
PORT = 8888
HEADER_LENGTH = 8

HALLS = [
        {'id': 1, 'title': '练习房', 'min_coin':5, 'max_coin':50, 'banker_coin': 300, 'fee':
            0, 'tax': 5, 'chip_values': {10, 20, 50, 80, 100}},

        {'id': 2, 'title': '初级房', 'min_coin': 50, 'max_coin':200, 'banker_coin': 800,
            'fee': 0, 'tax': 5, 'chip_values': {200, 300, 500, 1000, 2000}}        
]

contract = {
    'transact_account': '0x14CD5c014C56cd8464f871b0955Aa3B23EB78B5a',
    'provider_url': 'http://localhost:8545',        
    'contract_address': '0xcd46ebf5c3cec2b062a809d39a834c5f01e30852',
    'abi_file': 'docs/abi.json'
} 


