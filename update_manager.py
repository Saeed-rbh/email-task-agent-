import os
import sys
import requests
import subprocess
import time

GITHUB_REPO = "Saeed-rbh/email-task-agent-"
CURRENT_VERSION_FILE = "VERSION.txt"

def get_current_version():
    try:
        # Check for VERSION.txt in the same directory as the executable
        base_path = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
        version_path = os.path.join(base_path, CURRENT_VERSION_FILE)
        
        # If it's not in _MEIPASS, check the directory where the .exe is running
        if not os.path.exists(version_path):
             version_path = os.path.join(os.path.dirname(sys.executable), CURRENT_VERSION_FILE)

        if os.path.exists(version_path):
            with open(version_path, 'r') as f:
                return f.read().strip()
    except Exception as e:
        print(f"Error reading version: {e}")
    return "0.0.0"

def check_for_updates():
    current_version = get_current_version()
    print(f"Current version: {current_version}")
    
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        latest_version = data['tag_name'].lstrip('v')
        print(f"Latest version available: {latest_version}")
        
        if latest_version > current_version:
            print("Update found! Preparing to download...")
            # Find the EmailAgent.exe asset
            assets = data.get('assets', [])
            download_url = None
            for asset in assets:
                if asset['name'] == 'EmailAgent.exe':
                    download_url = asset['browser_download_url']
                    break
            
            if download_url:
                perform_update(download_url, latest_version)
            else:
                print("EmailAgent.exe not found in release assets.")
        else:
            print("You are running the latest version.")
            
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None and e.response.status_code == 404:
            print("Update check skipped: Repository is private or not found.")
        else:
            print(f"Update check failed: {e}")
    except Exception as e:
        print(f"Update check failed: {e}")

def perform_update(url, new_version):
    try:
        exe_path = sys.executable
        parent_dir = os.path.dirname(exe_path)
        new_exe_path = os.path.join(parent_dir, f"EmailAgent_new.exe")
        
        print(f"Downloading update to {new_exe_path}...")
        response = requests.get(url, stream=True)
        with open(new_exe_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print("Download complete. Creating updater script...")
        create_updater_and_restart(exe_path, new_exe_path)
        
    except Exception as e:
        print(f"Update failed: {e}")

def create_updater_and_restart(old_exe, new_exe):
    # On Windows, we can't replace the running .exe.
    # We create a .bat file that waits for this process to exit,
    # replaces the file, and restarts.
    
    bat_content = f"""
@echo off
timeout /t 2 /nobreak > nul
move /y "{new_exe}" "{old_exe}"
start "" "{old_exe}"
del "%~f0"
"""
    bat_path = os.path.join(os.path.dirname(old_exe), "update_helper.bat")
    with open(bat_path, 'w') as f:
        f.write(bat_content)
    
    print("Updater ready. Application will now restart...")
    subprocess.Popen([bat_path], shell=True)
    sys.exit(0)

if __name__ == "__main__":
    check_for_updates()
