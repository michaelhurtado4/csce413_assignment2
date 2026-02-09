#!/usr/bin/env python3
"""
Port Scanner - Starter Template for Students
Assignment 2: Network Security

This is a STARTER TEMPLATE to help you get started.
You should expand and improve upon this basic implementation.

TODO for students:
1. Implement multi-threading for faster scans
2. Add banner grabbing to detect services
3. Add support for CIDR notation (e.g., 192.168.1.0/24)
4. Add different scan types (SYN scan, UDP scan, etc.)
5. Add output formatting (JSON, CSV, etc.)
6. Implement timeout and error handling
7. Add progress indicators
8. Add service fingerprinting
"""

import socket
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed



def scan_port(target, port, timeout=1.0):
    """
    Scan a single port on the target host

    Args:
        target (str): IP address or hostname to scan
        port (int): Port number to scan
        timeout (float): Connection timeout in seconds

    Returns:
        bool: True if port is open, False otherwise
    """
    start_time = time.time()
    banner = None

    try:
        # TODO: Create a socket
        # TODO: Set timeout
        # TODO: Try to connect to target:port
        # TODO: Close the socket
        # TODO: Return True if connection successful
        # Create TCP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)

        # Attempt connection
        sock.connect((target, port))

        # Try to grab banner
        try:
            sock.sendall(b"\r\n")
            banner = sock.recv(1024).decode(errors="ignore").strip()
        except Exception:
            banner = None

        sock.close()
        elapsed = round(time.time() - start_time, 3)
        return True, banner, elapsed

    except (socket.timeout, ConnectionRefusedError, OSError):
        elapsed = round(time.time() - start_time, 3)
        return False, None, elapsed


def scan_range(target, start_port, end_port, threads=50):
    """
    Scan a range of ports on the target host

    Args:
        target (str): IP address or hostname to scan
        start_port (int): Starting port number
        end_port (int): Ending port number

    Returns:
        list: List of open ports
    """
    open_ports = []

    print(f"[*] Scanning {target} from port {start_port} to {end_port}")
    print(f"[*] This may take a while...")

    # TODO: Implement the scanning logic
    # Hint: Loop through port range and call scan_port()
    # Hint: Consider using threading for better performance

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {
            executor.submit(scan_port, target, port): port
            for port in range(start_port, end_port + 1)
        }

        for future in as_completed(futures):
            is_open, banner, elapsed = future.result()

            if is_open:
                port = futures[future]
                open_ports.append(port)
                service = banner if banner else "Unknown service"
                print(f"[OPEN] Port {port:<5} | {elapsed}s | {service}")

    return open_ports


def main():
    """Main function"""
    # TODO: Parse command-line arguments
    # TODO: Validate inputs
    # TODO: Call scan_range()
    # TODO: Display results

    # Example usage (you should improve this):
    if len(sys.argv) < 2:
        print("Usage: python3 port_scanner_template.py <target>")
        print("Example: python3 port_scanner_template.py 172.20.0.10")
        sys.exit(1)

    target = sys.argv[1]
    start_port = 1
    end_port = 65535  # Scan first 1024 ports by default

    print(f"[*] Starting port scan on {target}")
    start = time.time()


    open_ports = scan_range(target, start_port, end_port, threads=50)

    duration = round(time.time() - start, 2)

    print(f"\n[+] Scan complete!")
    print(f"[+] Found {len(open_ports)} open ports:")
    for port in open_ports:
        print(f"    Port {port}: open")


if __name__ == "__main__":
    main()