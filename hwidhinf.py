import uuid
import winreg
import ctypes
import sys
import hashlib
import random
import string
import subprocess
import time
import os
import wmi
import struct
from ctypes import windll, c_uint64, c_uint32, c_uint16, c_ubyte, Structure, sizeof, POINTER

DISCLAIMER = """DISCLAIMER: This License Agreement permits the Licensee, Sibersec Indonesia, to engage in cybersecurity operations, including but not limited to, network security assessments, hardware information modification, penetration testing, vulnerability analysis, and other related services in accordance with applicable laws and ethical guidelines."""

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def get_volume_id():
    try:
        output = subprocess.check_output("vol C:", shell=True).decode()
        return output.split()[-1].strip()
    except:
        return generate_random_string(9)

def get_hardware_hash():
    try:
        output = subprocess.check_output("powershell.exe Get-WmiObject -Class Win32_ComputerSystemProduct | Select-Object -ExpandProperty UUID", shell=True).decode().strip()
        return output
    except:
        return str(uuid.uuid4())

def generate_hwid():
    components = [
        get_hardware_hash(),
        get_volume_id(),
        generate_random_string(32),
        str(random.randint(1000000000, 9999999999))
    ]
    combined = ':'.join(components).encode()
    return hashlib.sha256(combined).hexdigest()

def modify_registry(key_path, value_name, new_value, value_type=winreg.REG_SZ):
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_ALL_ACCESS)
        winreg.SetValueEx(key, value_name, 0, value_type, new_value)
        winreg.CloseKey(key)
        print(f"Modified {key_path}\\{value_name}")
    except Exception as e:
        print(f"Error modifying {key_path}\\{value_name}: {e}")

def spoof_mac_address():
    new_mac = ':'.join(['{:02x}'.format(random.randint(0x00, 0xff)) for _ in range(6)])
    try:
        subprocess.run(["reg", "add", "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e972-e325-11ce-bfc1-08002be10318}\\0001", "/v", "NetworkAddress", "/d", new_mac, "/f"], check=True)
        print(f"Spoofed MAC address to: {new_mac}")
    except subprocess.CalledProcessError as e:
        print(f"Error spoofing MAC address: {e}")

def modify_boot_id():
    new_boot_id = str(uuid.uuid4())
    try:
        subprocess.run(["bcdedit", "/set", "{current}", "identifier", new_boot_id], check=True)
        print(f"Modified boot identifier to: {new_boot_id}")
    except subprocess.CalledProcessError as e:
        print(f"Error modifying boot identifier: {e}")

def spoof_cpu_info():
    new_cpu = f"Intel(R) Core(TM) i{random.randint(5,9)}-{random.randint(10000,13900)}K CPU @ {random.uniform(3.0, 5.5):.2f}GHz"
    modify_registry(r"HARDWARE\DESCRIPTION\System\CentralProcessor\0", "ProcessorNameString", new_cpu)
    modify_registry(r"HARDWARE\DESCRIPTION\System\CentralProcessor\0", "VendorIdentifier", "GenuineIntel")
    modify_registry(r"HARDWARE\DESCRIPTION\System\CentralProcessor\0", "Identifier", f"Intel64 Family 6 Model {random.randint(60, 190)} Stepping {random.randint(0, 9)}")
    print(f"Spoofed CPU to: {new_cpu}")

def spoof_gpu_info():
    gpu_brands = ["NVIDIA GeForce RTX", "AMD Radeon RX"]
    new_gpu = f"{random.choice(gpu_brands)} {random.randint(3000,4090)}"
    modify_registry(r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0000", "DriverDesc", new_gpu)
    modify_registry(r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0000", "HardwareInformation.ChipType", new_gpu)
    print(f"Spoofed GPU to: {new_gpu}")

def spoof_bios_info():
    new_manufacturer = random.choice(["Dell", "HP", "Lenovo", "ASUS", "Acer"])
    new_model = f"{new_manufacturer}-{generate_random_string(8)}"
    modify_registry(r"HARDWARE\DESCRIPTION\System\BIOS", "SystemManufacturer", new_manufacturer)
    modify_registry(r"HARDWARE\DESCRIPTION\System\BIOS", "SystemProductName", new_model)
    modify_registry(r"HARDWARE\DESCRIPTION\System\BIOS", "BIOSVersion", generate_random_string(10))
    print(f"Spoofed BIOS info: Manufacturer - {new_manufacturer}, Model - {new_model}")

def spoof_disk_info():
    new_disk_serial = generate_random_string(20)
    modify_registry(r"HARDWARE\DEVICEMAP\Scsi\Scsi Port 0\Scsi Bus 0\Target Id 0\Logical Unit Id 0", "SerialNumber", new_disk_serial)
    print(f"Spoofed Disk Serial to: {new_disk_serial}")

def spoof_smbios():
    try:
        subprocess.run(["wmic", "bios", "set", f"SMBIOSBIOSVersion={generate_random_string(10)}"], shell=True)
        subprocess.run(["wmic", "computersystem", "set", f"uuid={str(uuid.uuid4())}"], shell=True)
        print("Modified SMBIOS information")
    except Exception as e:
        print(f"Error modifying SMBIOS: {e}")

def spoof_tpm():
    modify_registry(r"SYSTEM\CurrentControlSet\Control\TPM\12", "SpecVersion", "2.0")
    modify_registry(r"SYSTEM\CurrentControlSet\Control\TPM\12", "ManufacturerVersion", generate_random_string(8))
    print("Spoofed TPM information")

def spoof_hwid():
    if not is_admin():
        run_as_admin()

    print(DISCLAIMER)
    input("Press Enter to continue...")

    old_hwid = generate_hwid()
    print(f"Current HWID: {old_hwid}")

    # Perform deep system modifications
    spoof_cpu_info()
    spoof_gpu_info()
    spoof_bios_info()
    spoof_disk_info()
    spoof_mac_address()
    modify_boot_id()
    spoof_smbios()
    spoof_tpm()

    # Additional registry modifications
    new_hwid = generate_hwid()
    new_product_id = '-'.join([generate_random_string(5) for _ in range(5)])
    new_install_date = hex(int(time.time()))[2:].upper()

    registry_modifications = [
        (r"SYSTEM\CurrentControlSet\Control\IDConfigDB\Hardware Profiles\0001", "HwProfileGuid", "{" + str(uuid.uuid4()) + "}"),
        (r"SOFTWARE\Microsoft\Cryptography", "MachineGuid", str(uuid.uuid4())),
        (r"SOFTWARE\Microsoft\Windows NT\CurrentVersion", "ProductId", new_product_id),
        (r"SOFTWARE\Microsoft\Windows NT\CurrentVersion", "InstallDate", new_install_date, winreg.REG_DWORD),
        (r"SOFTWARE\Microsoft\Windows NT\CurrentVersion", "BuildGUID", str(uuid.uuid4())),
        (r"SYSTEM\CurrentControlSet\Control\SystemInformation", "ComputerHardwareId", "{" + str(uuid.uuid4()) + "}"),
        (r"SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate", "SusClientId", str(uuid.uuid4())),
        (r"SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate", "SusClientIDValidation", generate_random_string(44)),
        (r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0000", "HardwareInformation.AdapterString", f"NVIDIA GeForce RTX {random.randint(2000, 4090)}"),
        (r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0000", "HardwareInformation.ChipType", f"NVIDIA GeForce RTX {random.randint(2000, 4090)}"),
    ]

    for key_path, value_name, new_value, *args in registry_modifications:
        value_type = args[0] if args else winreg.REG_SZ
        modify_registry(key_path, value_name, new_value, value_type)

    # Modify USB controller information
    modify_registry(r"SYSTEM\CurrentControlSet\Enum\USB", "Vid", generate_random_string(4))
    modify_registry(r"SYSTEM\CurrentControlSet\Enum\USB", "Pid", generate_random_string(4))

    # Flush DNS cache and reset network adapters
    os.system("ipconfig /flushdns")
    os.system("netsh winsock reset")
    os.system("netsh int ip reset")

    print(f"New HWID set to: {new_hwid}")
    print(f"New Product ID: {new_product_id}")
    print("\nHWID spoofing complete. It's strongly recommended to restart your system for changes to take full effect.")
    print("Note: Some changes are simulated and may not affect actual hardware behavior.")

if __name__ == "__main__":
    spoof_hwid()