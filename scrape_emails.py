from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

def scrape_page(driver, url):
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    
    profiles = []

    profile_xpath = '//div[contains(@class, "card card--xsmall card--inline card--stacked--small")]'

    # Wait for the elements to be present
    try:
        wait.until(EC.presence_of_all_elements_located((By.XPATH, profile_xpath)))
    except:
        print("Timed out waiting for page to load")
        return profiles
    
    # Find all divs with the specified XPath
    divs = driver.find_elements(By.XPATH, profile_xpath)

    if not divs:
        return profiles  # Return empty if no profiles found

    for div in divs:
        # Extract profile details using XPath
        profile = {}
        try:
            profile['Name'] = div.find_element(By.XPATH, './/h3[@class="text-margin-reset"]/a').text.strip()
        except:
            profile['Name'] = None
        
        try:
            profile['Title'] = div.find_element(By.XPATH, './/div[@class="card__content--subtitle"]/span').text.strip()
        except:
            profile['Title'] = None
        
        try:
            profile['Location'] = div.find_element(By.XPATH, './/li[contains(@class, "fal fa-map-marker-alt")]').text.strip()
        except:
            profile['Location'] = None
        
        try:
            profile['Phone'] = div.find_element(By.XPATH, './/a[starts-with(@href, "tel:")]').text.strip()
        except:
            profile['Phone'] = None
        
        try:
            profile['Email'] = div.find_element(By.XPATH, './/a[starts-with(@href, "mailto:")]').text.strip()
        except:
            profile['Email'] = None
        
        profiles.append(profile)

    return profiles


school = input('Enter the school name: ').replace(' ', '_')
base_url = input('Enter the base URL: ')  
url_template = base_url + '&page='  

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  

# Initialize WebDriver
driver = webdriver.Chrome(options=chrome_options)

page_number = 1
all_profiles = []
seen_names = set()

max_pages = 10
while page_number <= max_pages:
    url = f"{url_template}{page_number}#"
    print(f"Scraping page {page_number}...")
    profiles = scrape_page(driver, url)

    if not profiles:
        print("No profiles found on this page. Stopping.")
        break

    new_profiles = []
    for profile in profiles:
        name = profile.get('Name')
        if name and name not in seen_names:
            seen_names.add(name)
            new_profiles.append(profile)
    
    if not new_profiles:
        print("No new profiles found. Stopping.")
        break

    all_profiles.extend(new_profiles)
    page_number += 1

driver.quit()

df = pd.DataFrame(all_profiles)

filename = f'olemiss_profiles_{school}.xlsx'
df.to_excel(filename, index=False, engine='openpyxl')

print(f"Data has been saved to '{filename}'")


