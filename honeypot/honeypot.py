#!/usr/bin/env python3
"""
SSH Honeypot with banner and fake shell responses
"""

import os
import socket
import threading
import logging
import paramiko

# Configuration
LISTEN_PORT = 22
SSH_BANNER = "SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5"
LOG_PATH = "/logs/honeypot.log"
HOST_KEY_PATH = "/logs/server_rsa.key"


def setup_logging():
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler()],
    )


def generate_host_key():
    if not os.path.exists(HOST_KEY_PATH):
        key = paramiko.RSAKey.generate(2048)
        key.write_private_key_file(HOST_KEY_PATH)
    return paramiko.RSAKey(filename=HOST_KEY_PATH)


class HoneypotServer(paramiko.ServerInterface):
    def __init__(self, logger):
        self.logger = logger
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        self.logger.info(f"LOGIN ATTEMPT | user={username} password={password}")
        return paramiko.AUTH_SUCCESSFUL

    def get_banner(self):
        return SSH_BANNER, "en-US"

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True


def handle_command(command):
    cmd = command.lower().strip()

    if cmd.startswith("ls"):
        return "bin  boot  dev  etc  home  lib  lib64  root  usr  var"
    elif cmd.startswith("cd"):
        return ""
    elif cmd == "pwd":
        return "/root"
    elif cmd == "whoami":
        return "root"
    elif cmd == "uname -a":
        return "Linux ubuntu 5.15.0-91-generic x86_64 GNU/Linux"
    elif cmd.startswith("cat /etc/passwd"):
        return (
            "root:x:0:0:root:/root:/bin/bash\n"
            "daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin"
        )
    else:
        return f"bash: {command}: command not found"


def fake_shell(channel, addr, logger):
    """Simulate a fake shell session over SSH"""
    channel.send(
        "Welcome to Ubuntu 20.04.6 LTS (GNU/Linux 5.15.0-91-generic x86_64)\r\n"
        "\r\n"
        " * Documentation:  https://help.ubuntu.com\r\n"
        " * Management:     https://landscape.canonical.com\r\n"
        f"\r\nLast login: Tue Feb  6 13:37:00 2026 from {addr[0]}\r\n"
    )

    prompt = "root@ubuntu:~# "

    while True:
        try:
            channel.send(prompt)
            data = channel.recv(1024)
            if not data:
                break

            command = data.decode("utf-8", errors="ignore").strip()
            logger.info(f"COMMAND | {addr[0]} | {command}")

            if command in ("exit", "logout"):
                channel.send("logout\r\n")
                channel.close()
                break

            response = handle_command(command)
            channel.send(response + "\r\n")

        except Exception as e:
            logger.error(f"Fake shell error for {addr}: {e}")
            break


def handle_client(client, addr, host_key, logger):
    try:
        transport = paramiko.Transport(client)
        transport.local_version = SSH_BANNER
        transport.add_server_key(host_key)

        server = HoneypotServer(logger)
        transport.start_server(server=server)

        channel = transport.accept(20)
        if channel is None:
            return

        server.event.wait(10)
        fake_shell(channel, addr, logger)

    except Exception as e:
        logger.error(f"Client error {addr}: {e}")
    finally:
        try:
            transport.close()
        except Exception:
            pass


def run_honeypot():
    logger = logging.getLogger("Honeypot")
    host_key = generate_host_key()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", LISTEN_PORT))
    sock.listen(100)

    logger.info(f"SSH Honeypot listening on port {LISTEN_PORT}")

    while True:
        client, addr = sock.accept()
        logger.info(f"Connection from {addr}")
        threading.Thread(
            target=handle_client,
            args=(client, addr, host_key, logger),
            daemon=True,
        ).start()


if __name__ == "__main__":
    setup_logging()
    run_honeypot()
