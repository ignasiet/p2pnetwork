from datetime import datetime
import json

class Block():
    def __init__(self, previous=None, data=None, creator=None) -> None:
        if previous is None:
            self.id=0
            self.pointer = None
            self.previous = None
            self.len = 0
            self.owner = "Genesis"
            self.coin = 0
            self.destiny = None
        else:
            self.id=previous.getId() + 1
            self.pointer = previous.getId()
            self.previous = previous
            self.len = previous.len + 1
            self.owner = data['Name']
            self.coin = data['Coin']
            self.destiny = data['To']
        self.created = datetime.now()
        self.creator = creator

    def getHash(self):
        return hash(f'{self.owner}|{self.coin}')

        
    def load(self, block: dict) -> None:
        self.id=block['id']
        self.pointer = block['pointer']
        self.len = block['len']
        self.owner = block['owner']
        self.coin = block['coin']
        self.destiny = block['to']
        self.creator = block['creator']
        self.created = block['created']
        if block['previous'] is not None:
            new_block = Block()
            new_block.load(block['previous'])
            self.previous = new_block

    def getId(self):
        return self.id

    def getPrevious(self):
        return self.previous

    def diff(self, block):
        return self.len - block.len

    def __str__(self) -> str:
        return f'Block: {self.id}; by: {self.creator}'

    def toDict(self) -> dict:
        return {'id': self.id,
                'pointer': self.pointer,
                'previous': self.previous.toDict() if self.previous is not None else None,
                'len' : self.len,
                'owner': self.owner,
                'coin': self.coin,
                'to': self.destiny,
                'creator': self.creator,
                'created': self.created
                }
        
    