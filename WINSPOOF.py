import winreg
import ctypes
import sys
import random
import uuid
import subprocess
import os
import time
import string
import hashlib
import wmi

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

def modify_registry(key_path, value_name, new_value, value_type=winreg.REG_SZ):
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_ALL_ACCESS)
        winreg.SetValueEx(key, value_name, 0, value_type, new_value)
        winreg.CloseKey(key)
        print(f"Modified {key_path}\\{value_name}")
    except Exception as e:
        print(f"Error modifying {key_path}\\{value_name}: {e}")

def spoof_windows_version():
    print("Spoofing Windows version information...")
    new_build = str(random.randint(19041, 19045))
    new_display_version = f"21H{random.randint(1,2)}"
    new_edition_id = random.choice(["Core", "Professional", "Enterprise"])
    new_product_name = f"Windows 10 {new_edition_id}"
    
    modify_registry(r"SOFTWARE\Microsoft\Windows NT\CurrentVersion", "CurrentBuild", new_build)
    modify_registry(r"SOFTWARE\Microsoft\Windows NT\CurrentVersion", "DisplayVersion", new_display_version)
    modify_registry(r"SOFTWARE\Microsoft\Windows NT\CurrentVersion", "EditionID", new_edition_id)
    modify_registry(r"SOFTWARE\Microsoft\Windows NT\CurrentVersion", "ProductName", new_product_name)

def spoof_system_info():
    print("Spoofing system information...")
    new_computer_name = generate_random_string(8).upper()
    new_username = generate_random_string(8).lower()
    
    os.system(f"wmic computersystem where name='%computername%' call rename {new_computer_name}")
    os.system(f"wmic useraccount where name='%username%' call rename {new_username}")
    
    modify_registry(r"SYSTEM\CurrentControlSet\Control\ComputerName\ComputerName", "ComputerName", new_computer_name)
    modify_registry(r"SYSTEM\CurrentControlSet\Control\ComputerName\ActiveComputerName", "ComputerName", new_computer_name)

def spoof_install_date():
    print("Spoofing Windows installation date...")
    new_install_date = hex(int(time.time()) - random.randint(0, 31536000))[2:].upper()  # Random date within the last year
    modify_registry(r"SOFTWARE\Microsoft\Windows NT\CurrentVersion", "InstallDate", new_install_date, winreg.REG_DWORD)

def spoof_product_id():
    print("Spoofing Windows Product ID...")
    new_product_id = '-'.join([generate_random_string(5) for _ in range(5)])
    modify_registry(r"SOFTWARE\Microsoft\Windows NT\CurrentVersion", "ProductId", new_product_id)

def spoof_machine_guid():
    print("Spoofing Machine GUID...")
    new_machine_guid = str(uuid.uuid4())
    modify_registry(r"SOFTWARE\Microsoft\Cryptography", "MachineGuid", new_machine_guid)

def spoof_hardware_profile():
    print("Spoofing Hardware Profile...")
    new_hw_profile_guid = "{" + str(uuid.uuid4()) + "}"
    modify_registry(r"SYSTEM\CurrentControlSet\Control\IDConfigDB\Hardware Profiles\0001", "HwProfileGuid", new_hw_profile_guid)

def spoof_windows_update_info():
    print("Spoofing Windows Update information...")
    new_sus_client_id = str(uuid.uuid4())
    new_sus_client_id_validation = generate_random_string(44)
    
    modify_registry(r"SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate", "SusClientId", new_sus_client_id)
    modify_registry(r"SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate", "SusClientIDValidation", new_sus_client_id_validation)

def spoof_telemetry_id():
    print("Spoofing Telemetry ID...")
    new_telemetry_id = "{" + str(uuid.uuid4()) + "}"
    modify_registry(r"SOFTWARE\Microsoft\Windows\CurrentVersion\Diagnostics\DiagTrack", "DiagTrackAuthorization", new_telemetry_id)

def spoof_network_info():
    print("Spoofing network information...")
    new_mac = ':'.join(['{:02x}'.format(random.randint(0x00, 0xff)) for _ in range(6)])
    
    try:
        subprocess.run(["reg", "add", "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e972-e325-11ce-bfc1-08002be10318}\\0001", "/v", "NetworkAddress", "/d", new_mac, "/f"], check=True)
        print(f"Spoofed MAC address to: {new_mac}")
    except subprocess.CalledProcessError as e:
        print(f"Error spoofing MAC address: {e}")
    
    os.system("ipconfig /release")
    time.sleep(5)
    os.system("ipconfig /renew")

def spoof_time_zone():
    print("Spoofing time zone...")
    time_zones = ["Pacific Standard Time", "Mountain Standard Time", "Central Standard Time", "Eastern Standard Time"]
    new_time_zone = random.choice(time_zones)
    os.system(f"tzutil /s \"{new_time_zone}\"")

def spoof_windows_defender():
    print("Modifying Windows Defender information...")
    modify_registry(r"SOFTWARE\Microsoft\Windows Defender\Miscellaneous Configuration", "UILockdown", 0, winreg.REG_DWORD)
    modify_registry(r"SOFTWARE\Microsoft\Windows Defender", "ProductStatus", random.randint(0, 5), winreg.REG_DWORD)

def spoof_windows_activation():
    print("Spoofing Windows activation status...")
    modify_registry(r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\SoftwareProtectionPlatform", "BackupProductKeyDefault", generate_random_string(29))
    modify_registry(r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\SoftwareProtectionPlatform", "actionlist", generate_random_string(32), winreg.REG_BINARY)

def winspoof():
    if not is_admin():
        run_as_admin()

    print("DISCLAIMER: This License Agreement permits the Licensee, Sibersec Indonesia, to engage in cybersecurity operations, including but not limited to, network security assessments, hardware information modification, penetration testing, vulnerability analysis, and other related services in accordance with applicable laws and ethical guidelines.")
    input("Press Enter to continue...")

    spoof_windows_version()
    spoof_system_info()
    spoof_install_date()
    spoof_product_id()
    spoof_machine_guid()
    spoof_hardware_profile()
    spoof_windows_update_info()
    spoof_telemetry_id()
    spoof_network_info()
    spoof_time_zone()
    spoof_windows_defender()
    spoof_windows_activation()

    print("\nWindows information spoofing complete. It's strongly recommended to restart your system for changes to take full effect.")
    print("Note: Some changes are simulated and may not affect actual system behavior or bypass all detection methods.")

if __name__ == "__main__":
    winspoof()
