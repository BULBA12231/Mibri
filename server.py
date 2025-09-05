import argparse
import asyncio
import json
from typing import Dict, Any, List

# In-memory store; for demo only. Replace with DB in production.
USERS: Dict[str, Dict[str, Any]] = {}
# USERS[username] = {
#   "pubkey": str(Base64),
#   "queue": List[encrypted_messages]
# }


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    addr = writer.get_extra_info('peername')
    while True:
        line = await reader.readline()
        if not line:
            break
        try:
            msg = json.loads(line.decode().strip())
            cmd = msg.get("cmd")
            if cmd == "register":
                username = msg["username"]
                pubkey = msg["public_key"]
                if username in USERS:
                    USERS[username]["pubkey"] = pubkey
                else:
                    USERS[username] = {"pubkey": pubkey, "queue": []}
                await send_json(writer, {"ok": True})
            elif cmd == "get_pubkey":
                recipient = msg["username"]
                pub = USERS.get(recipient, {}).get("pubkey")
                await send_json(writer, {"ok": bool(pub), "public_key": pub})
            elif cmd == "send":
                recipient = msg["to"]
                sender = msg["from"]
                ciphertext = msg["ciphertext"]
                sender_pub = msg["sender_public_key"]
                if recipient not in USERS:
                    await send_json(writer, {"ok": False, "error": "recipient_not_found"})
                    continue
                USERS[recipient]["queue"].append({
                    "from": sender,
                    "sender_public_key": sender_pub,
                    "ciphertext": ciphertext,
                })
                await send_json(writer, {"ok": True})
            elif cmd == "inbox":
                username = msg["username"]
                items: List[Dict[str, Any]] = USERS.get(username, {}).get("queue", [])
                USERS.get(username, {}).update({"queue": []})
                await send_json(writer, {"ok": True, "messages": items})
            elif cmd == "ping":
                await send_json(writer, {"ok": True, "pong": True})
            else:
                await send_json(writer, {"ok": False, "error": "unknown_cmd"})
        except Exception as e:
            await send_json(writer, {"ok": False, "error": str(e)})
    writer.close()
    await writer.wait_closed()


async def send_json(writer: asyncio.StreamWriter, obj: Dict[str, Any]):
    data = (json.dumps(obj) + "\n").encode()
    writer.write(data)
    await writer.drain()


async def main():
    parser = argparse.ArgumentParser(description="Mibiri relay server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5555)
    args = parser.parse_args()

    server = await asyncio.start_server(handle_client, args.host, args.port)
    addr = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    print(f"Server listening on {addr}")
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
