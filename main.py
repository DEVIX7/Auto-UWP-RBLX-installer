import os
import re
import zipfile
import subprocess
import shutil
import time

try:
    from colorama import init, Fore, Style
except ImportError:
    print("Colorama not found. Installing...")
    os.system("pip install colorama")
    from colorama import init, Fore, Style

try:
    import requests
except ImportError:
    print("Requests not found. Installing...")
    os.system("pip install requests")
    import requests

os.system('cls')

def print_blue_logo():
    logo = r"""
   ___       __         __  ___      _____    ___       __   __           _ _   _          __       ____       
  / _ |__ __/ /____    / / / / | /| / / _ \  / _ \___  / /  / /__ __ __  ( | ) (_)__  ___ / /____ _/ / /__ ____
 / __ / // / __/ _ \  / /_/ /| |/ |/ / ___/ / , _/ _ \/ _ \/ / _ \\ \ /  |/|/ / / _ \(_-</ __/ _ `/ / / -_) __/
/_/ |_\_,_/\__/\___/  \____/ |__/|__/_/    /_/|_|\___/_.__/_/\___/_\_\       /_/_//_/___/\__/\_,_/_/_/\__/_/   
            MADE BY DEVIX7 | github.com/DEVIX7 | Auto UWP Roblox " installer @ Version: 1.5
"""
    print(Fore.CYAN + Style.BRIGHT + logo + Style.RESET_ALL)

class MsixBundleDownloader:

    def get_insert_number(self):
        while True:
            insert_num = input("Enter the Roblox Instance No.: ")
            if insert_num.isdigit():
                os.system('cls')
                print_blue_logo()
                print(f"Roblox Instance No.: {insert_num}")
                print("\nLogs:")
                return insert_num
            else:
                print(Fore.RED + "Invalid input. Please enter a valid number." + Style.RESET_ALL)
        
    def create_temp_directory(self):
        current_directory = os.path.dirname(os.path.abspath(__file__))
        temp_directory = os.path.join(current_directory, "temp")
        if not os.path.exists(temp_directory):
            os.mkdir(temp_directory)
            print(f"Created 'temp' directory at {temp_directory}")
        return temp_directory

    def clear_temp_directory(self, temp_directory):
        print(f"Clearing 'temp' directory at {temp_directory}...")
        shutil.rmtree(temp_directory)
        os.mkdir(temp_directory)

    def download_msix_bundle_file(self, product_url, roblox_path):
        insert_num = self.get_insert_number()

        temp_directory = self.create_temp_directory()
        self.clear_temp_directory(temp_directory)

        api_url = "https://store.rg-adguard.net/api/GetFiles"

        body = {
            'type': 'url',
            'url': product_url,
            'ring': 'RP',
            'lang': 'en-US'
        }

        print(f"{Fore.YELLOW}Necessary msixbundle file not found.Attempting to find link via website:{Style.RESET_ALL} https://store.rg-adguard.net/ ")
        response = requests.post(api_url, data=body)
        raw = response.text

        pattern = r'<tr style.*<a href="(?P<url>.*)"\s.*>(?P<text>.*)<\/a>'
        msix_bundle_links = re.findall(pattern, raw)
        msix_bundle_links = [(url, text) for url, text in msix_bundle_links if text.strip().endswith('.msixbundle')]

        for url, text in msix_bundle_links:
            architecture = "x86" if "x86" in text else "x64"
            download_file = os.path.join(temp_directory, text.replace(".appx", ".msixbundle"))
            if not os.path.exists(download_file):
                print(f"{Fore.YELLOW}Found the link to the msixbundle file. Attempting to download. This may take a moment.{Style.RESET_ALL}")
                response = requests.get(url)
                if response.status_code == 200:
                    with open(download_file, 'wb') as f:
                        f.write(response.content)
                    print(f"{Fore.GREEN}Successfully downloaded {Style.RESET_ALL}{download_file}")
                    self.extract_msix_bundle(download_file, temp_directory)  # Extract the downloaded file to the 'temp' folder
                    self.extract_win32_msix_contents(temp_directory)  # Extract contents of _Win32.msix file to 'temp2'
                    self.delete_appx_signature_file(temp_directory)  # Delete "AppxSignature.p7x" file from 'temp2'
                    self.update_appx_manifest(temp_directory, insert_num)  # Update AppxManifest.xml with the user input number
                    self.register_appx_package(temp_directory)  # Register the modified package
                    return True
                else:
                    print(Fore.RED + "Failed to download the msixbundle file." + Style.RESET_ALL)
                    return False

        print(Fore.RED + "No valid msixbundle link found." + Style.RESET_ALL)
        return False

    def extract_msix_bundle(self, zip_file_path, extraction_path):
        print(f"{Fore.BLUE}Extracting{Style.RESET_ALL} {zip_file_path} {Fore.BLUE}to{Style.RESET_ALL} {extraction_path}...")
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(extraction_path)
        print(Fore.GREEN + "Extraction completed." + Style.RESET_ALL)

    def extract_win32_msix_contents(self, base_path):
        for root, _, files in os.walk(base_path):
            for file in files:
                if "_Win32.msix" in file:
                    msix_file_path = os.path.join(root, file)
                    temp2_path = os.path.join(base_path, "temp2")
                    with zipfile.ZipFile(msix_file_path, 'r') as zip_ref:
                        zip_ref.extractall(temp2_path)
                    print(f"{Fore.BLUE}Extracted contents of {Style.RESET_ALL}{msix_file_path} {Fore.BLUE}to{Style.RESET_ALL} {temp2_path}")
                    return

    def delete_appx_signature_file(self, base_path):
        appx_signature_file_path = os.path.join(base_path, "temp2", "AppxSignature.p7x")
        if os.path.exists(appx_signature_file_path):
            os.remove(appx_signature_file_path)
            print(f"{Fore.GREEN}Deleted{Style.RESET_ALL} {appx_signature_file_path}")

    def update_appx_manifest(self, base_path, insert_num):
        appx_manifest_path = os.path.join(base_path, "temp2", "AppxManifest.xml")
        if os.path.isfile(appx_manifest_path):
            print(f"{Fore.BLUE}Modifying AppxManifest.xml file in{Style.RESET_ALL} {base_path}...")

            with open(appx_manifest_path, 'r') as f:
                appx_manifest_content = f.read()

            appx_manifest_content = appx_manifest_content.replace(
                '<Identity Name="ROBLOXCORPORATION.ROBLOX"',
                f'<Identity Name="ROBLOXCORPORATION.ROBLOX.{insert_num}"'
            )
            appx_manifest_content = appx_manifest_content.replace(
                '<DisplayName>Roblox</DisplayName>',
                f'<DisplayName>Roblox {insert_num}</DisplayName>'
            )
            appx_manifest_content = appx_manifest_content.replace(
                'uap:VisualElements DisplayName="Roblox"',
                f'uap:VisualElements DisplayName="Roblox {insert_num}"'
            )
            appx_manifest_content = appx_manifest_content.replace(
                'uap:DefaultTile ShortName="Roblox"',
                f'uap:DefaultTile ShortName="Roblox {insert_num}"'
            )

            with open(appx_manifest_path, 'w') as f:
                f.write(appx_manifest_content)

            print(Fore.GREEN + "AppxManifest.xml has been updated." +Style.RESET_ALL)
        else:
            print(Fore.RED + "AppxManifest.xml not found."  + Style.RESET_ALL)

    def register_appx_package(self, base_path):
        appx_manifest_path = os.path.join(base_path, "temp2", "AppxManifest.xml")
        if os.path.isfile(appx_manifest_path):
            ps_command = f'Add-AppxPackage -path "{appx_manifest_path}" -register'
            print(f"{Fore.BLUE}Running PowerShell command:{Style.RESET_ALL} {ps_command}")
            try:
                subprocess.run(["powershell", "-Command", ps_command], check=True)
                print(Fore.GREEN + "Appx package registered successfully." +Style.RESET_ALL)
                time.sleep(1.5)
            except subprocess.CalledProcessError as e:
                print(f"{Fore.RED}Failed to register the Appx package. Error:{Style.RESET_ALL} {e}")
        else:
            print({Fore.RED}+"AppxManifest.xml not found."+{Style.RESET_ALL})

if __name__ == "__main__":
    init(autoreset=True)
    print_blue_logo()
    downloader = MsixBundleDownloader()
    product_url = "https://www.microsoft.com/store/productId/9NBLGGGZM6WM"
    downloader.download_msix_bundle_file(product_url, os.path.dirname(os.path.abspath(__file__)))