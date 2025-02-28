#!/usr/bin/env python3
import os
import platform
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path
import urllib.request

def print_header(message):
    """Print a formatted header message."""
    print("\n" + "=" * 60)
    print(f"  {message}")
    print("=" * 60)

def print_step(message):
    """Print a step message."""
    print(f"\n👉 {message}")

def print_success(message):
    """Print a success message."""
    print(f"\n✅ {message}")

def print_error(message):
    """Print an error message."""
    print(f"\n❌ {message}")

def run_command(command, shell=False):
    """Run a command and return its output."""
    try:
        result = subprocess.run(
            command,
            shell=shell,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, f"Command failed with exit code {e.returncode}: {e.stderr}"

def download_file(url, destination):
    """Download a file from a URL to a destination."""
    try:
        print_step(f"Downloading from {url}")
        with urllib.request.urlopen(url) as response, open(destination, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        return True
    except Exception as e:
        print_error(f"Failed to download: {e}")
        return False

def install_fonts_windows():
    """Install fonts on Windows."""
    print_header("Installing Devanagari Fonts for Windows")
    
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        # URLs for the Noto Sans Devanagari fonts
        font_urls = [
            # Latest Noto Sans Devanagari from Google Fonts
            "https://fonts.google.com/download?family=Noto%20Sans%20Devanagari",
            # Lohit Devanagari
            "https://releases.pagure.org/lohit/lohit-devanagari-ttf-2.95.4.tar.gz"
        ]
        
        # Download and install each font
        for url in font_urls:
            filename = os.path.join(temp_dir, os.path.basename(url))
            if download_file(url, filename):
                # Extract if it's a compressed file
                if filename.endswith('.zip'):
                    print_step(f"Extracting {filename}")
                    import zipfile
                    with zipfile.ZipFile(filename, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)
                elif filename.endswith('.tar.gz'):
                    print_step(f"Extracting {filename}")
                    import tarfile
                    with tarfile.open(filename, 'r:gz') as tar_ref:
                        tar_ref.extractall(temp_dir)
                
                # Find TTF files and install them
                for ttf_file in Path(temp_dir).glob('**/*.ttf'):
                    print_step(f"Installing font: {ttf_file.name}")
                    
                    # Copy to Windows Fonts directory
                    fonts_dir = os.path.join(os.environ['WINDIR'], 'Fonts')
                    font_path = os.path.join(fonts_dir, ttf_file.name)
                    
                    # Skip if the font already exists
                    if os.path.exists(font_path):
                        print(f"Font {ttf_file.name} already installed.")
                        continue
                    
                    try:
                        shutil.copy(str(ttf_file), font_path)
                        
                        # Add registry entry
                        import winreg
                        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts",
                                          0, winreg.KEY_WRITE) as key:
                            winreg.SetValueEx(key, f"{ttf_file.stem} (TrueType)", 0, winreg.REG_SZ, ttf_file.name)
                        
                        print_success(f"Installed {ttf_file.name}")
                    except Exception as e:
                        print_error(f"Failed to install {ttf_file.name}: {e}")
                        print("You may need to run this script as Administrator.")
        
        print_success("Font installation completed")
        print("\nYou may need to restart your applications or system for the fonts to be recognized.")
    
    finally:
        # Clean up
        shutil.rmtree(temp_dir)

def install_fonts_macos():
    """Install fonts on macOS."""
    print_header("Installing Devanagari Fonts for macOS")
    
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        # URLs for the Noto Sans Devanagari fonts
        font_urls = [
            # Latest Noto Sans Devanagari from Google Fonts
            "https://fonts.google.com/download?family=Noto%20Sans%20Devanagari",
            # Lohit Devanagari
            "https://releases.pagure.org/lohit/lohit-devanagari-ttf-2.95.4.tar.gz"
        ]
        
        # Download and install each font
        for url in font_urls:
            filename = os.path.join(temp_dir, os.path.basename(url))
            if download_file(url, filename):
                # Extract if it's a compressed file
                if filename.endswith('.zip'):
                    print_step(f"Extracting {filename}")
                    import zipfile
                    with zipfile.ZipFile(filename, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)
                elif filename.endswith('.tar.gz'):
                    print_step(f"Extracting {filename}")
                    import tarfile
                    with tarfile.open(filename, 'r:gz') as tar_ref:
                        tar_ref.extractall(temp_dir)
                
                # Find TTF files and install them
                for ttf_file in Path(temp_dir).glob('**/*.ttf'):
                    print_step(f"Installing font: {ttf_file.name}")
                    
                    # Create user fonts directory if it doesn't exist
                    user_fonts_dir = os.path.expanduser('~/Library/Fonts')
                    os.makedirs(user_fonts_dir, exist_ok=True)
                    
                    # Copy font to user's Fonts directory
                    font_path = os.path.join(user_fonts_dir, ttf_file.name)
                    
                    # Skip if the font already exists
                    if os.path.exists(font_path):
                        print(f"Font {ttf_file.name} already installed.")
                        continue
                    
                    try:
                        shutil.copy(str(ttf_file), font_path)
                        print_success(f"Installed {ttf_file.name}")
                    except Exception as e:
                        print_error(f"Failed to install {ttf_file.name}: {e}")
        
        print_success("Font installation completed")
        print("\nYou may need to restart your applications for the fonts to be recognized.")
    
    finally:
        # Clean up
        shutil.rmtree(temp_dir)

def install_fonts_linux():
    """Install fonts on Linux."""
    print_header("Installing Devanagari Fonts for Linux")
    
    # Try to detect package manager
    package_managers = {
        "apt-get": "sudo apt-get update && sudo apt-get install -y fonts-noto-cjk fonts-noto-hinted fonts-noto-extra fonts-lohit-deva",
        "dnf": "sudo dnf install -y google-noto-sans-devanagari-fonts lohit-devanagari-fonts",
        "pacman": "sudo pacman -Sy ttf-noto-fonts ttf-indic-otf",
        "zypper": "sudo zypper install -y noto-sans-devanagari-fonts"
    }
    
    # Try to detect which package manager is available
    pm_found = False
    for pm, cmd in package_managers.items():
        success, _ = run_command(["which", pm])
        if success:
            print_step(f"Detected package manager: {pm}")
            print_step(f"Running: {cmd}")
            success, output = run_command(cmd, shell=True)
            if success:
                print_success(f"Successfully installed fonts using {pm}")
            else:
                print_error(f"Failed to install fonts using {pm}")
                print(output)
            pm_found = True
            break
    
    if not pm_found:
        print_error("Could not detect your package manager. Let's try manual installation.")
        
        # Manual installation
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            
            # URLs for the Noto Sans Devanagari fonts
            font_urls = [
                # Latest Noto Sans Devanagari from Google Fonts
                "https://fonts.google.com/download?family=Noto%20Sans%20Devanagari",
                # Lohit Devanagari
                "https://releases.pagure.org/lohit/lohit-devanagari-ttf-2.95.4.tar.gz"
            ]
            
            # Download and install each font
            for url in font_urls:
                filename = os.path.join(temp_dir, os.path.basename(url))
                if download_file(url, filename):
                    # Extract if it's a compressed file
                    if filename.endswith('.zip'):
                        print_step(f"Extracting {filename}")
                        import zipfile
                        with zipfile.ZipFile(filename, 'r') as zip_ref:
                            zip_ref.extractall(temp_dir)
                    elif filename.endswith('.tar.gz'):
                        print_step(f"Extracting {filename}")
                        import tarfile
                        with tarfile.open(filename, 'r:gz') as tar_ref:
                            tar_ref.extractall(temp_dir)
                    
                    # Find TTF files and install them
                    for ttf_file in Path(temp_dir).glob('**/*.ttf'):
                        print_step(f"Installing font: {ttf_file.name}")
                        
                        # Create user fonts directory if it doesn't exist
                        user_fonts_dir = os.path.expanduser('~/.local/share/fonts')
                        os.makedirs(user_fonts_dir, exist_ok=True)
                        
                        # Copy font to user's fonts directory
                        font_path = os.path.join(user_fonts_dir, ttf_file.name)
                        
                        # Skip if the font already exists
                        if os.path.exists(font_path):
                            print(f"Font {ttf_file.name} already installed.")
                            continue
                        
                        try:
                            shutil.copy(str(ttf_file), font_path)
                            print_success(f"Installed {ttf_file.name}")
                        except Exception as e:
                            print_error(f"Failed to install {ttf_file.name}: {e}")
            
            # Update font cache
            print_step("Updating font cache")
            run_command(["fc-cache", "-f", "-v"])
            
            print_success("Font installation completed")
            print("\nYou may need to restart your applications for the fonts to be recognized.")
        
        finally:
            # Clean up
            shutil.rmtree(temp_dir)

def main():
    """Main function."""
    print_header("Devanagari Font Installer")
    
    # Detect operating system
    system = platform.system()
    print(f"Detected operating system: {system}")
    
    if system == "Windows":
        install_fonts_windows()
    elif system == "Darwin":  # macOS
        install_fonts_macos()
    elif system == "Linux":
        install_fonts_linux()
    else:
        print_error(f"Unsupported operating system: {system}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())