#!/usr/bin/env python3

import os
import sys
import json
import hashlib
import shutil
import threading
from pathlib import Path
from typing import Dict, List, Tuple
import urllib.request
import urllib.error
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

class ModSorterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft Mod Sorter")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Variables
        self.mod_folder = tk.StringVar()
        self.is_sorting = False
        self.modrinth_api = "https://api.modrinth.com/v2"
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Minecraft Mod Sorter", 
                                font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Folder selection
        folder_frame = ttk.LabelFrame(main_frame, text="Mod Folder Selection", padding="10")
        folder_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        folder_frame.columnconfigure(1, weight=1)
        
        ttk.Label(folder_frame, text="Folder:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        ttk.Entry(folder_frame, textvariable=self.mod_folder, width=50).grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(folder_frame, text="Browse...", command=self.browse_folder).grid(
            row=0, column=2, padx=(5, 0))
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=(0, 10))
        
        self.sort_button = ttk.Button(button_frame, text="Start Sorting", 
                                      command=self.start_sorting, width=20)
        self.sort_button.grid(row=0, column=0, padx=5)
        
        self.cancel_button = ttk.Button(button_frame, text="Cancel", 
                                        command=self.cancel_sorting, 
                                        state=tk.DISABLED, width=20)
        self.cancel_button.grid(row=0, column=1, padx=5)
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        progress_frame.rowconfigure(1, weight=1)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                            maximum=100, mode='determinate')
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Log output
        self.log_text = scrolledtext.ScrolledText(progress_frame, height=20, width=80, 
                                                   state=tk.DISABLED, wrap=tk.WORD)
        self.log_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select Mods Folder")
        if folder:
            self.mod_folder.set(folder)
            self.log(f"Selected folder: {folder}")
    
    def log(self, message):
        """Add message to log window"""
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def start_sorting(self):
        folder = self.mod_folder.get()
        if not folder:
            messagebox.showerror("Error", "Please select a mods folder first!")
            return
        
        if not os.path.isdir(folder):
            messagebox.showerror("Error", f"'{folder}' is not a valid folder!")
            return
        
        # Disable sort button, enable cancel
        self.sort_button.configure(state=tk.DISABLED)
        self.cancel_button.configure(state=tk.NORMAL)
        self.is_sorting = True
        
        # Clear log
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state=tk.DISABLED)
        
        # Start sorting in separate thread
        thread = threading.Thread(target=self.sort_mods_thread, args=(folder,))
        thread.daemon = True
        thread.start()
    
    def cancel_sorting(self):
        self.is_sorting = False
        self.log("\nCancelling...")
        self.status_var.set("Cancelled")
    
    def sort_mods_thread(self, folder):
        try:
            self.sort_mods(folder)
        except Exception as e:
            self.log(f"\nError: {e}")
            import traceback
            self.log(traceback.format_exc())
            self.status_var.set("Error occurred")
        finally:
            self.sort_button.configure(state=tk.NORMAL)
            self.cancel_button.configure(state=tk.DISABLED)
            self.is_sorting = False
    
    def sort_mods(self, folder):
        mod_folder = Path(folder)
        output_folder = mod_folder.parent / "sorted_mods"
        
        # Create output folders
        client_only_folder = output_folder / "client-only"
        server_only_folder = output_folder / "server-only"
        both_folder = output_folder / "both"
        unknown_folder = output_folder / "unknown"
        
        for f in [client_only_folder, server_only_folder, both_folder, unknown_folder]:
            f.mkdir(parents=True, exist_ok=True)
        
        # Find all .jar files
        jar_files = list(mod_folder.glob("*.jar"))
        
        if not jar_files:
            self.log(f"No .jar files found in {mod_folder}!")
            self.status_var.set("No mods found")
            return
        
        self.log(f"Found {len(jar_files)} mod files")
        self.log("=" * 60)
        self.status_var.set(f"Processing {len(jar_files)} mods...")
        
        stats = {
            "client": [],
            "server": [],
            "both": [],
            "unknown": []
        }
        
        for i, jar_file in enumerate(jar_files, 1):
            if not self.is_sorting:
                self.log("\nSorting cancelled by user")
                return
            
            progress = (i / len(jar_files)) * 100
            self.progress_var.set(progress)
            self.status_var.set(f"Processing {i}/{len(jar_files)}: {jar_file.name}")
            
            self.log(f"\n[{i}/{len(jar_files)}] Checking: {jar_file.name}")
            
            side, mod_info = self.get_mod_side(jar_file)
            
            # Determine target folder
            if side == "client":
                target_folder = client_only_folder
                stats["client"].append(jar_file.name)
                self.log("  > CLIENT-ONLY")
            elif side == "server":
                target_folder = server_only_folder
                stats["server"].append(jar_file.name)
                self.log("  > SERVER-ONLY")
            elif side == "both":
                target_folder = both_folder
                stats["both"].append(jar_file.name)
                self.log("  > BOTH (Client & Server)")
            else:
                target_folder = unknown_folder
                stats["unknown"].append(jar_file.name)
                self.log("  > UNKNOWN")
            
            # Copy file
            target_file = target_folder / jar_file.name
            shutil.copy2(jar_file, target_file)
            
            # Rate limiting
            time.sleep(0.5)
        
        # Show summary
        self.print_summary(stats, output_folder)
        self.progress_var.set(100)
        self.status_var.set("Done!")
        
        messagebox.showinfo("Complete", 
                           f"Sorting complete!\n\n"
                           f"Client-only: {len(stats['client'])}\n"
                           f"Server-only: {len(stats['server'])}\n"
                           f"Both: {len(stats['both'])}\n"
                           f"Unknown: {len(stats['unknown'])}\n\n"
                           f"Output folder: {output_folder}")
    
    def calculate_sha1(self, file_path: Path) -> str:
        """Calculate SHA1 hash of a file"""
        sha1 = hashlib.sha1()
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                sha1.update(chunk)
        return sha1.hexdigest()
    
    def calculate_sha512(self, file_path: Path) -> str:
        """Calculate SHA512 hash of a file"""
        sha512 = hashlib.sha512()
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                sha512.update(chunk)
        return sha512.hexdigest()
    
    def query_modrinth_by_hash(self, file_hash: str, algorithm: str = "sha1") -> Dict:
        """Query Modrinth API for mod info based on hash"""
        try:
            url = f"{self.modrinth_api}/version_file/{file_hash}?algorithm={algorithm}"
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'ModSorter/1.0')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                return data
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            raise
        except Exception:
            return None
    
    def get_mod_side(self, file_path: Path) -> Tuple[str, Dict]:
        """
        Determine the side of a mod (client, server, both)
        Returns: (side, mod_info)
        """
        # Try SHA1 first
        sha1_hash = self.calculate_sha1(file_path)
        mod_info = self.query_modrinth_by_hash(sha1_hash, "sha1")
        
        # If SHA1 doesn't work, try SHA512
        if mod_info is None:
            self.log("  SHA1 not found, trying SHA512...")
            sha512_hash = self.calculate_sha512(file_path)
            mod_info = self.query_modrinth_by_hash(sha512_hash, "sha512")
        
        if mod_info is None:
            self.log("  Not found on Modrinth")
            return "unknown", None
        
        # Get project info for more detailed information
        project_id = mod_info.get('project_id')
        if project_id:
            try:
                url = f"{self.modrinth_api}/project/{project_id}"
                req = urllib.request.Request(url)
                req.add_header('User-Agent', 'ModSorter/1.0')
                
                with urllib.request.urlopen(req, timeout=10) as response:
                    project_info = json.loads(response.read().decode())
                    mod_info['project_info'] = project_info
            except:
                pass
        
        # Analyze side information
        client_side = mod_info.get('client_side', 'unknown')
        server_side = mod_info.get('server_side', 'unknown')
        
        # If project_info is available, use it
        if 'project_info' in mod_info:
            client_side = mod_info['project_info'].get('client_side', client_side)
            server_side = mod_info['project_info'].get('server_side', server_side)
        
        self.log(f"  Client: {client_side}, Server: {server_side}")
        
        # Determine category
        if client_side in ['required', 'optional'] and server_side in ['required', 'optional']:
            return "both", mod_info
        elif client_side in ['required', 'optional'] and server_side == 'unsupported':
            return "client", mod_info
        elif server_side in ['required', 'optional'] and client_side == 'unsupported':
            return "server", mod_info
        elif client_side in ['required', 'optional']:
            return "both", mod_info
        elif server_side in ['required', 'optional']:
            return "both", mod_info
        else:
            return "unknown", mod_info
    
    def print_summary(self, stats: Dict[str, List[str]], output_folder: Path):
        """Display a summary of the sorting"""
        self.log("\n" + "=" * 60)
        self.log("SUMMARY")
        self.log("=" * 60)
        
        self.log(f"\nCLIENT-ONLY: {len(stats['client'])} mods")
        for mod in stats['client']:
            self.log(f"   - {mod}")
        
        self.log(f"\nSERVER-ONLY: {len(stats['server'])} mods")
        for mod in stats['server']:
            self.log(f"   - {mod}")
        
        self.log(f"\nBOTH (Client & Server): {len(stats['both'])} mods")
        for mod in stats['both']:
            self.log(f"   - {mod}")
        
        self.log(f"\nUNKNOWN: {len(stats['unknown'])} mods")
        for mod in stats['unknown']:
            self.log(f"   - {mod}")
        
        self.log("\n" + "=" * 60)
        self.log(f"Output folder: {output_folder}")
        self.log("=" * 60)
        
        self.log("\nNOTES:")
        self.log("   - Mods in 'both' should be on Client AND Server")
        self.log("   - Mods in 'client-only' ONLY on the Client")
        self.log("   - Mods in 'server-only' ONLY on the Server")
        self.log("   - Mods in 'unknown' were not found on Modrinth")
        self.log("     -> You need to check these manually")

def main():
    root = tk.Tk()
    app = ModSorterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
