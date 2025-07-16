import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
SLEEP_TIME = 2



def get_book_detail(driver,url):
    driver.get(url)
    time.sleep(SLEEP_TIME)
    content_div = driver.find_elements(By.XPATH,"//div[@class = 'content']")

    inner_html = content_div[0].get_attribute("innerHTML")

    soup = BeautifulSoup(inner_html,"html.parser")

    name_elem = soup.find("h1")
    book_name = name_elem.text

    price_elem = soup.find("p",attrs ={"class" : "price_color"})
    book_price = price_elem.text
     

    regex = re.compile('^star-rating ')
    star_elem = soup.find("p",attrs = {"class":regex})
    print(star_elem)
    book_star_count = star_elem["class"][-1]

    desc_elem = soup.find("div",attrs={"id" : "product_description"}).find_next_sibling()
    book_desc = desc_elem.text

    product_info = {}
    table_rows = soup.find("table").find_all("tr")

    for row in table_rows:
        key = row.find("th").text
        value = row.find("td").text
        product_info[key] = value

    return {
    'book_name': book_name,                   # Kitabın ismi
    'book_price': book_price,                 # Kitabın fiyatı
    'book_star_count': book_star_count,       # Yıldız sayısı (derecelendirme)
    'book_desc': book_desc,                   # Kitap açıklaması
    **product_info                            # Tablo şeklindeki tüm diğer bilgiler (örneğin: UPC, Tax, Availability...)
}



# WebDriver başlatılır ve Chrome penceresi tam ekran açılır
def initialize_driver():
    # Chrome tarayıcısı için opsiyonlar tanımlanıyor
    options = webdriver.ChromeOptions()
    # Tarayıcının ekranı tam boy açılması için argüman ekleniyor
    options.add_argument("--start-maximized")
    # Bu opsiyonlarla birlikte Chrome webdriver başlatılıyor
    driver = webdriver.Chrome(options)
    return driver

# Verilen homepage URL’sinden sadece 'Travel' ve 'Nonfiction' kategorilerinin linklerini çeker
def get_travel_and_nonfiction_category_urls(driver, url):
    # Ana sayfaya git
    driver.get(url)
    time.sleep(SLEEP_TIME)  # Sayfanın yüklenmesi bekleniyor

    # Sadece 'Travel' veya 'Nonfiction' metni içeren <a> etiketlerini bulmak için XPath
    category_elements_xpath = "//a[contains(text(),'Travel') or contains(text(),'Nonfiction')]"

    # İlgili kategori öğeleri bulunur
    category_elements = driver.find_elements(By.XPATH, category_elements_xpath)

    # Kategori linklerinin href’leri çekilir
    category_urls = [element.get_attribute("href") for element in category_elements]

    return category_urls

# Belirtilen kategori sayfasından kitap detay linklerini çeker (sayfa sayfa gezerek)
def get_book_urls(driver, url):
    MAX_PAGINATION = 3  # Maksimum gezilecek sayfa sayısı
    book_urls = []  # Kitap URL'lerini tutacak liste

    # Kitap linklerini bulmak için XPath ifadesi
    book_elements_xpath = "//div[@class='image_container']/a"

    # Sayfa numarası ile gezinilir
    for i in range(1, MAX_PAGINATION):
        # İlk sayfa ise URL değişmeden kullanılır, diğerlerinde "index" yerine "page-i" konur
        updated_url = url if i == 1 else url.replace("index", f"page-{i}")
        driver.get(updated_url)
        time.sleep(SLEEP_TIME)

        # Kitap öğeleri bulunur
        book_elements = driver.find_elements(By.XPATH, book_elements_xpath)

        # Sayfada hiç kitap yoksa (örneğin 3. sayfa yoksa) döngüden çık
        if not book_elements:
            break

        # Kitap linkleri alınır ve listeye eklenir
        temp_urls = [element.get_attribute("href") for element in book_elements]
        book_urls.extend(temp_urls)

    return book_urls

# Ana işlem fonksiyonu — tüm kategorileri ve kitapları gezip bilgileri toplar
def main():
    BASE_URL = "https://books.toscrape.com/"
    driver = initialize_driver()  # Chrome başlat

    # Travel ve Nonfiction kategorilerini al
    category_urls = get_travel_and_nonfiction_category_urls(driver, BASE_URL)

    data = []  # Kitap bilgilerini tutacak liste

    # Her kategori için:
    for cat_url in category_urls:
        # O kategoriye ait kitapları al
        book_urls = get_book_urls(driver, cat_url)

        # Her kitap için detayları al
        for book_url in book_urls:
            book_data = get_book_detail(driver, book_url)  # Bu fonksiyon tanımlı olmalı
            book_data["cat_url"] = cat_url  # Kitabın ait olduğu kategori URL’si
            data.append(book_data)  # Listeye ekle

    len(data)  # Toplam kitap sayısı

    # (Opsiyonel) pandas ayarları — DataFrame gösterimini optimize eder
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_colwidth", 40)
    pd.set_option("display.width", 2000)

    # Verileri pandas DataFrame’e çevir
    df = pd.DataFrame(data)
    return df

# Ana fonksiyon çağrılır ve çıktı yazdırılır
df = main()
print(df.head())   # İlk 5 satırı göster
print(df.shape)    # (satır, sütun) şeklinde tablo boyutunu göster
