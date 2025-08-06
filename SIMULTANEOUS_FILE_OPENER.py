#!/usr/bin/env python3
"""
SIMULTANEOUS FILE OPENER - RUNS INDEPENDENTLY FROM START
Launches file search immediately when NYC website opens
Completely independent of Genesis automation timing
"""

import os
import subprocess
import logging
import glob
import threading
import time
from pathlib import Path

# Configure logging for simultaneous file opener
sim_file_logger = logging.getLogger('simultaneous_file_opener')
sim_file_logger.setLevel(logging.INFO)

# Create separate handler to avoid conflicts
if not sim_file_logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - SIMULTANEOUS_FILE_OPENER - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    sim_file_logger.addHandler(handler)

class SimultaneousFileOpener:
    """
    File opener that runs completely independently from main automation
    Launches immediately when called, doesn't wait for anything
    """
    
    def __init__(self, search_folder_path="C:\\Users\\MLFLL\\Downloads\\n8ntest\\"):
        self.search_folder_path = search_folder_path
        self.supported_extensions = ['.txt', '.pdf', '.xlsx', '.docx', '.eml', '.xls', '.doc', '.rtf', '.csv']
        self.property_address = None
        
    def find_and_open_file_immediately(self, property_address):
        """
        Find and open file immediately - runs in separate thread
        Does not wait for any other automation to complete
        """
        try:
            sim_file_logger.info("📁 ===== SIMULTANEOUS FILE OPENER STARTING =====")
            sim_file_logger.info(f"🏠 Property address: {property_address}")
            sim_file_logger.info(f"📂 Search folder: {self.search_folder_path}")
            sim_file_logger.info("⚡ Running INDEPENDENTLY of main automation")
            
            # Ensure the folder exists
            if not os.path.exists(self.search_folder_path):
                sim_file_logger.error(f"❌ Search folder does not exist: {self.search_folder_path}")
                return False
            
            # Find matching files
            matching_files = self._find_matching_files(property_address)
            
            if not matching_files:
                sim_file_logger.info("ℹ️ No matching files found")
                sim_file_logger.info("📁 ===== SIMULTANEOUS FILE OPENER COMPLETED =====")
                return False
            
            # Open the first matching file
            if len(matching_files) == 1:
                sim_file_logger.info(f"📂 Single file found: {os.path.basename(matching_files[0])}")
            else:
                sim_file_logger.info(f"📂 Multiple files found ({len(matching_files)}), opening first:")
                for i, file_path in enumerate(matching_files):
                    sim_file_logger.info(f"   {i+1}. {os.path.basename(file_path)}")
            
            # Open the file
            success = self._open_file_with_default_app(matching_files[0])
            
            if success:
                sim_file_logger.info(f"🎉 SUCCESS: Opened {os.path.basename(matching_files[0])}")
            else:
                sim_file_logger.error("❌ Failed to open file")
            
            sim_file_logger.info("📁 ===== SIMULTANEOUS FILE OPENER COMPLETED =====")
            return success
            
        except Exception as e:
            sim_file_logger.error(f"❌ Error in simultaneous file opener: {e}")
            sim_file_logger.info("📁 ===== SIMULTANEOUS FILE OPENER COMPLETED (WITH ERROR) =====")
            return False
    
    def _find_matching_files(self, address):
        """Find files that match the address name"""
        try:
            sim_file_logger.info(f"🔍 Searching for files matching: '{address}'")
            
            matching_files = []
            
            # Search for exact matches with each supported extension
            for extension in self.supported_extensions:
                file_pattern = os.path.join(self.search_folder_path, f"{address}{extension}")
                matches = glob.glob(file_pattern)
                
                if matches:
                    matching_files.extend(matches)
                    sim_file_logger.info(f"✅ Found exact match: {matches[0]}")
            
            # Also search case-insensitive and partial matches
            for extension in self.supported_extensions:
                pattern = os.path.join(self.search_folder_path, f"*{extension}")
                all_files = glob.glob(pattern)
                
                for file_path in all_files:
                    filename = os.path.basename(file_path).lower()
                    address_lower = address.lower()
                    
                    # Check if address is contained in filename
                    if address_lower in filename and file_path not in matching_files:
                        matching_files.append(file_path)
                        sim_file_logger.info(f"✅ Found partial match: {file_path}")
            
            return matching_files
            
        except Exception as e:
            sim_file_logger.error(f"❌ Error searching for files: {e}")
            return []
    
    def _open_file_with_default_app(self, file_path):
        """Open file with Windows default application"""
        try:
            sim_file_logger.info(f"📂 Opening file: {file_path}")
            
            if not os.path.exists(file_path):
                sim_file_logger.error(f"❌ File does not exist: {file_path}")
                return False
            
            # Use Windows 'start' command to open with default application
            subprocess.run(['start', '', file_path], shell=True, check=True)
            
            sim_file_logger.info(f"✅ Successfully opened: {os.path.basename(file_path)}")
            return True
            
        except subprocess.CalledProcessError as e:
            sim_file_logger.error(f"❌ Error opening file: {e}")
            return False
        except Exception as e:
            sim_file_logger.error(f"❌ Unexpected error opening file: {e}")
            return False

# MAIN FUNCTION FOR SIMULTANEOUS EXECUTION
def launch_file_opener_immediately(property_address, search_folder="C:\\Users\\MLFLL\\Downloads\\n8ntest\\"):
    """
    Launch file opener immediately in a separate thread
    This runs completely independently of main automation
    
    Args:
        property_address (str): The property address from Airtable
        search_folder (str): Folder to search in
    
    Returns:
        threading.Thread: The thread running the file opener
    """
    try:
        sim_file_logger.info("🚀 LAUNCHING SIMULTANEOUS FILE OPENER")
        sim_file_logger.info("⚡ This runs INDEPENDENTLY of main automation")
        
        # Create file opener instance
        opener = SimultaneousFileOpener(search_folder)
        
        # Create and start thread for file opening
        file_thread = threading.Thread(
            target=opener.find_and_open_file_immediately,
            args=(property_address,),
            name="FileOpenerThread",
            daemon=True  # Dies when main program exits
        )
        
        # Start the thread immediately
        file_thread.start()
        
        sim_file_logger.info("✅ File opener thread started successfully")
        sim_file_logger.info("🔄 Main automation can continue independently")
        
        return file_thread
        
    except Exception as e:
        sim_file_logger.error(f"❌ Error launching simultaneous file opener: {e}")
        return None

# INTEGRATION FUNCTION - CALL THIS IMMEDIATELY WHEN NYC STARTS
def start_file_search_now(property_address):
    """
    Start file search immediately - call this when NYC website launches
    Does not wait for anything, runs completely independently
    
    Usage in main automation:
        # Call this RIGHT when NYC automation starts
        start_file_search_now(property_address)
    """
    try:
        sim_file_logger.info("🎯 IMMEDIATE FILE SEARCH REQUESTED")
        sim_file_logger.info(f"🏠 Address: {property_address}")
        
        # Launch immediately in separate thread
        thread = launch_file_opener_immediately(property_address)
        
        if thread:
            sim_file_logger.info("✅ File search launched successfully")
            sim_file_logger.info("🔄 Continuing with main automation...")
        else:
            sim_file_logger.error("❌ Failed to launch file search")
        
        return thread
        
    except Exception as e:
        sim_file_logger.error(f"❌ Error starting immediate file search: {e}")
        return None

# TEST FUNCTION
def test_simultaneous_opener():
    """Test the simultaneous file opener"""
    print("🧪 Testing Simultaneous File Opener")
    
    test_address = "348 East 55 Street"
    print(f"🏠 Test address: {test_address}")
    
    # Start file opener
    thread = start_file_search_now(test_address)
    
    if thread:
        print("✅ File opener started in background")
        print("🔄 Main program continues...")
        
        # Simulate main program continuing
        for i in range(5):
            print(f"⏳ Main program working... {i+1}/5")
            time.sleep(1)
        
        print("✅ Main program completed")
        print("📁 File opener runs independently")
        
        # Wait for file opener to complete (optional)
        thread.join(timeout=10)
        print("🎉 Test completed")
    else:
        print("❌ Failed to start file opener")

if __name__ == "__main__":
    test_simultaneous_opener()

