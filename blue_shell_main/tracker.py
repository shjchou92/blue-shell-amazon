import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from blue_shell_main import db, ENV
from blue_shell_main.models import Product

def fetch_product(url):
    if ENV == 'dev':
        chrome_options = Options()
        chrome_options.headless = True
        chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--allow-running-insecure-content')
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"
        chrome_options.add_argument(f"user-agent={user_agent}")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), chrome_options=chrome_options)
    else:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)

    # Retrieve ASIN
    start = url.find('/dp/')
    end = url.find('/', start+4)
    asin = url[start+4:end]

    camel = "https://camelcamelcamel.com"
    driver.get(camel)

    camel_input = driver.find_element(By.ID, "sq")
    camel_input.send_keys(url)
    camel_input.send_keys(Keys.ENTER)

    image = driver.find_element(By.ID, "pimg").get_attribute('src')

    current_price = driver.find_element(By.CLASS_NAME, 'green').text

    camel_link = driver.find_element(By.CSS_SELECTOR, 'a.button.expanded.buy.has-tip').get_attribute('href')

    title = driver.find_element(By.XPATH, "/html/body/div[1]/div[3]/div[2]/div/div/div[2]/div[2]/div[1]/h2[2]/a").text
    last_update = driver.find_element(By.XPATH, "//*[contains(text(), 'Last update scan')]/following-sibling::td").text

    if driver.find_elements(By.XPATH, '/html/body/div[1]/div[3]/div[2]/div/div/div[5]/div/div[5]/div[1]/div/div[2]/div/div/table/tbody/tr[2]/td[2]'):
        amazon_high = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[2]/div/div/div[5]/div/div[5]/div[1]/div/div[2]/div/div/table/tbody/tr[2]/td[2]').text
        amazon_high_date = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[2]/div/div/div[5]/div/div[5]/div[1]/div/div[2]/div/div/table/tbody/tr[2]/td[3]').text
        amazon_low = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[2]/div/div/div[5]/div/div[5]/div[1]/div/div[2]/div/div/table/tbody/tr[3]/td[2]').text
        amazon_low_date = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[2]/div/div/div[5]/div/div[5]/div[1]/div/div[2]/div/div/table/tbody/tr[3]/td[3]').text
        amazon_avg = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[2]/div/div/div[5]/div/div[5]/div[1]/div/div[2]/div/div/table/tbody/tr[4]/td[2]').text
    else:
        amazon_high = None
        amazon_high_date = None
        amazon_low = None
        amazon_low_date = None
        amazon_avg = None

    if driver.find_elements(By.XPATH, "/html/body/div[1]/div[3]/div[2]/div/div/div[5]/div/div[5]/div[2]/div/div[2]/div/div/table/tbody/tr[2]/td[2]"):
        highest_price = driver.find_element(By.XPATH, "/html/body/div[1]/div[3]/div[2]/div/div/div[5]/div/div[5]/div[2]/div/div[2]/div/div/table/tbody/tr[2]/td[2]").text
        highest_price_date = driver.find_element(By.XPATH, "/html/body/div[1]/div[3]/div[2]/div/div/div[5]/div/div[5]/div[2]/div/div[2]/div/div/table/tbody/tr[2]/td[3]").text
        lowest_price = driver.find_element(By.XPATH, "/html/body/div[1]/div[3]/div[2]/div/div/div[5]/div/div[5]/div[2]/div/div[2]/div/div/table/tbody/tr[3]/td[2]").text
        lowest_price_date = driver.find_element(By.XPATH, "/html/body/div[1]/div[3]/div[2]/div/div/div[5]/div/div[5]/div[2]/div/div[2]/div/div/table/tbody/tr[3]/td[3]").text
        avg_price = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[2]/div/div/div[5]/div/div[5]/div[2]/div/div[2]/div/div/table/tbody/tr[4]/td[2]').text
    else:
        highest_price = None
        highest_price_date = None
        lowest_price = None
        lowest_price_date = None
        avg_price = None

    product = Product(
        asin=asin,
        image=image,
        title=title,
        link=url,
        camel_link=camel_link,
        current_price=current_price,
        amazon_high=amazon_high,
        amazon_high_date=amazon_high_date,
        amazon_low=amazon_low,
        amazon_low_date=amazon_low_date,
        amazon_avg=amazon_avg,
        third_high=highest_price,
        third_high_date=highest_price_date,
        third_low=lowest_price,
        third_low_date=lowest_price_date,
        third_avg=avg_price,
        last_update=last_update
    )

    db.session.add(product)
    db.session.commit()

    driver.quit()

    return product