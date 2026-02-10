## Port Knocking Starter Template

This directory is a starter template for the port knocking portion of the assignment.

### What you need to implement
- Pick a protected service/port (default is 2222).
- Define a knock sequence (e.g., 1234, 5678, 9012).
- Implement a server that listens for knocks and validates the sequence.
- Open the protected port only after a valid sequence.
- Add timing constraints and reset on incorrect sequences.
- Implement a client to send the knock sequence.

### Getting started
1. Implement your server logic in `knock_server.py`.
2. Implement your client logic in `knock_client.py`.
3. Update `demo.sh` to demonstrate your flow.
4. Run from the repo root with `docker compose up port_knocking`.

### Example usage
```bash
python3 knock_client.py --target 172.20.0.40 --sequence 1234,5678,9012
```
This implementation works by setting up a listener on the server where the protected port is located. The script will reset the firewall rules and add a drop to any connection to the protected port. Then it sets up listeners to the sequence ports waiting for them to knocked by the client. Then the client will try to connect to the sequence ports in order, and the server script will check if the sequence was completed in order in the right amount of time. If the sequence is complete the server script will change the firewall rules to allow connections to the protected port from the client. 