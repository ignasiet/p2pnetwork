from aiohttp import web
from app.lib.server import Server



async def test_hello(aiohttp_client, loop):
    s = Server()
    app = web.Application()
    app.router.add_get('/', s.healthz)
    client = await aiohttp_client(app)
    resp = await client.get('/')
    assert resp.status == 200
    text = await resp.text()
    assert 'OK' in text
    
async def test_receiving(aiohttp_client, loop):
    s = Server()
    app = web.Application()
    app.router.add_post('/receive', s.treatBlocks)
    client = await aiohttp_client(app)
    resp = await client.post('/receive', data='{"id": 1, "pointer": 0, "previous": {"id": 0, "pointer": null, "previous": null, "len": 0, "owner": "Genesis", "coin": 0, "to": null, "creator": null, "created": "2022-05-06 14:14:12.326472"}, "len": 1, "owner": "User1", "coin": 1, "to": "User2", "creator": "server1", "created": "2022-05-06 14:14:46.253623"}')
    assert resp.status == 200
    text = await resp.text()
    assert 'Received package and blocks created' in text
