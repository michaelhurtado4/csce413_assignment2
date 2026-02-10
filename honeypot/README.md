## Honeypot Starter Template

This directory is a starter template for the honeypot portion of the assignment.

### What you need to implement
- Choose a protocol (SSH, HTTP, or multi-protocol).
- Simulate a convincing service banner and responses.
- Log connection metadata, authentication attempts, and attacker actions.
- Store logs under `logs/` and include an `analysis.md` summary.
- Update `honeypot.py` 
### Getting started
1. Implement your honeypot logic in `honeypot.py`.
2. Summarize your findings in `analysis.md`.
3. Run from the repo root with `docker-compose up honeypot`.


Paramiko is a python library that implements the SSH protocol so that python programs can use SSH. This honeypot leverages paramiko to act as a SSH server allowing clients to connect to it using SSH. The honeypot works by impersonating a Ubuntu VM as whenever the attacker trys to ssh to the server it responds with a ssh banner and a password checker. It generates RSA keys as well to prevent suspicion from attackers that the VM might be fake. The paramiko server responds like a normal ubuntu vm does it shows the version, the command line everything so that the attackers think it is real. Some commands are hardcoded to show something like ls, whoami, exit, etc. When the attacker interacts with the SSH server all of this is logged and stored. The IP is logged, the username and password is logged, as well as the commands attempted is logged. This allows for you to check what attackers will try to do your machine if they get root access to it. 

To test the honeypot build the docker container first. Then from a container/shell within the docker network try to ssh to 172.20.0.30 on port 22 and it will fake respond like a real SSH request. 