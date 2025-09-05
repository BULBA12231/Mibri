import argparse
import asyncio
import json
from typing import Dict, Any, Tuple
from colorama import Fore, Style
from nacl.encoding import Base64Encoder

from crypto_utils import generate_keypair, save_profile, load_profile, encrypt_message, decrypt_message


def parse_hostport(s: str) -> Tuple[str, int]:
    if ":" not in s:
        raise ValueError("server must be host:port")
    h, p = s.rsplit(":", 1)
    return h, int(p)


async def tcp_request(host: str, port: int, payload: Dict[str, Any]) -> Dict[str, Any]:
    reader, writer = await asyncio.open_connection(host, port)
    writer.write((json.dumps(payload) + "\n").encode())
    await writer.drain()
    line = await reader.readline()
    writer.close()
    await writer.wait_closed()
    return json.loads(line.decode())


def cmd_keygen(args):
    priv, pub = generate_keypair()
    path = save_profile(args.username, priv, pub)
    print(f"Saved keys for {args.username} at {path}")


def cmd_register(args):
    host, port = parse_hostport(args.server)
    _, pub = load_profile(args.username)
    pub_b64 = Base64Encoder.encode(pub).decode()
    resp = asyncio.run(tcp_request(host, port, {"cmd": "register", "username": args.username, "public_key": pub_b64}))
    print(resp)


def cmd_send(args):
    host, port = parse_hostport(args.server)
    sender_priv, sender_pub = load_profile(args.from_user)
    resp = asyncio.run(tcp_request(host, port, {"cmd": "get_pubkey", "username": args.to}))
    if not resp.get("ok") or not resp.get("public_key"):
        print("Recipient not found or has no key")
        return
    recipient_pub = Base64Encoder.decode(resp["public_key"].encode())
    cipher = encrypt_message(sender_priv, recipient_pub, args.message)
    sender_pub_b64 = Base64Encoder.encode(sender_pub).decode()
    resp2 = asyncio.run(tcp_request(host, port, {
        "cmd": "send",
        "from": args.from_user,
        "to": args.to,
        "ciphertext": cipher,
        "sender_public_key": sender_pub_b64,
    }))
    print(resp2)


def cmd_inbox(args):
    host, port = parse_hostport(args.server)
    recipient_priv, _ = load_profile(args.username)
    resp = asyncio.run(tcp_request(host, port, {"cmd": "inbox", "username": args.username}))
    for item in resp.get("messages", []):
        try:
            sender_pub = Base64Encoder.decode(item["sender_public_key"].encode())
            plaintext = decrypt_message(recipient_priv, sender_pub, item["ciphertext"])
            print(f"{Fore.CYAN}{item['from']}{Style.RESET_ALL}: {plaintext}")
        except Exception as e:
            print(f"{Fore.RED}Failed to decrypt from {item.get('from')}: {e}{Style.RESET_ALL}")


def cmd_listen(args):
    host, port = parse_hostport(args.server)
    recipient_priv, _ = load_profile(args.username)
    print("Listening for new messages. Press Ctrl+C to stop.")

    async def loop():
        while True:
            resp = await tcp_request(host, port, {"cmd": "inbox", "username": args.username})
            for item in resp.get("messages", []):
                try:
                    sender_pub = Base64Encoder.decode(item["sender_public_key"].encode())
                    plaintext = decrypt_message(recipient_priv, sender_pub, item["ciphertext"])
                    print(f"{Fore.CYAN}{item['from']}{Style.RESET_ALL}: {plaintext}")
                except Exception as e:
                    print(f"{Fore.RED}Failed to decrypt from {item.get('from')}: {e}{Style.RESET_ALL}")
            await asyncio.sleep(args.interval)

    asyncio.run(loop())


def main():
    parser = argparse.ArgumentParser(description="Mibiri CLI client")
    sub = parser.add_subparsers(dest="cmd")

    p1 = sub.add_parser("keygen")
    p1.add_argument("--username", required=True)
    p1.set_defaults(func=cmd_keygen)

    p2 = sub.add_parser("register")
    p2.add_argument("--server", required=True)
    p2.add_argument("--username", required=True)
    p2.set_defaults(func=cmd_register)

    p3 = sub.add_parser("send")
    p3.add_argument("--server", required=True)
    p3.add_argument("--from", dest="from_user", required=True)
    p3.add_argument("--to", required=True)
    p3.add_argument("--message", required=True)
    p3.set_defaults(func=cmd_send)

    p4 = sub.add_parser("inbox")
    p4.add_argument("--server", required=True)
    p4.add_argument("--username", required=True)
    p4.set_defaults(func=cmd_inbox)

    p5 = sub.add_parser("listen")
    p5.add_argument("--server", required=True)
    p5.add_argument("--username", required=True)
    p5.add_argument("--interval", type=int, default=2)
    p5.set_defaults(func=cmd_listen)

    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()
