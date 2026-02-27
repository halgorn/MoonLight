#!/usr/bin/env python3
"""
MoonLight Package Manager (moonpkg)
Install and manage MoonLight packages
"""

import sys
import os
import json
import argparse
from pathlib import Path

MOONPKG_DIR = Path.home() / '.moonlight' / 'packages'
REGISTRY_URL = "https://packages.moonlight-lang.org"  # Placeholder

class PackageManager:
    """Package manager for MoonLight"""
    
    def __init__(self):
        self.packages_dir = MOONPKG_DIR
        self.ensure_dirs()
    
    def ensure_dirs(self):
        """Create necessary directories"""
        self.packages_dir.mkdir(parents=True, exist_ok=True)
    
    def list_installed(self):
        """List installed packages"""
        packages = []
        
        if not self.packages_dir.exists():
            return packages
        
        for item in self.packages_dir.iterdir():
            if item.is_dir():
                packages.append(item.name)
        
        return packages
    
    def install(self, package_name):
        """Install a package"""
        print(f"Installing {package_name}...")
        
        # Placeholder implementation
        # Real implementation would:
        # 1. Fetch from registry
        # 2. Download package
        # 3. Extract to packages_dir
        # 4. Install dependencies
        
        package_dir = self.packages_dir / package_name
        package_dir.mkdir(exist_ok=True)
        
        print(f"✓ {package_name} installed successfully")
        print(f"  Location: {package_dir}")
    
    def uninstall(self, package_name):
        """Uninstall a package"""
        print(f"Uninstalling {package_name}...")
        
        package_dir = self.packages_dir / package_name
        
        if not package_dir.exists():
            print(f"✗ Package {package_name} not found")
            return
        
        # Remove directory
        import shutil
        shutil.rmtree(package_dir)
        
        print(f"✓ {package_name} uninstalled")
    
    def search(self, query):
        """Search for packages"""
        print(f"Searching for '{query}'...")
        
        # Placeholder - would query registry
        results = [
            {"name": "moonlight-utils", "description": "Utility functions"},
            {"name": "moonlight-ai", "description": "AI helpers"},
        ]
        
        if results:
            print("\nResults:")
            for pkg in results:
                print(f"  {pkg['name']}: {pkg['description']}")
        else:
            print("No packages found")
    
    def info(self, package_name):
        """Show package info"""
        package_dir = self.packages_dir / package_name
        
        if not package_dir.exists():
            print(f"Package {package_name} not installed")
            return
        
        print(f"Package: {package_name}")
        print(f"Location: {package_dir}")
        print(f"Files:")
        
        for file in package_dir.rglob('*.gpu'):
            print(f"  - {file.name}")

def main():
    """Main CLI"""
    parser = argparse.ArgumentParser(
        description='MoonLight Package Manager',
        prog='moonpkg'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Install command
    install_parser = subparsers.add_parser('install', help='Install a package')
    install_parser.add_argument('package', help='Package name')
    
    # Uninstall command
    uninstall_parser = subparsers.add_parser('uninstall', help='Uninstall a package')
    uninstall_parser.add_argument('package', help='Package name')
    
    # List command
    subparsers.add_parser('list', help='List installed packages')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for packages')
    search_parser.add_argument('query', help='Search query')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show package info')
    info_parser.add_argument('package', help='Package name')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    pm = PackageManager()
    
    if args.command == 'install':
        pm.install(args.package)
    
    elif args.command == 'uninstall':
        pm.uninstall(args.package)
    
    elif args.command == 'list':
        packages = pm.list_installed()
        if packages:
            print("Installed packages:")
            for pkg in packages:
                print(f"  - {pkg}")
        else:
            print("No packages installed")
    
    elif args.command == 'search':
        pm.search(args.query)
    
    elif args.command == 'info':
        pm.info(args.package)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())









