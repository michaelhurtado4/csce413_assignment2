#!/usr/bin/env python3
import socket
import select
import subprocess
import logging

# ========= CONFIG =========
HOST = "0.0.0.0"
KNOCK_SEQUENCE = [1234, 5678, 9012]
PROTECTED_PORT = 2222
# ==========================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

client_progress = {}
sockets = []


def run_iptables(cmd):
    subprocess.run(cmd, check=True)


def setup_firewall():
    logging.info("Resetting iptables and blocking protected port")

    # Flush rules
    run_iptables(["iptables", "-F"])
    run_iptables(["iptables", "-X"])

    # Default policies
    run_iptables(["iptables", "-P", "INPUT", "ACCEPT"])
    run_iptables(["iptables", "-P", "FORWARD", "ACCEPT"])
    run_iptables(["iptables", "-P", "OUTPUT", "ACCEPT"])

    # Block protected port
    run_iptables([
        "iptables", "-A", "INPUT",
        "-p", "tcp",
        "--dport", str(PROTECTED_PORT),
        "-j", "DROP"
    ])


def open_protected_port():
    logging.info(f"Opening protected port {PROTECTED_PORT}")

    # Remove DROP rule
    run_iptables([
        "iptables", "-D", "INPUT",
        "-p", "tcp",
        "--dport", str(PROTECTED_PORT),
        "-j", "DROP"
    ])

    # Add ACCEPT rule
    run_iptables([
        "iptables", "-I", "INPUT", "1",
        "-p", "tcp",
        "--dport", str(PROTECTED_PORT),
        "-j", "ACCEPT"
    ])


def main():
    setup_firewall()

    # Create listening sockets for knock ports
    for port in KNOCK_SEQUENCE:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, port))
        s.listen(5)
        sockets.append(s)
        logging.info(f"Listening on TCP port {port}")

    logging.info("Waiting for knock sequence...")

    while True:
        readable, _, _ = select.select(sockets, [], [])

        for s in readable:
            conn, addr = s.accept()
            client_ip = addr[0]
            port = s.getsockname()[1]
            conn.close()

            if client_ip not in client_progress:
                client_progress[client_ip] = 0

            expected_port = KNOCK_SEQUENCE[client_progress[client_ip]]

            if port == expected_port:
                client_progress[client_ip] += 1
                logging.info(f"{client_ip} knocked correct port {port}")

                if client_progress[client_ip] == len(KNOCK_SEQUENCE):
                    logging.info(f"{client_ip} COMPLETED knock sequence")
                    open_protected_port()
                    client_progress[client_ip] = 0
            else:
                logging.info(f"{client_ip} wrong knock ({port}), resetting")
                client_progress[client_ip] = 0


if __name__ == "__main__":
    main()
