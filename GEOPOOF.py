import winreg
import ctypes
import sys
import random
import subprocess
import os
import time
import json
import requests
from faker import Faker

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

def modify_registry(key_path, value_name, new_value, value_type=winreg.REG_SZ):
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_ALL_ACCESS)
        winreg.SetValueEx(key, value_name, 0, value_type, new_value)
        winreg.CloseKey(key)
        print(f"Modified {key_path}\\{value_name}")
    except Exception as e:
        print(f"Error modifying {key_path}\\{value_name}: {e}")

def spoof_gps_location(latitude, longitude):
    print(f"Spoofing GPS location to: {latitude}, {longitude}")
    modify_registry(r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location", "Value", "Allow")
    modify_registry(r"SYSTEM\CurrentControlSet\Services\lfsvc\Settings", "Status", 1, winreg.REG_DWORD)
    modify_registry(r"SYSTEM\CurrentControlSet\Services\lfsvc\Settings", "Latitude", latitude, winreg.REG_QWORD)
    modify_registry(r"SYSTEM\CurrentControlSet\Services\lfsvc\Settings", "Longitude", longitude, winreg.REG_QWORD)

def spoof_timezone(timezone):
    print(f"Spoofing timezone to: {timezone}")
    os.system(f'tzutil /s "{timezone}"')
    modify_registry(r"SYSTEM\CurrentControlSet\Control\TimeZoneInformation", "TimeZoneKeyName", timezone)

def spoof_language_and_region(language, region):
    print(f"Spoofing language to {language} and region to {region}")
    os.system(f'setx LANG {language}')
    os.system(f'setx LANGUAGE {language}')
    modify_registry(r"SYSTEM\CurrentControlSet\Control\Nls\Language", "Default", language)
    modify_registry(r"SYSTEM\CurrentControlSet\Control\Nls\Locale", "(Default)", region)

def spoof_ip_address(ip):
    print(f"Attempting to spoof IP address to: {ip}")
    modify_registry(r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters", "IPAddress", ip)
    os.system('ipconfig /release')
    time.sleep(5)
    os.system('ipconfig /renew')

def spoof_mac_address():
    new_mac = ':'.join(['{:02x}'.format(random.randint(0x00, 0xff)) for _ in range(6)])
    print(f"Spoofing MAC address to: {new_mac}")
    subprocess.run(["reg", "add", "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e972-e325-11ce-bfc1-08002be10318}\\0001", "/v", "NetworkAddress", "/d", new_mac, "/f"], check=True)

def spoof_browser_geolocation():
    print("Modifying browser geolocation settings")
    # Chrome
    modify_registry(r"SOFTWARE\Policies\Google\Chrome", "DefaultGeolocationSetting", 1, winreg.REG_DWORD)
    # Firefox (this is a user preference, so it's set in a different way)
    os.system('echo user_pref("geo.enabled", false);>> %APPDATA%\\Mozilla\\Firefox\\Profiles\\*.default\\user.js')

def deep_location_spoof():
    if not is_admin():
        run_as_admin()

    print("DISCLAIMER: This script performs deep system modifications. Use at your own risk and only in controlled environments.")
    input("Press Enter to continue...")

    fake = Faker()
    fake_location = fake.location_on_land()

    latitude, longitude = fake_location[0], fake_location[1]
    country = fake_location[3]
    timezone = fake.timezone()
    language = fake.language_code()
    region = fake.current_country_code()

    # Fetch a random IP from the spoofed country
    try:
        response = requests.get(f"https://api.ipify.org?format=json")
        ip = response.json()["ip"]
    except:
        ip = f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"

    spoof_gps_location(latitude, longitude)
    spoof_timezone(timezone)
    spoof_language_and_region(language, region)
    spoof_ip_address(ip)
    spoof_mac_address()
    spoof_browser_geolocation()

    # Modify system files to reinforce the spoofed location
    with open(r"C:\Windows\System32\drivers\etc\hosts", "a") as hosts_file:
        hosts_file.write(f"\n{ip} localhost")

    # Modify network settings
    os.system(f'netsh interface ipv4 set address name="Ethernet" static {ip} 255.255.255.0')

    # Modify system environment variables
    os.environ['COUNTRY'] = country
    os.environ['LANG'] = language
    os.environ['TZ'] = timezone

    print("\nLocation spoofing complete. System restart recommended for changes to take full effect.")
    print(f"Spoofed Location: {country} ({latitude}, {longitude})")
    print(f"Timezone: {timezone}")
    print(f"Language: {language}")
    print(f"IP Address: {ip}")
    print("\nNote: These changes are extensive and may cause system instability.")

if __name__ == "__main__":
    deep_location_spoof()