to use the port scanner use python3 port_scanner.py <ip address> 

This will scan all the ports from 1 to 65535 on that IP and see if they are open and if they return a header 

NOTE: It might be needed to run the port_scanner inside of the docker container so in that case copying the python file into the container and running inside the shell will work.