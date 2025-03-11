from LinkedinCrawler import login_to_linkedin
import time

def test_login():
    """
    Tests the LinkedIn login function with optional proxy support.

    Args:
        username (str): LinkedIn username or email.
        password (str): LinkedIn password.
        proxy (str, optional): Proxy server address in format 'IP:PORT'. Default is None.

    Returns:
        bool: True if login is successful, False otherwise.
    """
    username = "zhengkaifan73@gmail.com"
    password = "zkf20001212"

    # Optional: Use a proxy (set to None to disable)
    proxy = None  # Example: "123.45.67.89:8080"
    print("Starting LinkedIn login test...")
    
    try:
        driver = login_to_linkedin(username, password, proxy)
        
        if driver:
            print("Login test passed! Successfully logged into LinkedIn.")
            
            # Optional: Wait a few seconds for manual verification
            time.sleep(5)
            
            # Close the browser after testing
            driver.quit()
            return True
        else:
            print("Login test failed.")
            return False
    
    except Exception as e:
        print(f"Login test encountered an error: {e}")
        return False

# Example usage
if __name__ == "__main__":
    # Run the test
    success = test_login()

    if success:
        print("Test completed successfully!")
    else:
        print("Test encountered issues. Check logs above.")
