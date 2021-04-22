import hashlib
import json
from urllib.parse import urlparse
import requests
import time
import sys
import threading

print(f"Arguments count: {len(sys.argv)}")


class Blockchain(object):
    # ctor
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        # create the genesis block
        self.new_block(previous_hash=1, proof=100)
        self.nodes = set()
        self.mining = False
        self.proactive = False
        self.faulty = False

    def new_block(self, proof, previous_hash=100):
        # create a new block and add it to the chain
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
        }
        # append the block and return it
        self.chain.append(block)
        self.current_transactions = []
        return block

    def register_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    @staticmethod
    def thread_forward_transaction(self, url, transaction):
        r = requests.post(url, json=transaction)

    def new_transaction(self, trans_id, sender, recipient, amount, send_remote=True):
        transaction = {
            'trans_id': trans_id,
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        }

        # filter out transactions in current_transactions that are also present in the blockchain
        filtered_list = list(filter(lambda stored_trans: stored_trans['trans_id'] == trans_id
                                    and stored_trans['sender'] == sender
                                    and stored_trans['sender'] != '0'
                                    and stored_trans['recipient'] == recipient
                                    and stored_trans['amount'] == amount, self.current_transactions))

        if len(filtered_list) == 0:
            self.current_transactions.append(transaction)
            if send_remote:
                for x in self.nodes:
                    url = f"http://{x}/transactions/new"
                    threading_function = threading.Thread(target=self.thread_forward_transaction,
                                                          args=(url, transaction))
                    threading_function.start()
            return self.last_block['index'] + 1
        else:
            print("RECEIVED A TRANSACTION WE ALREADY KNOW ABOUT")
            return self.last_block['index']

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        # dumps converts a python object to json
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            # check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False
            if not (self.valid_proof(last_block['proof'], block['proof'])):
                return False
            last_block = block
            current_index += 1
        return True

    def resolve_conflicts(self):
        neighbours = self.nodes
        new_chain = None

        # We want to find chains longer than the one we already have
        max_length = len(self.chain)

        # request the chains from the neighbors
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # check if length longer and if so check if chain valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain
        # Replace our chain with new longest chain if it exists
        if new_chain:
            # remove the transactions in the block from our current transactions
            all_transactions = []
            for item in chain:
                for trans in item['transactions']:
                    all_transactions.append(trans)
            values_to_keep = []
            for i in self.current_transactions:
                if i not in all_transactions:
                    if not values_to_keep:
                        values_to_keep = i
                    else:
                        values_to_keep.append(i)

            self.current_transactions = values_to_keep
            self.chain = new_chain
            return True
        return False
