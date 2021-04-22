from uuid import uuid4
from flask import jsonify, Flask, request
import requests
import time
import sys
import threading
import blockchain
import random

print(f"Arguments count: {len(sys.argv)}")

# instantiate our node
app = Flask(__name__)

# generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-','')

# instantiate the blockchain
blockchain = blockchain.Blockchain()


def thread_proactive(url):
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    r = requests.post(url, json=response)


def proactive_consensus():
    print("Proactive Consensus Being Called")
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    # for each neighbor node, notify them of our chain
    for x in blockchain.nodes:
        url = f"http://{x}/receive_proactive_chain"
        threading_function = threading.Thread(target=thread_proactive, args=(url,))
        threading_function.start()


def thread_mine(current_index):
    # sleep for a random number of seconds from 10 to 60 seconds to simulate mining
    time.sleep(random.randint(10, 60))

    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # if faulty, edit the hash to be incorrect
    if blockchain.faulty:
        proof = 0

    previous_hash = blockchain.hash(last_block)
    # if the blockchain is still the same length as when we started, add the new block
    if len(blockchain.chain) == current_index:

        # reward miner
        blockchain.new_transaction(1, "0", node_identifier, 1, False, )

        blockchain.new_block(proof, previous_hash)
        # if we are proactively telling other nodes of the new chain
        if blockchain.proactive:
            proactive_consensus()

    blockchain.mining = False


@app.route('/mine', methods=['GET'])
def mine():
    # if not already mining, create a thread that starts mining
    if not blockchain.mining:
        blockchain.mining = True
        current_index = len(blockchain.chain)
        x = threading.Thread(target=thread_mine, args =(current_index,))
        x.start()
        return jsonify({'message': "MINING STARTED"}), 200
    else:
        return jsonify({'message': "ALREADY MINING"}), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    # check required fields are in the received data
    required = ['trans_id', 'sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # create the transaction
    index = blockchain.new_transaction(values['trans_id'], values['sender'], values['recipient'], values['amount'])

    # return message saying transaction added to pool
    response = {'message': f'Transaction will be added'}
    return jsonify(response), 201


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@app.route('/shutdown', methods=['GET'])
def shutdown():
    shutdown_server()
    return jsonify({'result': "successfully terminated"}), 200


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/peers', methods=['GET'])
def show_peers():
    return jsonify({'peers': list(blockchain.nodes)}), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json(force = True)
    print(values)
    nodes = values.get('nodes')
    if nodes is None:
        return "Error: please supply a valid list of nodes", 400
    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New Nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message':'Our chain is authoritative',
            'chain': blockchain.chain
        }
    return jsonify(response), 200


@app.route('/toggle_proactive_consensus', methods=['GET'])
def toggle_proactive():
    blockchain.proactive = not blockchain.proactive
    return jsonify({'proactive-value': blockchain.proactive}), 200


@app.route('/receive_proactive_chain', methods=['POST'])
def receive_proactive_chain():
    values = request.get_json(force=True)
    print(values)
    length = values.get('length')
    chain = values.get('chain')
    chain_copy = values.get('chain')

    # check if length longer and if so check if chain valid
    if length > len(blockchain.chain) and blockchain.valid_chain(chain):
        print_replaced_chain()

        # remove the transactions in the chain from our current transactions
        all_transactions = []
        for item in chain_copy:
            for trans in item['transactions']:
                all_transactions.append(trans)

        blockchain.chain = chain
    elif not(blockchain.valid_chain(chain)):
        print("BAD CHAIN RECEIVED")

    return jsonify({'status': 'success'}), 200


@app.route('/toggle_faulty', methods=['GET'])
def toggle_faulty():
    blockchain.faulty = not blockchain.faulty
    return jsonify({'faulty-value': blockchain.faulty}), 200


@app.route('/valid_chain', methods=['GET'])
def valid_chain_query():
    return_val = blockchain.valid_chain(blockchain.chain)
    return jsonify({'valid-chain': return_val}), 200


@app.route('/seeTransactions', methods=['GET'])
def see_transactions():
    return_val = blockchain.current_transactions
    response = {
            'transactions': return_val
        }
    return jsonify(response), 200


# open our log file
if len(sys.argv) > 1:
    f = open(f"127.0.0.1:{sys.argv[1]}.txt", "w")
else:
    f = open(f"127.0.0.1:5001.txt", "w")


def print_replaced_chain():
    f.write("Chain Replaced\n")
    for index in blockchain.chain:
        val = index.get("index")
        hash_val = index.get("previous_hash")
        proof = index.get("proof")
        f.write(f"\tindex: {val}  hash: {hash_val}  proof: {proof}\n")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        app.run(host='0.0.0.0', port=sys.argv[1])
    else:
        # 5001 will be our default
        app.run(host='0.0.0.0', port=5001)