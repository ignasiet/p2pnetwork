# Simulator of a P2P network to test algorithms

Create a port-forward and send the following curl commands to test:

1. To create a block in a node: curl http://localhost:8080/create --data '{"Name": "User1", "Coin": 1, "To": "User2"}'

2. To update the blockchain in a node: curl -X POST http://localhost:8080/receive --data '{"id": 1, "pointer": 0, "previous": {"id": 0, "pointer": null, "previous": null, "len": 0, "owner": "Genesis", "coin": 0, "to": null, "creator": null, "created": "2022-05-06 14:14:12.326472"}, "len": 1, "owner": "User1", "coin": 1, "to": "User2", "creator": "server1", "created": "2022-05-06 14:14:46.253623"}'

3. TO list the blockchain present in a node: curl http://localhost:8080/listblocks