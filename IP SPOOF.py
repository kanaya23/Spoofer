import subprocess
import random
import winreg
import ctypes
import sys
import time

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

def generate_random_ip():
    return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"

def modify_hosts_file(ip, hostname):
    with open(r"C:\Windows\System32\drivers\etc\hosts", "a") as hosts_file:
        hosts_file.write(f"\n{ip} {hostname}")

def modify_dns_cache(ip, hostname):
    subprocess.run(["ipconfig", "/flushdns"], capture_output=True)
    subprocess.run(["dnscmd", "/recordadd", ".", hostname, "A", ip], capture_output=True)

def modify_registry(ip):
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters", 0, winreg.KEY_ALL_ACCESS)
        winreg.SetValueEx(key, "IPAddress", 0, winreg.REG_MULTI_SZ, [ip])
        winreg.CloseKey(key)
        print(f"Modified registry to show IP: {ip}")
    except Exception as e:
        print(f"Error modifying registry: {e}")

def spoof_ip():
    if not is_admin():
        run_as_admin()

    print("DISCLAIMER: This script is for educational purposes only. Ensure you have proper authorization before use.")
    input("Press Enter to continue...")

    original_ip = subprocess.run(["ipconfig"], capture_output=True, text=True).stdout
    print(f"Original IP information:\n{original_ip}")

    new_ip = generate_random_ip()
    print(f"Attempting to spoof IP to: {new_ip}")

    # Modify hosts file
    modify_hosts_file(new_ip, "localhost")

    # Modify DNS cache
    modify_dns_cache(new_ip, "localhost")

    # Modify registry
    modify_registry(new_ip)

    # Restart network adapter
    subprocess.run(["netsh", "interface", "set", "interface", "Ethernet", "disable"], capture_output=True)
    time.sleep(5)
    subprocess.run(["netsh", "interface", "set", "interface", "Ethernet", "enable"], capture_output=True)

    print("IP spoofing attempt complete. Note that this does not change your actual public IP address.")
    print("Some applications and websites may still detect your real IP.")

    new_ip_info = subprocess.run(["ipconfig"], capture_output=True, text=True).stdout
    print(f"New IP information (local view):\n{new_ip_info}")

if __name__ == "__main__":
    spoof_ip()