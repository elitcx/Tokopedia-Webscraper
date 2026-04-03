from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import pandas as pd
import time

service = Service("chromedriver.exe")
driver = webdriver.Chrome(service=service)

base_url = "https://www.tokopedia.com"
search_url = r"https://www.tokopedia.com/search?st=&q=aula%20f75"
driver.set_window_size(1300, 800)
driver.get(search_url)

list_nama, list_gambar, list_harga, list_link, list_terjual = [], [], [], [], []

max_pages = 3  # Number of pages you want to scrape
current_page = 1

while current_page <= max_pages:
    print(f"\nScraping Page {current_page}...")

    # Scroll to load content
    for i in range(1, 8):
        driver.execute_script(f"window.scrollTo(0, {i * 500})")
        time.sleep(1)
    time.sleep(2)

    content = driver.page_source
    data = BeautifulSoup(content, 'html.parser')

    for i, area in enumerate(data.find_all('div', class_="css-5wh65g"), 1):
        print(f"  Processing item {i}")
        try:
            nama = area.find('span', class_="_0T8-iGxMpV6NEsYEhwkqEg==").get_text()
            gambar = area.find('img')['src']
            harga = area.find('div', class_="_67d6E1xDKIzw+i2D2L0tjw==").get_text()
            link = area.find('a')['href']
            terjual_tag = area.find('span', class_="se8WAnkjbVXZNA8mT+Veuw==")
            terjual = terjual_tag.get_text() if terjual_tag else None

            list_nama.append(nama)
            list_gambar.append(gambar)
            list_harga.append(harga)
            list_link.append(link)
            list_terjual.append(terjual)
        except Exception as e:
            print(f"  Skipping an item due to error: {e}")
    
    # Try to go to the next page
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Laman berikutnya"]')
        if next_button.is_enabled():
            next_button.click()
            time.sleep(3)
            current_page += 1
        else:
            print("Next button is disabled. Stopping.")
            break
    except NoSuchElementException:
        print("No 'Next' button found. Finished scraping.")
        break

driver.quit()

# Save to Excel
df = pd.DataFrame({
    'Nama': list_nama,
    'Gambar': list_gambar,
    'Harga': list_harga,
    'Link': list_link,
    'Terjual': list_terjual
})

with pd.ExcelWriter('aulaf75.xlsx', engine='openpyxl') as writer:
    df.to_excel(writer, 'Sheet1', index=False)
