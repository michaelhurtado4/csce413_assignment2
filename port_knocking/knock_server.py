#!/usr/bin/env python3
"""
Python Port Knocking Server

- Listens on a sequence of TCP ports
- Tracks each client IP's progress through the sequence
- Opens protected port via iptables for 30 seconds on correct sequence
"""

import argparse
import logging
import socket
import threading
import time
import subprocess

DEFAULT_KNOCK_SEQUENCE = [1234, 5678, 9012]
DEFAULT_PROTECTED_PORT = 2222
DEFAULT_SEQUENCE_WINDOW = 10.0
DEFAULT_OPEN_DURATION = 30  # seconds to keep protected port open


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )


def open_protected_port(ip, protected_port):
    """Open the protected port for the given IP using iptables."""
    logging.info(f"[+] Opening protected port {protected_port} for {ip}")
    cmd = [
        "iptables",
        "-I",
        "INPUT",
        "-p",
        "tcp",
        "-s",
        ip,
        "--dport",
        str(protected_port),
        "-j",
        "ACCEPT",
    ]
    subprocess.run(cmd, check=False)


def close_protected_port(ip, protected_port):
    """Close the protected port for the given IP using iptables."""
    logging.info(f"[-] Closing protected port {protected_port} for {ip}")
    cmd = [
        "iptables",
        "-D",
        "INPUT",
        "-p",
        "tcp",
        "-s",
        ip,
        "--dport",
        str(protected_port),
        "-j",
        "ACCEPT",
    ]
    subprocess.run(cmd, check=False)


class KnockTracker:
    """Tracks client IPs and their progress through the knock sequence."""

    def __init__(self, sequence, window):
        self.sequence = sequence
        self.window = window
        self.clients = {}  # ip -> (current_index, last_knock_time)
        self.lock = threading.Lock()

    def register_knock(self, ip, port):
        with self.lock:
            now = time.time()
            idx, last_time = self.clients.get(ip, (0, None))

            # If too much time has passed since last knock, reset
            if last_time is not None and now - last_time > self.window:
                idx = 0

            # Check if this port is correct for current index
            if port == self.sequence[idx]:
                idx += 1
                self.clients[ip] = (idx, now)
                if idx == len(self.sequence):
                    # Full sequence completed
                    logging.info(f"[+] Correct sequence from {ip}")
                    self.clients[ip] = (0, None)  # reset
                    return True
            else:
                # Incorrect knock, reset
                self.clients[ip] = (0, None)
            return False


def knock_listener(port, tracker, protected_port):
    """Listen on a TCP port for knocks and update tracker."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", port))
    sock.listen(5)
    logging.info(f"[*] Listening for knocks on port {port}")

    while True:
        try:
            conn, addr = sock.accept()
            ip = addr[0]
            conn.close()  # We don't actually need to receive data
            if tracker.register_knock(ip, port):
                open_protected_port(ip, protected_port)
                # Close after DEFAULT_OPEN_DURATION seconds
                threading.Thread(
                    target=lambda ip=ip: (time.sleep(DEFAULT_OPEN_DURATION), close_protected_port(ip, protected_port)),
                    daemon=True,
                ).start()
        except Exception as e:
            logging.error(f"[!] Error on port {port}: {e}")


def listen_for_knocks(sequence, window_seconds, protected_port):
    logging.info(f"Listening for knock sequence: {sequence}")
    tracker = KnockTracker(sequence, window_seconds)

    # Start a listener thread for each knock port
    for port in sequence:
        t = threading.Thread(target=knock_listener, args=(port, tracker, protected_port), daemon=True)
        t.start()

    # Keep main thread alive
    while True:
        time.sleep(1)


def parse_args():
    parser = argparse.ArgumentParser(description="Python Port Knocking Server")
    parser.add_argument(
        "--sequence",
        default=",".join(str(port) for port in DEFAULT_KNOCK_SEQUENCE),
        help="Comma-separated knock ports",
    )
    parser.add_argument(
        "--protected-port",
        type=int,
        default=DEFAULT_PROTECTED_PORT,
        help="Protected service port",
    )
    parser.add_argument(
        "--window",
        type=float,
        default=DEFAULT_SEQUENCE_WINDOW,
        help="Seconds allowed to complete the sequence",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    setup_logging()

    try:
        sequence = [int(port) for port in args.sequence.split(",")]
    except ValueError:
        raise SystemExit("Invalid sequence. Use comma-separated integers.")

    listen_for_knocks(sequence, args.window, args.protected_port)


if __name__ == "__main__":
    main()
