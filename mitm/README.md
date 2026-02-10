## MITM Starter Template

This directory is a starter template for the MITM portion of the assignment.

### What you need to implement
- Capture traffic between the web app and database.
- Analyze packets for sensitive data and explain the impact.
- Record your findings.
- Include evidence (pcap files or screenshots) alongside your report.

### Getting started
1. Run your capture workflow from this directory or the repo root.
2. Save artifacts (pcap or screenshots) in this folder.
3. Document everything.


Steps:
Use tcpdump to intercept traffic between the webapp and database. The traffic is not encrypted so it's possible to see what is being sent.

docker exec 2_network_webapp tcpdump -i eth0 -nn -vv -X

After looking at the packets the flag will be revealed and that flag can be used to get flag number 3 

docker exec 2_network_webapp curl -H "Authorization: Bearer FLAG{n3tw0rk_tr4ff1c_1s_n0t_s3cur3}" http://172.20.0.21:8888/flag