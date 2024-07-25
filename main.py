import subprocess
import re
import platform

def scan_wifi_networks():
    if platform.system() == "Windows":
        scan_output = subprocess.run(["netsh", "wlan", "show", "network", "mode=Bssid"], capture_output=True, text=True)
    elif platform.system() == "Linux":
        scan_output = subprocess.run(["iwlist", "wlan0", "scan"], capture_output=True, text=True)
    else:
        print("Unsupported platform.")
        return []

    networks = []
    if scan_output.returncode == 0:
        if platform.system() == "Windows":
            networks = parse_windows_wifi_networks(scan_output.stdout)
        elif platform.system() == "Linux":
            networks = parse_linux_wifi_networks(scan_output.stdout)

    return networks

def parse_windows_wifi_networks(output):
    networks = []
    current_network = {}
    lines = output.splitlines()
    for line in lines:
        if re.match(r'\s+SSID \d+ :', line):
            if current_network:
                networks.append(current_network)
                current_network = {}
            current_network['SSID'] = re.sub(r'\s+SSID \d+ :', '', line).strip()
        elif re.match(r'\s+BSSID \d+ :', line):
            current_network['BSSID'] = re.sub(r'\s+BSSID \d+ :', '', line).strip()
        elif re.match(r'\s+Signal \d+ :', line):
            current_network['Signal'] = re.sub(r'\s+Signal \d+ :', '', line).strip()
        elif re.match(r'\s+Authentication\s+', line):
            current_network['Authentication'] = re.sub(r'\s+Authentication\s+', '', line).strip()
        elif re.match(r'\s+Encryption\s+', line):
            current_network['Encryption'] = re.sub(r'\s+Encryption\s+', '', line).strip()
    if current_network:
        networks.append(current_network)
    return networks

def parse_linux_wifi_networks(output):
    networks = []
    current_network = {}
    lines = output.split('Cell')
    for line in lines:
        if 'ESSID:' in line:
            current_network['SSID'] = re.search(r'ESSID:"([^"]+)"', line).group(1)
        if 'Address:' in line:
            current_network['BSSID'] = re.search(r'Address: ([^\s]+)', line).group(1)
        if 'Signal level=' in line:
            current_network['Signal'] = re.search(r'Signal level=(-\d+)', line).group(1)
        if 'Authentication Suites' in line:
            current_network['Authentication'] = re.search(r'Authentication Suites: ([^\n]+)', line).group(1)
        if 'Encryption key:' in line:
            current_network['Encryption'] = re.search(r'Encryption key:([^\n]+)', line).group(1)
            if current_network['Encryption'] == 'off':
                current_network['Encryption'] = 'Open'
            else:
                current_network['Encryption'] = 'Encrypted'
        if 'IE:' in line:
            networks.append(current_network)
            current_network = {}
    return networks

def print_networks(networks):
    if not networks:
        print("No WiFi networks found.")
        return

    print("Detected WiFi Networks:")
    for idx, network in enumerate(networks, start=1):
        print(f"\nNetwork {idx}:")
        print(f"  SSID: {network.get('SSID', 'Unknown')}")
        print(f"  BSSID: {network.get('BSSID', 'Unknown')}")
        print(f"  Signal Strength: {network.get('Signal', 'Unknown')}")
        print(f"  Authentication: {network.get('Authentication', 'Unknown')}")
        print(f"  Encryption: {network.get('Encryption', 'Unknown')}")

def main():
    print("Scanning WiFi networks...")
    networks = scan_wifi_networks()
    print_networks(networks)
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()