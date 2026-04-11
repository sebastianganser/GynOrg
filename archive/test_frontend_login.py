import os
"""
Test script to verify frontend login functionality
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_frontend_login():
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("http://localhost:3000")
        
        # Wait for page to load
        wait = WebDriverWait(driver, 10)
        
        # Check if login form is present
        username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        password_field = driver.find_element(By.NAME, "password")
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        
        print("✓ Login form elements found")
        
        # Fill in credentials
        username_field.send_keys(os.environ.get("ADMIN_USERNAME", "admin"))
        password_field.send_keys(os.environ.get("ADMIN_PASSWORD", "admin"))
        
        print("✓ Credentials entered")
        
        # Submit form
        login_button.click()
        
        # Wait for redirect or success
        time.sleep(3)
        
        # Check if we're redirected to employees page or see employee content
        try:
            # Look for employee-related content
            employees_content = driver.find_element(By.XPATH, "//*[contains(text(), 'Mitarbeiter') or contains(text(), 'Employee')]")
            print("✓ Successfully logged in - employee content visible")
            return True
        except:
            # Check if we're still on login page (error case)
            if driver.find_element(By.NAME, "username"):
                print("✗ Still on login page - login failed")
                # Check for error messages
                try:
                    error_msg = driver.find_element(By.CSS_SELECTOR, ".text-red-700, .text-red-800")
                    print(f"Error message: {error_msg.text}")
                except:
                    print("No error message found")
                return False
            else:
                print("✓ Redirected away from login page")
                return True
                
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        return False
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    print("Testing frontend login...")
    success = test_frontend_login()
    print(f"Test result: {'PASSED' if success else 'FAILED'}")
