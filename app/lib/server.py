from typing import List
from aiohttp import web, ClientSession
from asyncio import sleep, gather, ensure_future, get_event_loop, run, create_task
from datetime import datetime
from app.lib.block import Block
import os
import logging
from functools import cmp_to_key
import ast
import json

# logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

WEBSERVER_HOST = os.getenv('HOST', '0.0.0.0')
WEBSERVER_PORT = os.getenv('PORT', '8080')
SLEEP_TIME = int(os.getenv('SLEEP_TIME', 5))
DELAY_START = int(os.getenv('DELAY_START', 1))
KNOWN_HOSTS = ast.literal_eval(os.getenv('KNOWN_HOSTS', "['sv-server2']"))


class Server():
    def __init__(self) -> None:
        self.routes = web.RouteTableDef()
        self.app = web.Application()
        self.pool = []
        self.known_hosts = KNOWN_HOSTS
        self.block = self.createGenesisBlock()
        self.name = os.getenv('NAME', 'server1')
        self.setup_endpoints()


    def setup_endpoints(self):
        self.app.add_routes([web.get('/healthz', self.healthz)])
        self.app.add_routes([web.post('/create', self.receivepackage)])
        self.app.add_routes([web.get('/listpool', self.listPool)])
        self.app.add_routes([web.get('/listblocks', self.listBlocks)])
        self.app.add_routes([web.post('/receive', self.treatBlocks)])
        self.app.add_routes(self.routes)

    def name(self):
        return self.name

    def getPool(self):
        return [str(block) for block in self.pool]

    # @routes.get('/healthz')
    async def healthz(self, request):
        return web.Response(text='OK', status=200)

    def createblock(self, previousblock, data):
        block = Block(previous=previousblock, data=data, creator=self.name)
        self.pool.append(block)
        return block

    def createGenesisBlock(self):
        return Block(data="Genesis")

    def verifyIfBlockPresent(self, block)-> bool:
        presentBlocks = self.block
        bhash = block.getHash()
        while presentBlocks.id != 0:
            if bhash == presentBlocks.getHash():
                return True
            presentBlocks = presentBlocks.previous
        return False

    async def processPool(self):
        while True:
            await sleep(5)
            if self.pool:
                # logging.info("Awake")
                self.pool.sort(key=cmp_to_key(lambda x, y: x.diff(self.block) - y.diff(self.block)), reverse=True)
                self.block = self.pool.pop(0)
                self.pool = []
                # logginginfo(f'Selected current block: {str(self.block)}')
                await self.propagateblock(self.block)
            # else:
            #     logging.info('Pass')

    async def propagateblock(self, block):
        try:
            logging.info(f'Selected current block: {str(block.toDict())}')
            async with ClientSession() as session:
                data = json.dumps(block.toDict(), default=str)
                logging.info(data)
                for host in self.known_hosts:
                    url_host = f'http://{host}/receive'
                    async with session.post(url_host, json=data) as resp:
                        logging.info(f'Sending block to host: {host}: response: {resp.status}')
        except Exception as e:
            logging.info(f'Exception while sending block to host: {host}: error: {e}')

    def untieBlocks(self, block1, block2) -> int:
        long1 = block1.diff(self.block)
        long2 = block2.diff(self.block)
        return long1 - long2

    async def treatBlocks(self, request):
        try:
            data = await request.json()
            data = json.loads(data)
            logging.info(f'Received block {data}; parsing it. Type: {type(data)}')       
            block = Block()
            block.load(data)
            if not self.verifyIfBlockPresent(block) and self.verifyValidTransaction(block):
                self.pool.append(block)
            return web.Response(text=f'Received package and blocks created', status=200)
        except Exception as e:
            logging.info(f'Error processing block {block}: {e}, {e.__traceback__}')
            return web.Response(text=f'An error occured during the block processing', status=500)

    async def receivepackage(self, request):
        data = await request.json()
        if 'Coin' not in data or 'Name' not in data or 'To' not in data:
            return web.Response(text=f'Incomplete or malformed request', status=500)
        block = self.createblock(self.block, data)
        logging.info(f'Received block {block}')
        return web.Response(text=f'Added block to the pool', status=200)

    async def listPool(self, request):
        return web.json_response({'Blocks': self.getPool()})

    async def listBlocks(self, request) -> List:
        l = []
        block = self.block
        l.append(str(block))
        while block.id != 0:
            block = block.getPrevious()
            l.append(str(block))
        return web.json_response({'Blocks': l})

    async def paralel_block_task(self, _app):
        task = create_task(self.processPool())
        yield
        task.cancel()
    
    def startServer(self):
        self.app.cleanup_ctx.append(self.paralel_block_task)
        web.run_app(self.app)

    async def start(self):
        logging.info(
            f"Starting server on {WEBSERVER_HOST} pn port {WEBSERVER_PORT}..")
        await sleep(DELAY_START)
        logging.info(
            f"Started server on {WEBSERVER_HOST} pn port {WEBSERVER_PORT}..")
        await gather(self.app,
                     self.processPool)

