#!/usr/bin/env python3
"""Port knocking client implementation in Python."""

import argparse
import socket
import time

DEFAULT_KNOCK_SEQUENCE = [1234, 5678, 9012]
DEFAULT_PROTECTED_PORT = 2222
DEFAULT_DELAY = 0.3  # seconds between knocks


def send_knock(target: str, port: int, delay: float):
    """Send a single TCP knock to the target port."""
    try:
        print(f"[*] Knocking port {port} on {target}...")
        with socket.create_connection((target, port), timeout=1.0):
            # Connection likely refused — we only need the SYN packet
            pass
    except (ConnectionRefusedError, TimeoutError):
        # Expected behavior: port is closed
        pass
    except OSError as e:
        print(f"[!] Error knocking port {port}: {e}")
    time.sleep(delay)


def perform_knock_sequence(target: str, sequence: list[int], delay: float):
    """Send the full knock sequence in order."""
    print(f"[*] Performing knock sequence: {sequence}")
    for port in sequence:
        send_knock(target, port, delay)
    print("[*] Knock sequence complete.")


def check_protected_port(target: str, protected_port: int):
    """Try connecting to the protected port after knocking."""
    print(f"[*] Checking if protected port {protected_port} is open...")
    try:
        with socket.create_connection((target, protected_port), timeout=2.0):
            print(f"[+] Successfully connected to protected port {protected_port}!")
    except OSError:
        print(f"[-] Could not connect to protected port {protected_port}.")


def parse_args():
    parser = argparse.ArgumentParser(description="Port knocking client in Python")
    parser.add_argument("--target", required=True, help="Target host or IP")
    parser.add_argument(
        "--sequence",
        default=",".join(str(port) for port in DEFAULT_KNOCK_SEQUENCE),
        help="Comma-separated knock ports (default: 1234,5678,9012)",
    )
    parser.add_argument(
        "--protected-port",
        type=int,
        default=DEFAULT_PROTECTED_PORT,
        help=f"Protected service port (default: {DEFAULT_PROTECTED_PORT})",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=DEFAULT_DELAY,
        help=f"Delay between knocks in seconds (default: {DEFAULT_DELAY})",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Attempt connection to protected port after knocking",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        sequence = [int(port.strip()) for port in args.sequence.split(",")]
    except ValueError:
        raise SystemExit("Invalid sequence. Use comma-separated integers.")

    perform_knock_sequence(args.target, sequence, args.delay)

    if args.check:
        check_protected_port(args.target, args.protected_port)


if __name__ == "__main__":
    main()
