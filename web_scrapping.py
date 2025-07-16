from selenium import webdriver
import time
SLEEP_TIME = 2
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import re


options = webdriver.ChromeOptions
options.add_argument("--start-maximized")  

driver = webdriver.Chrome(options)

driver.get("https://books.toscrape.com/")
time.sleep(SLEEP_TIME)

category_elements_xpath = "//a[contains(text(),'Travel') or contains(text(),'Nonfiction')]"

category_elements = driver.find_elements(By.XPATH,category_elements_xpath)


category_urls = [element.get_attribute("href") for element in category_elements]
print(category_urls)

driver.get(category_urls[0])
time.sleep(SLEEP_TIME)


book_element_xpath = "//div[@class = 'image_container']//a"

book_elements = driver.find_elements(By.XPATH,book_element_xpath)

book_urls = [element.get_attribute("href") for element in book_elements]

print(book_urls)
print(len(book_urls))


MAX_PAGINATION = 3                          
category_url = category_urls[0]
books_urls = []


for i in range(1, MAX_PAGINATION + 1):

    page_url = (category_url if i == 1
                else category_url.replace("index", f"page-{i}"))

    driver.get(page_url)
    time.sleep(SLEEP_TIME)

    
    elements = driver.find_elements(By.XPATH, book_element_xpath)

    if not elements:
        break

    page_links = [el.get_attribute("href") for el in elements]
    book_urls.extend(page_links)


    driver.get(book_urls[0])
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

     


       


    


