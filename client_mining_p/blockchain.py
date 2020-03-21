import hashlib
import json
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Create the genesis block
        # We always have to have a started block
        self.new_block(previous_hash=1, proof=100) 

    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain

        A block should have:
        * Index
        * Timestamp
        * List of current transactions
        * The proof used to mine this block
        * The hash of the previous block

        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """

        block = {
            'index': len(self.chain) + 1,
            'proof': proof,
            'timestamp': time(),
            'transactions':self.current_transactions,
            'previous_hash': previous_hash,
        }

        # Reset the current list of transactions 
        # --> We can safely update the list of transactions since things have happened
        self.current_transactions = [] 

        # Append the block to the chain
        self.chain.append(block)
        # Return the new block
        return block

    def hash(self, block):
        """
        Creates a SHA-256 hash of a Block

        :param block": <dict> Block
        "return": <str>
        """

        # Use json.dumps to convert json into a string
        # Use hashlib.sha256 to create a hash
        # It requires a `bytes-like` object, which is what
        # .encode() does.
        # It converts the Python string into a byte string.
        # We must make sure that the Dictionary is Ordered,
        # or we'll have inconsistent hashes

        # TODO: Create the block_string
        #json.dumps will do the work of turning the block/JSON object into a string
        # NB: order in a dictionary is not guaranteed, so order of keys/values might be important
         
        block_string = json.dumps(block) 
        string_in_bytes = block_string.encode()

        # TODO: Hash this string using sha256
        hash_object = hashlib.sha256(string_in_bytes)

        # By itself, the sha256 function returns the hash in a raw string (a hash object)
        # that will likely include escaped characters.
        # This can be hard to read, but .hexdigest() converts the
        # hash to a string of hexadecimal characters, which is
        # easier to work with and understand

        # TODO: Return the hashed block string in hexadecimal format
        hash_string = hash_object.hexdigest()

        return hash_string

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def valid_proof(block_string, proof):
        """
        Validates the Proof:  Does hash(block_string, proof) contain 3
        leading zeroes?  Return true if the proof is valid
        :param block_string: <string> The stringified block to use to
        check in combination with `proof`
        :param proof: <int?> The value that when combined with the
        stringified previous block results in a hash that has the
        correct number of leading zeroes.
        :return: True if the resulting hash is a valid proof, False otherwise
        """
        guess = f'{block_string}{proof}'.encode() #we need to turn it into bytes
        guess_hash = hashlib.sha256(guess).hexdigest()

        
        # return True or False
        return guess_hash[:6] == '000000'


# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route('/mine', methods=['POST'])
def mine():

    # Handle non-JSON response
    try:
        values = request.get_json()
    except ValueError:
        response = {"message":"Non-JSON response"}
        return jsonify(response), 400


    # Check that what we have got back contains a proof and an ID
    required = ['proof', 'id']
    
    if not all(k in values for k in required):
        response = {'message': "Missing values"}
        return jsonify(response), 400

    #Let's grab that submitted proof
    submitted_proof = values['proof']

    # Determine if proof is valid
    last_block = blockchain.last_block
    last_block_string = json.dumps(last_block, sort_keys=True)

    if blockchain.valid_proof(last_block_string, submitted_proof):

        # Forge the new Block by adding it to the chain with the proof
        previous_hash = blockchain.hash(blockchain.last_block)
        new_block = blockchain.new_block(submitted_proof, previous_hash)

        response = {
            'message': "New Block Forged",
            'block': new_block
        }

        return jsonify(response), 200

    else:

        response = {
            'message': "Proof invalid or already submitted"
        }

        return jsonify(response), 200


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        # TODO: Return the chain and its current length
        'chain':blockchain.chain,
        'chain_length':len(blockchain.chain)
    }
    return jsonify(response), 200

@app.route('/last_block', methods=['GET'])
def get_last_block():
    response = {
        'last_block': blockchain.last_block
    }
    return jsonify(response), 200


# Run the program on port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
