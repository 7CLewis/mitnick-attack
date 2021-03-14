import threading
c = threading.Condition()
val = 0

def t1():
    global val
    c.acquire()
    for i in range(10):
        val = val + 1
        print("VAL1: " + str(val))
    c.release()

def t2():
    global val
    c.acquire()
    for i in range(10):
        val = val + 1
        print("VAL2: " + str(val))
    c.release()

def main():
    thread1 = threading.Thread(target=t1)
    thread2 = threading.Thread(target=t2)
    
    thread1.start()
    thread2.start()
    
    thread1.join()
    thread2.join()

    print("VAL FINAL: " + str(val))

if __name__ == "__main__":
    main()