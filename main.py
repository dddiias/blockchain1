import hashlib
import json
import time

def generate_key_pair():
    # Choose two large prime numbers
    p = 61
    q = 53

    # Calculate n and totient
    n = p * q
    totient = (p - 1) * (q - 1)

    # Choose public key e (usually a small prime, often 65537)
    e = 17

    # Calculate private key d
    d = pow(e, -1, totient)

    return ((e, n), (d, n))

def encrypt(message, public_key):
    e, n = public_key
    encrypted_message = [pow(ord(char), e, n) for char in message]
    return encrypted_message

def decrypt(encrypted_message, private_key):
    d, n = private_key
    decrypted_message = [chr(pow(char, d, n)) for char in encrypted_message]
    return ''.join(decrypted_message)

class Transaction:
    def __init__(self, sender, recipient, amount):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.timestamp = time.time()
        self.signature = None

    def sign(self, private_key):
        data = f"{self.sender}{self.recipient}{self.amount}{self.timestamp}"
        encrypted_data = encrypt(data, private_key)
        self.signature = encrypted_data

    def verify_signature(self, public_key):
        data = f"{self.sender}{self.recipient}{self.amount}{self.timestamp}"
        decrypted_data = decrypt(self.signature, public_key)
        return decrypted_data == data

    def to_dict(self):
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "timestamp": self.timestamp,
            "signature": self.signature
        }

class Block:
    def __init__(self, previous_hash):
        self.transactions = []
        self.previous_hash = previous_hash
        self.timestamp = time.time()
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        data = json.dumps([transaction.to_dict() for transaction in self.transactions]) + str(self.previous_hash) + str(self.timestamp)
        return hashlib.sha256(data.encode()).hexdigest()

    def add_transaction(self, transaction):
        transaction.sign(private_key)
        self.transactions.append(transaction)
        self.hash = self.calculate_hash()

class MerkleTree:
    def __init__(self, transactions):
        self.transactions = transactions
        self.root = self.build_tree()

    def build_tree(self):
        if not self.transactions:
            return None
        if len(self.transactions) == 1:
            return hashlib.sha256(str(self.transactions[0]).encode()).hexdigest()
        hashes = [hashlib.sha256(str(trans.to_dict()).encode()).hexdigest() for trans in self.transactions]
        while len(hashes) > 1:
            new_hashes = []
            for i in range(0, len(hashes), 2):
                concat_data = hashes[i] + (hashes[i + 1] if i + 1 < len(hashes) else '')
                new_hashes.append(hashlib.sha256(concat_data.encode()).hexdigest())
            hashes = new_hashes
        return hashes[0]

# Example usage
public_key, private_key = generate_key_pair()

# Create a blockchain with a genesis block
blockchain = [Block("0")]

# Example of adding a transaction
transaction = Transaction("Alice", "Bob", 10)
block = Block(blockchain[-1].hash)
block.add_transaction(transaction)
blockchain.append(block)

# Display blockchain information
for block in blockchain:
    print(f"Block Hash: {block.hash}")
    print(f"Previous Hash: {block.previous_hash}")
    print(f"Merkle Root: {MerkleTree(block.transactions).root}")
    print("Transactions:")
    for trans in block.transactions:
        print(f"Sender: {trans.sender}, Recipient: {trans.recipient}, Amount: {trans.amount}, Signature Verified: {trans.verify_signature(public_key)}")
    print(f"Timestamp: {block.timestamp}")
    print("="*30)
