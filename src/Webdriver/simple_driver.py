import platform
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

def build_driver(timeout: int = 45) -> tuple:
    s: Service = Service(ChromeDriverManager().install())
    o: webdriver.ChromeOptions = webdriver.ChromeOptions()
    # https://github.com/garywu/google-compute-engine-selenium

    o.add_argument("--no-sandbox")
    o.add_argument("--disable-dev-shm-usage")
    
    if platform.system() == 'Windows':
        o.add_argument("--disable-popup-blocking")
        o.add_argument("--disable-extensions")
        o.add_argument("--hide-scrollbars")
        o.add_argument("--mute-audio")
        o.add_argument("--window-size=800,800")
        o.add_argument("--disable-gpu")
        o.add_argument("--mode=incognito")
        o.add_argument("--disable-infobars")
        o.add_argument("--disable-notifications")
        o.add_argument("--silent")
        o.add_argument("--disable-logging")
        o.add_argument("--log-level=3")
        o.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    
    else:
        o.add_argument("--headless")
    # https://github.com/GoogleChrome/chrome-launcher/blob/main/docs/chrome-flags-for-tools.md

    driver: webdriver.Chrome = webdriver.Chrome(service=s, options=o)
    driver.set_page_load_timeout(timeout)
    wait: WebDriverWait = WebDriverWait(driver, timeout)
    
    return driver, wait

if __name__ == '__main__':
    driver, wait = build_driver()
    driver.get('https://www.google.com')
    print(driver.title)
    driver.quit()