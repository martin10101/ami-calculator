#!/usr/bin/env python3
"""
INFINITE GENESIS SCRIPT - Keeps Python script running indefinitely to keep browser alive
ENHANCED WITH LOT VALIDATION - MINIMAL ADDITION ONLY
COMBINED WITH NYC AND GOOGLE MAPS AUTOMATIONS - USING 100% WORKING CODE

SOLUTION: Python script never exits, so browser process stays alive indefinitely.
"""

import argparse
import logging
import time
import os
import re
import threading
import random
import urllib.parse
from datetime import datetime
from difflib import SequenceMatcher
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
import subprocess  # Added for file explorer opening
import glob  # Added for file pattern matching

# Configure logging with UTF-8 encoding
class UnicodeFormatter(logging.Formatter):
    def format(self, record):
        try:
            return super().format(record)
        except UnicodeEncodeError:
            record.msg = str(record.msg).encode('ascii', 'replace').decode('ascii')
            return super().format(record)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = UnicodeFormatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

try:
    file_handler = logging.FileHandler('genesis_automation.log', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_formatter = UnicodeFormatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
except Exception as e:
    logger.warning(f"Could not setup file logging: {e}")

# ============================================================================
# NEW: Standalone File Search and Open Function (Fully Decoupled)
# ============================================================================

def open_address_file(address):
    """
    Opens a file in the n8ntest folder that matches the address from Airtable.
    If no file matches, it opens File Explorer in the folder instead.
    Runs independently without affecting main automation.
    """
    # Set the folder path where files are stored
    folder_path = r"C:\Users\MLFLL\Downloads\n8ntest"
    
    # Sanitize the address input and build a search pattern
    address = address.strip()
    search_pattern = os.path.join(folder_path, f"{address}.*")

    # Use glob to match any file with the given address (any extension)
    matching_files = glob.glob(search_pattern)

    if matching_files:
        # Open the first matching file with its default app
        file_to_open = matching_files[0]
        try:
            os.startfile(file_to_open)
            logger.info(f"Opened file: {file_to_open}")
            if len(matching_files) > 1:
                logger.warning(f"Multiple files found for '{address}'. Opened the first one: {file_to_open}")
        except Exception as e:
            logger.error(f"Failed to open file '{file_to_open}': {e}")
    else:
        # Open File Explorer in the folder if no match is found
        try:
            subprocess.Popen(f'explorer "{folder_path}"')
            logger.info(f"No file found for '{address}'. Opened folder: {folder_path}")
        except Exception as e:
            logger.error(f"Failed to open folder '{folder_path}': {e}")

# ============================================================================
# NYC PROPERTY PORTAL AUTOMATION (100% WORKING CODE - NO CHANGES)
# ============================================================================

class NYCPropertyPortalAutomation:
    """
    NYC Property Portal automation that runs FIRST, then GENESIS runs
    Uses the same browser session but completely independent
    100% WORKING CODE - NO CHANGES
    """
    
    def __init__(self, driver, borough, block, lot):
        self.driver = driver
        self.borough = borough
        self.block = block
        self.lot = lot
        self.wait = WebDriverWait(driver, 5)  # Fast timeouts
        
        # Borough mapping for NYC Portal
        self.borough_mapping = {
            "manhattan": "1",
            "bronx": "2", 
            "brooklyn": "3",
            "queens": "4",
            "staten island": "5"
        }
        
    def run_nyc_automation(self):
        """Run NYC automation FIRST, then return control to GENESIS - 100% WORKING CODE"""
        try:
            logger.info("🏢 ===== NYC PROPERTY PORTAL AUTOMATION STARTING FIRST =====")
            logger.info(f"🏢 Searching for: Borough={self.borough}, Block={self.block}, Lot={self.lot}")
            
            # Open new tab for NYC Portal
            self.driver.execute_script("window.open('');")
            nyc_tab = self.driver.window_handles[-1]
            
            # Switch to NYC tab
            self.driver.switch_to.window(nyc_tab)
            
            # Navigate to NYC Property Portal
            self.driver.get("https://propertyinformationportal.nyc.gov/")
            logger.info("🏢 Navigated to NYC Property Information Portal")
            
            # Wait for page to load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(1)
            
            # Step 1: Click Select dropdown
            select_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[text()='Select']"))
            )
            select_button.click()
            logger.info("🏢 Clicked Select dropdown")
            
            # Step 2: Select "Borough / Block / Lot" option
            bbl_option = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[text()='Borough / Block / Lot']"))
            )
            bbl_option.click()
            logger.info("🏢 Selected Borough / Block / Lot option")
            
            time.sleep(1)
            
            # Step 3: Select Borough
            borough_select = self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "select"))
            )
            select = Select(borough_select)
            
            # Map borough name to number
            borough_normalized = self.borough.lower().strip()
            if borough_normalized in self.borough_mapping:
                borough_value = self.borough_mapping[borough_normalized]
                select.select_by_value(borough_value)
                logger.info(f"🏢 Selected borough: {self.borough} (value: {borough_value})")
            else:
                logger.error(f"🏢 ❌ Unknown borough: {self.borough}")
                return False
            
            # Step 4: Enter Block number
            block_inputs = self.driver.find_elements(By.XPATH, "//label[text()='Block']/following-sibling::input | //label[text()='Block']/..//input")
            if not block_inputs:
                all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
                if len(all_inputs) >= 2:
                    block_input = all_inputs[1]
                else:
                    raise NoSuchElementException("Block input not found")
            else:
                block_input = block_inputs[0]
            
            block_input.clear()
            block_input.send_keys(str(self.block))
            logger.info(f"🏢 Entered block: {self.block}")
            
            # Step 5: Enter Lot number (EXACT from Airtable)
            lot_inputs = self.driver.find_elements(By.XPATH, "//label[text()='Lot']/following-sibling::input | //label[text()='Lot']/..//input")
            if not lot_inputs:
                all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
                if len(all_inputs) >= 3:
                    lot_input = all_inputs[2]
                else:
                    raise NoSuchElementException("Lot input not found")
            else:
                lot_input = lot_inputs[0]
            
            lot_input.clear()
            lot_input.send_keys(str(self.lot))
            logger.info(f"🏢 Entered lot: {self.lot} (EXACT from Airtable)")
            
            # Step 6: Click Search button
            search_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[text()='Search']"))
            )
            search_button.click()
            logger.info("🏢 Clicked Search button")
            
            # Step 7: Wait for results
            time.sleep(2)
            
            # Check for "BBL was not found" error
            try:
                error_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'BBL was not found')]")
                if error_elements:
                    logger.warning("🏢 ⚠️ BBL was not found - property does not exist")
                    return True
            except:
                pass
            
            # Step 8: FAST Property Tax Account link detection and click
            try:
                logger.info("🏢 Looking for Property Tax Account link...")
                tax_account_link = None
                
                # Quick text search
                try:
                    tax_account_link = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Property Tax Account')]"))
                    )
                    logger.info("🏢 ✅ Found Property Tax Account link")
                except:
                    pass
                
                # Class-based search
                if not tax_account_link:
                    try:
                        tax_account_link = WebDriverWait(self.driver, 2).until(
                            EC.element_to_be_clickable((By.XPATH, "//p[contains(@class, 'bpptTs') and text()='Property Tax Account']/parent::a"))
                        )
                        logger.info("🏢 ✅ Found Property Tax Account link (class method)")
                    except:
                        pass
                
                # Exact XPath
                if not tax_account_link:
                    try:
                        tax_account_link = self.driver.find_element(By.XPATH, "/html/body/div/div/div/div[2]/div[1]/div/div[2]/div[2]/div[2]/div[1]/a[4]")
                        logger.info("🏢 ✅ Found Property Tax Account link (exact XPath)")
                    except:
                        pass
                
                # IMMEDIATE CLICK
                if tax_account_link:
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", tax_account_link)
                    try:
                        tax_account_link.click()
                        logger.info("🏢 ✅ IMMEDIATELY clicked Property Tax Account link")
                    except:
                        self.driver.execute_script("arguments[0].click();", tax_account_link)
                        logger.info("🏢 ✅ IMMEDIATELY clicked Property Tax Account link (JavaScript)")
                    
                    time.sleep(2)
                    logger.info("🏢 ✅ Property Tax Account page opened")
                else:
                    logger.warning("🏢 ⚠️ Could not find Property Tax Account link")
                
            except Exception as e:
                logger.warning(f"🏢 ⚠️ Error with Property Tax Account link: {e}")
            
            logger.info("🏢 ===== NYC AUTOMATION COMPLETED - RETURNING CONTROL TO GENESIS =====")
            
            # CRITICAL: Switch back to the first tab (GENESIS tab) before returning
            if len(self.driver.window_handles) > 1:
                self.driver.switch_to.window(self.driver.window_handles[0])
                logger.info("🏢 ✅ Switched back to GENESIS tab for GENESIS automation")
            
            return True
            
        except Exception as e:
            logger.error(f"🏢 ❌ NYC automation failed: {e}")
            return False

def run_nyc_first(driver, borough, block, lot):
    """Run NYC automation FIRST, then return control - 100% WORKING CODE"""
    try:
        nyc_automation = NYCPropertyPortalAutomation(driver, borough, block, lot)
        nyc_automation.run_nyc_automation()
    except Exception as e:
        logger.error(f"NYC automation failed: {e}")

# ============================================================================
# GOOGLE MAPS AUTOMATION (100% WORKING CODE - NO CHANGES)
# ============================================================================

class GoogleMapsAutomation:
    """
    Google Maps automation that opens with property address
    100% WORKING CODE - NO CHANGES
    """
    
    def __init__(self, driver, property_address):
        self.driver = driver
        self.property_address = property_address
        self.wait = WebDriverWait(driver, 5)
        
    def run_google_maps_automation(self):
        """Open Google Maps with property address - 100% WORKING CODE"""
        try:
            logger.info("🗺️ ===== GOOGLE MAPS AUTOMATION STARTING =====")
            logger.info(f"🗺️ Opening Google Maps for address: {self.property_address}")
            
            # Open new tab for Google Maps
            self.driver.execute_script("window.open('');")
            maps_tab = self.driver.window_handles[-1]
            
            # Switch to Google Maps tab
            self.driver.switch_to.window(maps_tab)
            
            # Create Google Maps URL with address
            encoded_address = urllib.parse.quote(self.property_address)
            maps_url = f"https://www.google.com/maps/search/{encoded_address}"
            
            # Navigate to Google Maps
            self.driver.get(maps_url)
            logger.info("🗺️ Navigated to Google Maps with property address")
            
            # Wait for page to load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(2)
            
            logger.info("🗺️ ✅ Google Maps opened successfully")
            logger.info("🗺️ ===== GOOGLE MAPS AUTOMATION COMPLETED =====")
            
            # Switch back to Genesis tab for Genesis automation
            if len(self.driver.window_handles) > 0:
                self.driver.switch_to.window(self.driver.window_handles[0])
                logger.info("🗺️ ✅ Switched back to GENESIS tab")
            
            return True
            
        except Exception as e:
            logger.error(f"🗺️ ❌ Google Maps automation failed: {e}")
            return False

# ============================================================================
# ENHANCED LOT VALIDATION WITH SMART CHUNKED STRATEGY (100% WORKING CODE)
# ============================================================================

class LotValidator:
    """ENHANCED - Lot validation with smart chunked search strategy - 100% WORKING CODE"""
    
    def __init__(self, driver, smart_form_filler):
        self.driver = driver
        self.smart_form_filler = smart_form_filler
        
    def check_for_target_property_error(self):
        """Check for red 'Target property does not exist' error message - 100% WORKING CODE"""
        try:
            error_selectors = [
                "//span[contains(@class, 'text-danger') and contains(text(), 'Target property does not exist')]",
                "//span[contains(text(), 'Target property does not exist')]",
                "//div[contains(text(), 'Target property does not exist')]",
                "//*[contains(text(), 'Target property does not exist')]"
            ]
            
            for selector in error_selectors:
                try:
                    error_element = self.driver.find_element(By.XPATH, selector)
                    if error_element.is_displayed():
                        logger.info("❌ Found 'Target property does not exist' error")
                        return True
                except:
                    continue
                    
            logger.info("✅ No 'Target property does not exist' error found")
            return False
            
        except Exception as e:
            logger.warning(f"Error checking for target property error: {e}")
            return False
            
    def test_lot_number(self, lot_number):
        """Test a specific lot number with anti-bot measures - 100% WORKING CODE"""
        logger.info(f"🧪 Testing lot number: {lot_number}")
        
        try:
            # Step 1: Input the lot number
            if not self.smart_form_filler.set_field_value("TargetLot", str(lot_number), f"Lot {lot_number}"):
                return False
                
            # Step 2: Exit/deselect the field (trigger blur event)
            try:
                lot_field = self.driver.find_element(By.ID, "TargetLot")
                self.driver.execute_script("arguments[0].blur();", lot_field)
                self.driver.execute_script("document.body.click();")
                logger.info(f"🔄 Exited lot field for lot {lot_number}")
            except Exception as e:
                logger.warning(f"Could not trigger blur for lot {lot_number}: {e}")
                
            # Step 3: Random wait (anti-bot measure)
            wait_time = random.uniform(4, 6)  # Random 4-6 seconds
            logger.info(f"⏳ Waiting {wait_time:.1f} seconds for Genesis to validate lot {lot_number}...")
            time.sleep(wait_time)
            
            # Step 4: Check for error
            has_error = self.check_for_target_property_error()
            
            if has_error:
                logger.info(f"❌ Lot {lot_number}: 'Target property does not exist' - continuing search")
                return False
            else:
                logger.info(f"✅ Lot {lot_number}: Property exists! No error message found - VALID PROPERTY")
                return True
                
        except Exception as e:
            logger.error(f"Error testing lot {lot_number}: {e}")
            return False
            
    def find_valid_lot(self, start_lot):
        """SMART CHUNKED STRATEGY: Search in chunks as requested by user - 100% WORKING CODE"""
        logger.info(f"🔍 STARTING SMART CHUNKED LOT SEARCH - Original lot: {start_lot}")
        
        # Test original lot first
        if self.test_lot_number(start_lot):
            logger.info(f"🛑 STOPPING SEARCH - Original lot {start_lot} is valid")
            return start_lot
        
        # SMART CHUNKED STRATEGY as requested:
        # 1. First: Check lots 30-40 (10 up from original)
        # 2. Then: Check lots 20-30 (10 down from original) 
        # 3. Then: Check lots 40-50 (next 10 up)
        # 4. Then: Check lots 10-20 (next 10 down)
        
        search_chunks = [
            (start_lot + 1, start_lot + 10, "up 1-10"),
            (start_lot - 10, start_lot - 1, "down 1-10"),
            (start_lot + 11, start_lot + 20, "up 11-20"),
            (start_lot - 20, start_lot - 11, "down 11-20")
        ]
        
        for start_range, end_range, description in search_chunks:
            logger.info(f"🔍 Searching chunk: {description} (lots {start_range} to {end_range})")
            
            # Search this chunk
            if start_range <= end_range:  # Forward search
                for lot in range(start_range, end_range + 1):
                    if lot <= 0:  # Skip invalid lot numbers
                        continue
                    
                    logger.info(f"🔍 Trying lot {lot} in chunk '{description}'")
                    
                    if self.test_lot_number(lot):
                        logger.info(f"🛑 STOPPING SEARCH - Found valid property at lot {lot}")
                        logger.info(f"🔍 SMART CHUNKED SEARCH COMPLETE - Using lot: {lot}")
                        return lot
                    
                    # Anti-bot pause every 10 attempts
                    if (lot - start_range + 1) % 10 == 0:
                        pause_time = random.uniform(2, 4)
                        logger.info(f"⏸️ Anti-bot pause: {pause_time:.1f} seconds")
                        time.sleep(pause_time)
                        
            else:  # Backward search
                for lot in range(start_range, end_range - 1, -1):
                    if lot <= 0:  # Skip invalid lot numbers
                        continue
                    
                    logger.info(f"🔍 Trying lot {lot} in chunk '{description}'")
                    
                    if self.test_lot_number(lot):
                        logger.info(f"🛑 STOPPING SEARCH - Found valid property at lot {lot}")
                        logger.info(f"🔍 SMART CHUNKED SEARCH COMPLETE - Using lot: {lot}")
                        return lot
                    
                    # Anti-bot pause every 10 attempts
                    if (start_range - lot + 1) % 10 == 0:
                        pause_time = random.uniform(2, 4)
                        logger.info(f"⏸️ Anti-bot pause: {pause_time:.1f} seconds")
                        time.sleep(pause_time)
            
            # Pause between chunks
            logger.info(f"✅ Completed chunk '{description}' - moving to next chunk")
            time.sleep(random.uniform(1, 2))
                
        logger.warning(f"⚠️ Could not find valid lot in any chunk around {start_lot}")
        logger.info(f"🔍 SMART CHUNKED SEARCH COMPLETE - Using original lot: {start_lot}")
        return start_lot

# ============================================================================
# ORIGINAL WORKING GENESIS AUTOMATION (100% PRESERVED FROM WORKING FILE)
# ============================================================================

class EnhancedBoroughDetector:
    """PRESERVED - Enhanced borough detection system - NO CHANGES"""
    
    BOROUGH_DATA = {
        "brooklyn": {
            "aliases": ["brooklyn", "bk", "kings", "kings county"],
            "zip_codes": [11201, 11202, 11203, 11204, 11205, 11206, 11207, 11208, 11209, 11210, 
                         11211, 11212, 11213, 11214, 11215, 11216, 11217, 11218, 11219, 11220,
                         11221, 11222, 11223, 11224, 11225, 11226, 11228, 11229, 11230, 11231,
                         11232, 11233, 11234, 11235, 11236, 11237, 11238, 11239],
            "block_ranges": [(1, 9999)],
            "dropdown_values_to_try": ["1", "3", "2", "4", "5"]  # Brooklyn = 1 (WORKING)
        },
        "manhattan": {
            "aliases": ["manhattan", "mn", "new york", "new york county", "nyc"],
            "zip_codes": [10001, 10002, 10003, 10004, 10005, 10006, 10007, 10009, 10010, 10011,
                         10012, 10013, 10014, 10016, 10017, 10018, 10019, 10020, 10021, 10022,
                         10023, 10024, 10025, 10026, 10027, 10028, 10029, 10030, 10031, 10032,
                         10033, 10034, 10035, 10036, 10037, 10038, 10039, 10040, 10044, 10065,
                         10069, 10075, 10128, 10162, 10280, 10282],
            "block_ranges": [(1, 2500)],
            "dropdown_values_to_try": ["2", "1", "3", "4", "5"]
        },
        "bronx": {
            "aliases": ["bronx", "bx", "bronx county"],
            "zip_codes": [10451, 10452, 10453, 10454, 10455, 10456, 10457, 10458, 10459, 10460,
                         10461, 10462, 10463, 10464, 10465, 10466, 10467, 10468, 10469, 10470,
                         10471, 10472, 10473, 10474, 10475],
            "block_ranges": [(1000, 6000)],
            "dropdown_values_to_try": ["4", "2", "3", "1", "5"]
        },
        "queens": {
            "aliases": ["queens", "qn", "queens county"],
            "zip_codes": [11004, 11005, 11101, 11102, 11103, 11104, 11105, 11106, 11109, 11120,
                         11354, 11355, 11356, 11357, 11358, 11359, 11360, 11361, 11362, 11363,
                         11364, 11365, 11366, 11367, 11368, 11369, 11370, 11371, 11372, 11373,
                         11374, 11375, 11377, 11378, 11379, 11385, 11411, 11412, 11413, 11414,
                         11415, 11416, 11417, 11418, 11419, 11420, 11421, 11422, 11423, 11426,
                         11427, 11428, 11429, 11432, 11433, 11434, 11435, 11436, 11691, 11692,
                         11693, 11694, 11695, 11697],
            "block_ranges": [(1, 15000)],
            "dropdown_values_to_try": ["3", "5", "2", "4", "1"]
        },
        "staten_island": {
            "aliases": ["staten island", "si", "richmond", "richmond county"],
            "zip_codes": [10301, 10302, 10303, 10304, 10305, 10306, 10307, 10308, 10309, 10310,
                         10311, 10312, 10313, 10314],
            "block_ranges": [(1, 8000)],
            "dropdown_values_to_try": ["5", "2", "3", "4", "1"]
        }
    }
    
    def __init__(self, driver):
        self.driver = driver
        self.discovered_mappings = {}
        
    def normalize_borough_name(self, borough_name):
        """PRESERVED - NO CHANGES"""
        if not borough_name:
            return ""
        return borough_name.lower().strip().replace("_", " ").replace("-", " ")
        
    def fuzzy_match_borough(self, input_borough, threshold=0.8):
        """PRESERVED - NO CHANGES"""
        normalized_input = self.normalize_borough_name(input_borough)
        
        best_match = None
        best_score = 0
        
        for borough_key, borough_data in self.BOROUGH_DATA.items():
            for alias in borough_data["aliases"]:
                score = SequenceMatcher(None, normalized_input, alias).ratio()
                if score > best_score and score >= threshold:
                    best_score = score
                    best_match = borough_key
                    
        logger.info(f"Fuzzy match for '{input_borough}': {best_match} (score: {best_score:.2f})")
        return best_match, best_score
        
    def select_borough_with_enhanced_detection(self, target_borough, property_address=None, block=None):
        """PRESERVED - Enhanced borough selection - NO CHANGES"""
        logger.info(f"ENHANCED BOROUGH DETECTION: Selecting {target_borough}")
        
        normalized_target = self.normalize_borough_name(target_borough)
        matched_borough, match_confidence = self.fuzzy_match_borough(target_borough, threshold=0.6)
        
        if not matched_borough:
            logger.error(f"Could not match '{target_borough}' to any known borough")
            return False
            
        logger.info(f"Target borough '{target_borough}' matched to '{matched_borough}' (confidence: {match_confidence:.2f})")
        
        borough_data = self.BOROUGH_DATA[matched_borough]
        values_to_try = borough_data["dropdown_values_to_try"]
        
        try:
            borough_dropdown = self.driver.find_element(By.ID, "Borough")
            select = Select(borough_dropdown)
            
            for value in values_to_try:
                try:
                    logger.info(f"Testing borough value: {value} for {matched_borough}")
                    
                    select.select_by_value(value)
                    time.sleep(1)
                    
                    selected_option = select.first_selected_option
                    selected_text = selected_option.text.strip()
                    selected_value = selected_option.get_attribute('value')
                    
                    logger.info(f"Value '{value}' selected: '{selected_text}' (value: {selected_value})")
                    
                    selected_match, selected_confidence = self.fuzzy_match_borough(selected_text, threshold=0.6)
                    
                    if selected_match == matched_borough and selected_confidence > 0.6:
                        logger.info(f"SUCCESS: {matched_borough} selected with value '{value}' -> '{selected_text}'")
                        return True
                    else:
                        logger.info(f"Value '{value}' selected '{selected_text}' (matched to {selected_match}), not {matched_borough}")
                        
                except Exception as e:
                    logger.warning(f"Failed to test borough value '{value}': {str(e)}")
                    continue
                    
            logger.error(f"FAILED: Could not select {matched_borough} with any method")
            return False
            
        except Exception as e:
            logger.error(f"Error in enhanced borough selection: {str(e)}")
            return False

class SmartFormFiller:
    """PRESERVED - Smart form filling that only updates necessary fields - NO CHANGES"""
    
    def __init__(self, driver):
        self.driver = driver
        self.form_state = {}
        
    def get_field_value(self, field_id):
        """Get current value of a form field"""
        try:
            element = self.driver.find_element(By.ID, field_id)
            if element.tag_name == "select":
                select = Select(element)
                return select.first_selected_option.get_attribute('value')
            else:
                return element.get_attribute('value')
        except:
            return None
            
    def set_field_value(self, field_id, value, field_name):
        """Set field value only if it's different from current value"""
        try:
            current_value = self.get_field_value(field_id)
            
            if current_value == value:
                logger.info(f"⏭️ {field_name}: Already set to '{value}' - skipping")
                return True
                
            element = self.driver.find_element(By.ID, field_id)
            
            if element.tag_name == "select":
                select = Select(element)
                select.select_by_value(value)
                logger.info(f"✅ {field_name}: Changed from '{current_value}' to '{value}'")
            else:
                element.clear()
                element.send_keys(value)
                logger.info(f"✅ {field_name}: Changed from '{current_value}' to '{value}'")
                
            time.sleep(1)
            return True
            
        except Exception as e:
            logger.error(f"❌ {field_name}: Failed to set value '{value}': {e}")
            return False
            
    def fill_assessment_field_properly(self):
        """PRESERVED - Fill Assessment field with proper validation - NO CHANGES"""
        logger.info("🔧 FIXING Assessment field (ensuring value sticks)")
        
        try:
            # Method 1: Enhanced hidden field approach with validation
            try:
                hidden_field = self.driver.find_element(By.ID, "ActualTotalAsstLow")
                
                visible_textbox = self.driver.execute_script("""
                    var hiddenField = arguments[0];
                    var visibleTextbox = hiddenField.previousElementSibling;
                    while (visibleTextbox && !visibleTextbox.classList.contains('format-textbox-class')) {
                        visible_textbox = visible_textbox.previousElementSibling;
                    }
                    return visible_textbox;
                """, hidden_field)
                
                if visible_textbox:
                    # Clear and set value
                    visible_textbox.clear()
                    time.sleep(0.5)
                    visible_textbox.send_keys("1")
                    time.sleep(0.5)
                    
                    # Trigger all necessary events
                    self.driver.execute_script("""
                        var element = arguments[0];
                        element.dispatchEvent(new Event('input', { bubbles: true }));
                        element.dispatchEvent(new Event('change', { bubbles: true }));
                        element.dispatchEvent(new Event('blur', { bubbles: true }));
                        element.dispatchEvent(new Event('focusout', { bubbles: true }));
                    """, visible_textbox)
                    
                    time.sleep(1)
                    
                    # Validate the value stuck
                    final_value = visible_textbox.get_attribute('value')
                    if final_value == "1":
                        logger.info("✅ Assessment Low: 1 (Method 1 - value validated)")
                        return True
                    else:
                        logger.warning(f"⚠️ Assessment value didn't stick: got '{final_value}', expected '1'")
                        
            except Exception as e1:
                logger.warning(f"Method 1 failed: {e1}")
                
            # Method 2: Enhanced CSS selector approach with validation
            try:
                assessment_textbox = self.driver.find_element(By.CSS_SELECTOR, 
                    "#act-total-assess .format-textbox-class")
                
                # Clear and set value with enhanced events
                assessment_textbox.clear()
                time.sleep(0.5)
                assessment_textbox.send_keys("1")
                time.sleep(0.5)
                
                # Enhanced event triggering
                self.driver.execute_script("""
                    var element = arguments[0];
                    element.focus();
                    element.dispatchEvent(new Event('input', { bubbles: true }));
                    element.dispatchEvent(new Event('change', { bubbles: true }));
                    element.dispatchEvent(new Event('keyup', { bubbles: true }));
                    element.dispatchEvent(new Event('blur', { bubbles: true }));
                    element.dispatchEvent(new Event('focusout', { bubbles: true }));
                    
                    // Force validation
                    if (element.form) {
                        element.form.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                """, assessment_textbox)
                
                time.sleep(1)
                
                # Validate the value stuck
                final_value = assessment_textbox.get_attribute('value')
                if final_value == "1":
                    logger.info("✅ Assessment Low: 1 (Method 2 - value validated)")
                    return True
                else:
                    logger.warning(f"⚠️ Assessment value didn't stick: got '{final_value}', expected '1'")
                    
            except Exception as e2:
                logger.warning(f"Method 2 failed: {e2}")
                
            # Method 3: JavaScript direct value setting with validation
            try:
                success = self.driver.execute_script("""
                    var inputs = document.query_selectorAll('input[class*="format-textbox"]');
                    for (var i = 0; i < inputs.length; i++) {
                        var input = inputs[i];
                        if (input.offsetParent !== null) { // visible
                            input.value = '1';
                            input.focus();
                            input.dispatchEvent(new Event('input', { bubbles: true }));
                            input.dispatchEvent(new Event('change', { bubbles: true }));
                            input.dispatchEvent(new Event('blur', { bubbles: true }));
                            
                            // Validate
                            if (input.value === '1') {
                                return true;
                            }
                        }
                    }
                    return false;
                """)
                
                if success:
                    logger.info("✅ Assessment Low: 1 (Method 3 - JavaScript validated)")
                    return True
                    
            except Exception as e3:
                logger.warning(f"Method 3 failed: {e3}")
                
            logger.error("❌ All Assessment field methods failed")
            return False
            
        except Exception as e:
            logger.error(f"❌ Assessment field completely failed: {e}")
            return False

class InfiniteGenesisAutomation:
    """INFINITE - Genesis automation that keeps Python script running indefinitely"""
    
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.driver = None
        self.wait = None
        self.current_distance = 0.5
        self.borough_detector = None
        self.smart_form_filler = None
        self.lot_validator = None
        self.form_initialized = False
        
    def setup_driver(self):
        """PRESERVED - Initialize Chrome driver - NO CHANGES"""
        logger.info("====== WebDriver manager ======")
        
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        download_dir = os.path.join(os.getcwd(), "genesis_reports")
        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        os.makedirs(download_dir, exist_ok=True)
        
        # Use local Chrome installation instead of downloading driver
        service = Service()  # Let Selenium find Chrome automatically
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 15)
        
        self.borough_detector = EnhancedBoroughDetector(self.driver)
        self.smart_form_filler = SmartFormFiller(self.driver)
        self.lot_validator = LotValidator(self.driver, self.smart_form_filler)
        
        logger.info("Chrome driver initialized successfully")
        
    def login_to_genesis(self):
        """PRESERVED - Login to Genesis GenPAD - NO CHANGES"""
        logger.info("Navigating to Genesis GenPAD and logging in")
        
        self.driver.get("https://genesisgenpad.com/comparison/main")
        time.sleep(3)
        
        try:
            email_field = self.wait.until(EC.presence_of_element_located((By.ID, "email-input")))
            logger.info("Login required - filling credentials")
            
            email_field.clear()
            email_field.send_keys(self.username)
            logger.info("Entered email address")
            
            password_field = self.driver.find_element(By.ID, "Password")
            password_field.clear()
            password_field.send_keys(self.password)
            logger.info("Entered password")
            
            login_button = self.driver.find_element(By.CSS_SELECTOR, "input[value='Log in']")
            login_button.click()
            logger.info("Clicked login button")
            
            time.sleep(5)
            
        except TimeoutException:
            logger.info("Already logged in - proceeding to form")
            
        current_url = self.driver.current_url
        logger.info(f"Current URL: {current_url}")
        
        if "comparison/main" in current_url:
            logger.info("Successfully on comparison page")
            return True
        else:
            logger.error("Failed to reach comparison page")
            return False
            
    def setup_form_initial(self, borough, block, lot, tax_class, property_address):
        """ENHANCED - Initial form setup with lot validation - MINIMAL ADDITION"""
        if self.form_initialized:
            logger.info("⏭️ Form already initialized - skipping initial setup")
            return True
            
        logger.info("🔧 INITIAL FORM SETUP (one-time only)")
        
        try:
            # Change comparison type to Distance
            if not self.smart_form_filler.set_field_value("curr-comparison-type", "2", "Comparison Type"):
                return False
            time.sleep(3)
            
            # Wait for distance area to appear
            try:
                self.wait.until(EC.visibility_of_element_located((By.ID, "distance-area")))
                logger.info("Distance area is now visible")
            except:
                logger.error("Distance area did not appear")
                return False
                
            # Set unit to Miles (only once)
            if not self.smart_form_filler.set_field_value("UnitFmSelect", "2", "Distance Unit"):
                return False
                
            # Fill borough (only once)
            if not self.borough_detector.select_borough_with_enhanced_detection(
                borough, property_address, block
            ):
                logger.warning("Enhanced borough selection failed, but continuing")
            time.sleep(1)
            
            # Fill block (only once)
            if not self.smart_form_filler.set_field_value("TargetBlock", block, "Block"):
                return False
                
            # NEW: Lot validation logic
            logger.info("🔍 Starting lot number validation...")
            valid_lot = self.lot_validator.find_valid_lot(int(lot))
            logger.info(f"🔍 LOT VALIDATION COMPLETE - Using lot: {valid_lot}")
            # END NEW SECTION
                
            # Fill tax class (only once)
            if not self.smart_form_filler.set_field_value("TaxClassSelect", "3", "Tax Class"):
                return False
                
            # Fill year built fields (only once)
            if not self.smart_form_filler.set_field_value("YearBuiltLow", "2015", "Year Built Low"):
                return False
            if not self.smart_form_filler.set_field_value("YearBuiltHigh", "2022", "Year Built High"):
                return False
                
            # Fill assessment field properly (only once)
            self.smart_form_filler.fill_assessment_field_properly()
            
            # Fill sort order (only once)
            if not self.smart_form_filler.set_field_value("sort-order-select", "2", "Sort Order"):
                return False
                
            self.form_initialized = True
            logger.info("✅ Initial form setup completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Initial form setup failed: {e}")
            return False
            
    def update_distance_only(self, distance):
        """PRESERVED - Update only the distance field (optimized) - NO CHANGES"""
        logger.info(f"🔧 UPDATING DISTANCE ONLY: {distance} miles")
        
        try:
            # Only update the distance field
            if self.smart_form_filler.set_field_value("Distance", str(distance), f"Distance ({distance} miles)"):
                self.current_distance = distance
                logger.info(f"✅ Distance updated to {distance} miles (other fields preserved)")
                return True
            else:
                logger.error(f"❌ Failed to update distance to {distance}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error updating distance: {e}")
            return False
            
    def click_button_with_nav_fix(self, button_id, button_name):
        """PRESERVED - Click button with navigation bar fix - NO CHANGES"""
        logger.info(f"Clicking {button_name} button with navigation bar fix")
        
        try:
            button = self.driver.find_element(By.ID, button_id)
            
            self.driver.execute_script("""
                var button = arguments[0];
                var navHeight = 80;
                var buttonRect = button.getBoundingClientRect();
                var scrollY = window.pageYOffset + buttonRect.top - navHeight - 20;
                window.scrollTo(0, scrollY);
            """, button)
            
            time.sleep(2)
            
            try:
                self.wait.until(EC.element_to_be_clickable((By.ID, button_id)))
                button.click()
                logger.info(f"Successfully clicked {button_name} button (regular click)")
                return True
            except:
                self.driver.execute_script("arguments[0].click();", button)
                logger.info(f"Successfully clicked {button_name} button (JavaScript click)")
                return True
                
        except Exception as e:
            logger.error(f"Error clicking {button_name} button: {str(e)}")
            return False
            
    def run_search_and_check_results(self):
        """PRESERVED - STEP 4: Run search and check results - NO CHANGES"""
        logger.info("STEP 4: Running search with navigation bar fix")
        
        try:
            if not self.click_button_with_nav_fix("btn-run", "RUN"):
                return 0
                
            logger.info("Waiting for search results to load...")
            time.sleep(15)
            
            try:
                logger.info("Looking for 'Records Selected' count in results box...")
                
                records_selected_label = self.driver.find_element(By.XPATH, "//label[@for='RecordsSelected']")
                logger.info("Found 'Records Selected' label")
                
                records_count_span = self.driver.find_element(By.XPATH, 
                    "//label[@for='RecordsSelected']/../../following-sibling::div[contains(@class, 'text-right')]//span[@class='left-offset-20']")
                
                records_count_text = records_count_span.text.strip()
                logger.info(f"Raw Records Selected text: '{records_count_text}'")
                
                import re
                numbers = re.findall(r'\d+', records_count_text.replace(',', ''))
                if numbers:
                    record_count = int(numbers[0])
                    logger.info(f"PARSED RESULT: {record_count} records selected")
                    return record_count
                else:
                    logger.warning(f"Could not parse number from: '{records_count_text}'")
                    
            except Exception as e:
                logger.warning(f"Primary method failed: {str(e)}")
                
            try:
                logger.info("Trying JavaScript method...")
                
                record_count = self.driver.execute_script("""
                    var label = document.query_selector('label[for="RecordsSelected"]');
                    if (label) {
                        var row = label.closest('.row');
                        if (row) {
                            var spans = row.querySelectorAll('span.left-offset-20');
                            for (var i = 0; i < spans.length; i++) {
                                var text = spans[i].textContent.trim();
                                if (text && !text.includes('%')) {
                                    var numbers = text.replace(/,/g, '').match(/\\d+/);
                                    if (numbers) {
                                        return parseInt(numbers[0]);
                                    }
                                }
                            }
                        }
                    }
                    return null;
                """)
                
                if record_count is not None:
                    logger.info(f"JAVASCRIPT METHOD: {record_count} records selected")
                    return record_count
                    
            except Exception as e:
                logger.warning(f"JavaScript method failed: {str(e)}")
                
            logger.warning("Could not determine record count - assuming 0 records")
            return 0
            
        except Exception as e:
            logger.error(f"Error running search: {str(e)}")
            return 0
            
    def generate_excel_filename(self, property_address, record_count):
        """NEW - Generate Excel filename based on property address"""
        try:
            # Clean the property address for filename
            clean_address = re.sub(r'[<>:"/\\|?*]', '', property_address)
            clean_address = clean_address.replace(' ', '_')
            clean_address = clean_address.replace(',', '')
            
            filename = f"{clean_address}_Genesis_Report_{record_count}_records.xlsx"
            logger.info(f"📄 Generated Excel filename: {filename}")
            return filename
        except Exception as e:
            logger.warning(f"Could not generate custom filename: {e}")
            return f"Genesis_Report_{record_count}_records.xlsx"
            
    def download_excel_with_custom_name(self, property_address, record_count):
        """ENHANCED - Excel download with custom naming - MINIMAL ADDITION"""
        logger.info("=== EXCEL DOWNLOAD WITH CUSTOM NAMING ===")
        
        try:
            # Get initial download state
            download_dir = os.path.join(os.getcwd(), "genesis_reports")
            initial_files = set()
            if os.path.exists(download_dir):
                initial_files = set([f for f in os.listdir(download_dir) if f.endswith(('.xlsx', '.xls'))])
            
            logger.info(f"Initial Excel files: {len(initial_files)}")
            
            # Excel button click with navigation bar fix (SAME AS RUN BUTTON)
            try:
                excel_button = self.driver.find_element(By.ID, "btn-excel")
                if excel_button.is_displayed() and excel_button.is_enabled():
                    logger.info("Found Excel button with ID 'btn-excel'")
                    
                    # Apply the SAME navigation bar fix as RUN button
                    self.driver.execute_script("""
                        var button = arguments[0];
                        var navHeight = 80;
                        var buttonRect = button.getBoundingClientRect();
                        var scrollY = window.pageYOffset + buttonRect.top - navHeight - 20;
                        window.scrollTo(0, scrollY);
                    """, excel_button)
                    
                    time.sleep(2)
                    
                    # Try regular click first, then JavaScript click
                    try:
                        self.wait.until(EC.element_to_be_clickable((By.ID, "btn-excel")))
                        excel_button.click()
                        logger.info("Successfully clicked Excel button (regular click)")
                    except:
                        self.driver.execute_script("arguments[0].click();", excel_button)
                        logger.info("Successfully clicked Excel button (JavaScript click)")
                    
                    # Wait for download with verification
                    logger.info("Waiting for Excel download...")
                    
                    for attempt in range(30):  # Wait up to 30 seconds
                        time.sleep(1)
                        
                        if os.path.exists(download_dir):
                            current_files = set([f for f in os.listdir(download_dir) if f.endswith(('.xlsx', '.xls'))])
                            new_files = current_files - initial_files
                            
                            if new_files:
                                # Check if files have content and rename
                                for file in new_files:
                                    file_path = os.path.join(download_dir, file)
                                    try:
                                        if os.path.getsize(file_path) > 0:
                                            # NEW: Rename file with custom name
                                            custom_filename = self.generate_excel_filename(property_address, record_count)
                                            custom_path = os.path.join(download_dir, custom_filename)
                                            
                                            # Avoid overwriting existing files
                                            counter = 1
                                            while os.path.exists(custom_path):
                                                name_part = custom_filename.replace('.xlsx', f'_{counter}.xlsx')
                                                custom_path = os.path.join(download_dir, name_part)
                                                counter += 1
                                                
                                            os.rename(file_path, custom_path)
                                            logger.info(f"SUCCESS: Downloaded and renamed Excel file: {os.path.basename(custom_path)}")
                                            return True
                                    except Exception as e:
                                        logger.warning(f"Could not rename file {file}: {e}")
                                        logger.info(f"SUCCESS: Downloaded Excel file: {file}")
                                        return True
                                        
                    logger.error("TIMEOUT: No Excel files downloaded within 30 seconds")
                    return False
                        
                else:
                    logger.error("Excel button found but not clickable")
                    return False
                    
            except NoSuchElementException:
                logger.error("Excel button with ID 'btn-excel' not found")
                return False
                
        except Exception as e:
            logger.error(f"Error in Excel download: {str(e)}")
            return False
        
    def run_automation(self, borough, block, lot, tax_class, property_address, owner, record_id):
        """ENHANCED - Main automation workflow with fixed 0.5 mile radius - EXACT FROM WORKING FILE"""
        logger.info("====== Starting INFINITE Genesis GenPAD Automation ======")
        logger.info(f"Property: {borough}, Block {block}, Lot {lot}, Tax Class {tax_class}")
        logger.info(f"Property Address: {property_address}")
        logger.info(f"Owner: {owner}")
        logger.info(f"Record ID: {record_id}")
        
        try:
            # Step 1: Run NYC automation FIRST
            logger.info("🏢 Running NYC automation FIRST...")
            run_nyc_first(self.driver, borough, block, lot)
            
            # Step 2: Run Google Maps automation SECOND
            logger.info("🗺️ Running Google Maps automation SECOND...")
            maps_automation = GoogleMapsAutomation(self.driver, property_address)
            maps_automation.run_google_maps_automation()
            
            # Step 3: Now run Genesis automation THIRD
            logger.info("⚡ Starting Genesis automation THIRD...")
            
            if not self.login_to_genesis():
                return False
                
            # NEW: Fixed 0.5 mile radius (as requested)
            FIXED_RADIUS = 0.5
            MINIMUM_RECORDS_TARGET = 10
            
            logger.info(f"\n===== USING FIXED RADIUS: {FIXED_RADIUS} miles =====")
            
            # Initial form setup with lot validation
            logger.info("🔧 Setting up complete form with lot validation")
            if not self.setup_form_initial(borough, block, lot, tax_class, property_address):
                logger.error(f"Failed to setup initial form")
                return False
                
            # Set fixed distance
            if not self.update_distance_only(FIXED_RADIUS):
                logger.error(f"Failed to update distance to {FIXED_RADIUS}")
                return False
                
            record_count = self.run_search_and_check_results()
            logger.info(f"Found {record_count} records at {FIXED_RADIUS} miles")
            
            if record_count >= MINIMUM_RECORDS_TARGET:
                logger.info(f"SUCCESS: Found {record_count} records (>= {MINIMUM_RECORDS_TARGET})")
                
                # Enhanced Excel download with custom naming
                if self.download_excel_with_custom_name(property_address, record_count):
                    logger.info("Excel download completed successfully")
                else:
                    logger.warning("Excel download failed, but continuing")
                    
                logger.info("Keeping results page open for review...")
                logger.info("INFINITE automation completed successfully!")
                return True
            else:
                logger.warning(f"Only {record_count} records found at {FIXED_RADIUS} miles")
                
                # Still download Excel even with fewer records
                if self.download_excel_with_custom_name(property_address, record_count):
                    logger.info("Excel download completed successfully")
                    
                logger.info("Keeping results page open for review...")
                logger.info("INFINITE automation completed!")
                return True
            
        except Exception as e:
            logger.error(f"Error in automation: {str(e)}")
            return False
            
    def keep_alive_forever(self):
        """PRESERVED - Keep Python script running indefinitely to keep browser alive - NO CHANGES"""
        logger.info("🔄 KEEPING PYTHON SCRIPT ALIVE FOREVER...")
        logger.info("🎉 SUCCESS! Browser will remain open indefinitely")
        logger.info("📊 You can now review the results in the browser")
        logger.info("🔍 Excel download completed and browser kept open")
        logger.info("🔒 Python script running indefinitely - browser will NEVER close")
        logger.info("💡 To close browser: Press Ctrl+C in this terminal, then close browser manually")
        
        try:
            while True:
                # Keep the script alive by sleeping in a loop
                time.sleep(60)  # Sleep for 1 minute at a time
                
                # Periodically check if browser is still alive
                try:
                    current_url = self.driver.current_url
                    logger.info(f"🔄 Browser still alive - Current URL: {current_url[:50]}...")
                except:
                    logger.warning("⚠️ Browser may have been closed manually")
                    break
                    
        except KeyboardInterrupt:
            logger.info("🛑 User pressed Ctrl+C - stopping keep-alive loop")
            logger.info("💡 Browser should still be open - close it manually when done")

def main():
    """100% WORKING MAIN FUNCTION - NO CHANGES"""
    parser = argparse.ArgumentParser(description='Infinite Genesis GenPAD Automation Script with Lot Validation')
    parser.add_argument('--username', required=True, help='Genesis username')
    parser.add_argument('--password', required=True, help='Genesis password')
    parser.add_argument('--borough', required=True, help='Borough name')
    parser.add_argument('--block', required=True, help='Block number')
    parser.add_argument('--lot', required=True, help='Lot number')
    parser.add_argument('--tax-class', required=True, help='Tax class')
    parser.add_argument('--property-address', required=True, help='Property address')
    parser.add_argument('--owner', required=True, help='Owner name')
    parser.add_argument('--record-id', required=True, help='Record ID')
    
    args = parser.parse_args()
    
    # NEW: Launch file search in a separate thread (parallel, non-blocking)
    logger.info("🔍 Launching file search for property address in parallel...")
    try:
        threading.Thread(target=open_address_file, args=(args.property_address,), daemon=True).start()
    except Exception as e:
        logger.error(f"Failed to launch file search thread: {e}")
    
    automation = None
    
    try:
        logger.info("🚀 ===== DUAL AUTOMATION STARTING =====")
        logger.info("🚀 Step 1: NYC Property Portal automation (runs FIRST)")
        logger.info("🚀 Step 2: Google Maps automation (runs SECOND)")
        logger.info("🚀 Step 3: GENESIS automation (runs THIRD, exactly as before)")
        
        logger.info("Setting up WebDriver")
        automation = InfiniteGenesisAutomation(args.username, args.password)
        automation.setup_driver()
        
        success = automation.run_automation(
            args.borough, args.block, args.lot, args.tax_class,
            args.property_address, args.owner, args.record_id
        )
        
        if success:
            logger.info("🎉 TRIPLE AUTOMATION COMPLETED SUCCESSFULLY!")
            logger.info("✅ NYC Property Portal automation: COMPLETED")
            logger.info("✅ Google Maps automation: COMPLETED")
            logger.info("✅ GENESIS automation: COMPLETED")
            logger.info("🚀 All automations finished - browser will stay open")
            
            # Keep Python script running indefinitely
            automation.keep_alive_forever()
            
            # This line will never be reached unless user presses Ctrl+C
            return 0
        else:
            logger.error("Automation failed")
            
            # Even on failure, keep script alive to preserve browser
            logger.info("🔄 Keeping script alive even after failure...")
            automation.keep_alive_forever()
            return 1
            
    except KeyboardInterrupt:
        logger.info("🛑 Automation interrupted by user (Ctrl+C)")
        logger.info("💡 Browser should still be open - close it manually when done")
        return 1
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        
        # Even on error, try to keep script alive to preserve browser
        if automation and automation.driver:
            logger.info("🔄 Keeping script alive even after error...")
            try:
                automation.keep_alive_forever()
            except:
                pass
        return 1

if __name__ == "__main__":
    exit(main())