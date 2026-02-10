# Honeypot Analysis
2_network_honeypot       | 2026-02-10 01:49:37,055 - INFO - Connection from ('172.20.0.10', 40918)
2_network_honeypot       | 2026-02-10 01:49:37,058 - INFO - Connected (version 2.0, client OpenSSH_10.0p2)
2_network_honeypot       | 2026-02-10 01:49:39,607 - INFO - Auth rejected (none).
2_network_honeypot       | 2026-02-10 01:49:43,264 - INFO - LOGIN ATTEMPT | user=root password=pass12345
2_network_honeypot       | 2026-02-10 01:49:43,264 - INFO - Auth granted (password).
2_network_honeypot       | 2026-02-10 01:49:53,022 - INFO - COMMAND | 172.20.0.10 | ls
2_network_honeypot       | 2026-02-10 01:49:55,160 - INFO - COMMAND | 172.20.0.10 | whoami
2_network_honeypot       | 2026-02-10 01:49:57,485 - INFO - COMMAND | 172.20.0.10 | exit

2_network_honeypot       | 2026-02-10 01:41:18,222 - INFO - Connection from ('172.20.0.10', 50550)
2_network_honeypot       | 2026-02-10 01:41:18,224 - INFO - Connected (version 2.0, client OpenSSH_10.0p2)
2_network_honeypot       | 2026-02-10 01:41:19,991 - INFO - Auth rejected (none).
2_network_honeypot       | 2026-02-10 01:41:24,360 - INFO - LOGIN ATTEMPT | user=root password=wasd123
2_network_honeypot       | 2026-02-10 01:41:24,361 - INFO - Auth granted (password).

## Summary of Observed Attacks
The attacks try to ssh into the honeypot as root to try and gain root access on the machine. It shows the IP address of the attackers, the password they try and use, and finally, the commands they try to run. 

## Notable Patterns
The notable patterns is that attackers try to use common passwords on multiple attempts to try and get access as root. Using the honeypot one can figure out the password table that attackers try to use when trying to access your machine. Not only that many attackers check to make sure they are actually root by using whoami as well as using ls to see the file directory. 

## Recommendations
The recommendations would be to add more fake commands so that you can see what files or commands attackers try to execute when they have root access to a machine. This will help protect yourself from future attacks if you see what they try to do to example machines. Additonally, logging what passwords they try to login in as well help guide people when making their own passwords to not make them similar to the common passwords attempted by the attackers. 