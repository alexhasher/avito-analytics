from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
from datetime import datetime, timedelta
from config import user, password, host, db_name, proxy_username, proxy_port, proxy_password, proxy_address
import pymysql

proxy_url = f"http://{proxy_username}:{proxy_password}@{proxy_address}:{proxy_port}"
seleniumwire_options = {
    "proxy": {
        "http": proxy_url,
        "https": proxy_url
    },
}

def pages_list_parse(link_url, urls_list):

    options = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)  # без картинок
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")  # disable automation mode
    service = Service(executable_path='./chromedriver')
    driver = webdriver.Chrome(service=service, seleniumwire_options=seleniumwire_options, options=options)
    driver.maximize_window()
    try:
        driver.set_page_load_timeout(60)
        driver.get(url=link_url)
        elements = driver.find_elements(By.XPATH, "//div/div/div[2]/div[2]/div/a")
        for element in elements:
            urls_list.append(element.get_attribute('href'))
        return urls_list
    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        time.sleep(1)
        driver.quit()

def next_page(link_url):
    options = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)  # без картинок
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")  # disable automation mode
    service = Service(executable_path='./chromedriver')
    driver = webdriver.Chrome(service=service, seleniumwire_options=seleniumwire_options, options=options)
    driver.maximize_window()
    try:
        driver.set_page_load_timeout(60)
        driver.get(url=link_url)
        np = driver.find_element(By.XPATH, "//a[@data-marker='pagination-button/nextPage']").get_attribute('href')
        return np
    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        time.sleep(1)
        driver.quit()

def pars_datetime(string):
    date_list = string.split()
    if date_list[0] == 'сегодня':
        pdate = datetime.now().date()
    elif date_list[0] == 'вчера':
        pdate = (datetime.now().date()-timedelta(days=1))
    else:
        month = date_list[1]
        match month:
            case "июля"     : month_int = 7
            case "августа"  : month_int = 8
            case "сентября" : month_int = 9
            case "октября"  : month_int = 10
            case "ноября"   : month_int = 11
            case "декабря"  : month_int = 12
            case "января"   : month_int = 1
            case "февраля"  : month_int = 2
            case "марта"    : month_int = 3
            case "апреля"   : month_int = 4
            case "май"      : month_int = 5
            case "июнь"     : month_int = 6
        if (datetime.now().month - month_int) < 0:
            year_int = datetime.now().year - 1
        else:
            year_int = datetime.now().year
        pdate = datetime(year_int, month_int, int(date_list[0]))
    return pdate

def page_parse(url2, dbase_name):
    options = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)  # без картинок
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")  # disable automation mode
    service = Service(executable_path='./chromedriver')
    driver = webdriver.Chrome(service=service, seleniumwire_options=seleniumwire_options, options=options)
    driver.maximize_window()
    # time.sleep(10)
    try:
        driver.set_page_load_timeout(60)
        driver.get(url=url2)
        url = url2.strip()
        print((url))
        title = driver.find_element(By.TAG_NAME, "H1").text
        print(title)
        category = driver.find_elements(By.XPATH, "//a[@class='breadcrumbs-link-Vr4Nc']")[3].text
        print(category)
        views_all = driver.find_element(By.XPATH, "//span[@data-marker='item-view/total-views']").text.split()[0]
        print(views_all)
        views_today = driver.find_element(By.XPATH, "//span[@data-marker='item-view/today-views']").text.split()[0].replace('(+', '')
        print(views_today)
        row_date = driver.find_element(By.XPATH, "//span[@data-marker='item-view/item-date']").text.strip('· ')
        print(row_date)
        publish_date = pars_datetime(row_date)
        print(publish_date)
        ## Экстра сбор данных
        description = driver.find_element(By.XPATH, "//div[@data-marker='item-view/item-description']").text
        print(description)
        price = driver.find_element(By.XPATH, "//span[@data-marker='item-view/item-price']").get_attribute('content')
        print(price)
        status = True


        #Занесение данных в базу SQL
        try:
            connection = pymysql.connect(
                host=host,
                port=3306,
                user=user,
                password=password,
                database=db_name,
                cursorclass=pymysql.cursors.DictCursor
            )
            print("Успешное соединение с", db_name)
            try:
                with connection.cursor() as cursor:
                    insert_query = f"INSERT INTO `{dbase_name}` (url, title, category, views_all, views_today, publish_date, description, price, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"
                    cursor.execute(insert_query, (url, title, category, views_all, views_today, publish_date, description, price, status))
                    connection.commit()
            finally:
                connection.close()
        except Exception as ex:
            print(ex)
            print("Не удалось установить соединение с", db_name)
    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        time.sleep(1)
        driver.quit()

# li = []
# with open("url-list-2024-08-12 20:59:28.411259.txt", "r") as file:
#     li.append(file.readline())
# for i in li:
#     page_parse(i)
#     time.sleep(30)
#
# # page_parse('https://avito.ru/ufa/gotoviy_biznes/nuzhen_investor_v_predpriyatie_4314834247')