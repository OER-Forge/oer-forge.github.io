import sys
import os
import platform
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from axe_selenium_python import Axe
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService

PAGE_URL = "https://open-physics-ed-org.github.io/oer-forge/index.html"
BROWSERS = ["firefox", "chrome", "safari"]
REPORT_FILE = "a11y-macos.md"

def generate_markdown_report(violations, browser, file_handle):
    file_handle.write(f"# Accessibility Violations Report ({browser.capitalize()})\n\n")
    if not violations:
        file_handle.write("No accessibility violations found.\n")
    else:
        for i, v in enumerate(violations, 1):
            file_handle.write(f"## {i}. {v['id']}: {v['description']}\n")
            file_handle.write(f"- **Impact:** {v['impact']}\n")
            file_handle.write(f"- **Help:** [{v['help']}]({v['helpUrl']})\n")
            file_handle.write(f"- **Tags:** {', '.join(v['tags'])}\n")
            file_handle.write("### Affected Elements:\n")
            for node in v['nodes']:
                file_handle.write(f"- `{node['html']}`\n")
            file_handle.write("\n")
    file_handle.write("\n---\n\n")  # Separator between browsers

def get_driver(browser):
    try:
        if browser == "chrome":
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service)
        elif browser == "firefox":
            service = FirefoxService(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service)
        elif browser == "safari":
            driver = webdriver.Safari()
        else:
            print(f"Unknown browser: {browser}")
            return None
        return driver
    except WebDriverException as e:
        print(f"WebDriverException for {browser}: {e}")
        return None
    except Exception as e:
        print(f"Exception for {browser}: {e}")
        return None

def test_page(browser, file_handle):
    print(f"Starting {browser.capitalize()} WebDriver...")
    driver = get_driver(browser)
    if driver is None:
        print(f"{browser.capitalize()} is not available or could not be started.")
        generate_markdown_report([], browser, file_handle)
        return False

    print(f"Opening page: {PAGE_URL}")
    driver.get(PAGE_URL)
    axe = Axe(driver)
    print("Injecting axe-core JavaScript...")
    axe.inject()
    print("Running axe accessibility checks...")
    results = axe.run()
    print(f"Writing results for {browser} to {REPORT_FILE}...")
    generate_markdown_report(results["violations"], browser, file_handle)
    print("Closing WebDriver...")
    driver.quit()
    print("Checking for accessibility violations...")
    if len(results["violations"]) == 0:
        print(f"No accessibility violations found in {browser.capitalize()}.")
    else:
        print(f"Found {len(results['violations'])} accessibility violations in {browser.capitalize()}. See {REPORT_FILE} for details.")
    return True

if __name__ == "__main__":
    if platform.system() != "Darwin":
        print("This script is configured for macOS. For other platforms, please adjust the browser list and drivers.")
        sys.exit(1)
    with open(REPORT_FILE, 'w', encoding='utf-8') as file_handle:
        for browser in BROWSERS:
            print("="*40)
            test_page(browser, file_handle)