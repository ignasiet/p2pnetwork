import asyncio
from app.lib.server import Server

def main():
    server = Server()
    server.startServer()

if __name__ == "__main__":
    main()