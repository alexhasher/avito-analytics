import pymysql
from config import host, user, password, db_name
from bs4 import BeautifulSoup
import requests
import time
from datetime import datetime, timedelta


#задаем заголовки к request запросам, чтобы обойти блокировки avito на робота
headers = {
  'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
  'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
  'cache-control': 'max-age=0',
  'cookie': 'srv_id=MbRXuy700w6BlqbC._6ezZ5RdWmCCVAxd9LSKireXUZ758ikmMjLDdgl5RSUAoH91xPwv98KebzmLQfS51wV-.4q80oNkQs7errTQY-_U0D1WKr4E7R5SJLJb1EBi37Cs=.web; u=32mh6l5b.11ldp3l.fhn0rsfuh6g0; v=1722879407; luri=ufa; buyer_location_id=646600; dfp_group=100; gMltIuegZN2COuSe=EOFGWsm50bhh17prLqaIgdir1V0kgrvN; uxs_uid=4f3674c0-5351-11ef-acc5-e75b699e279d; f=5.cc913c231fb04ced79a187ac14f12337e404c9a8ad2fd516e404c9a8ad2fd516e404c9a8ad2fd516e404c9a8ad2fd516d8b16176e03d2873d8b16176e03d2873d8b16176e03d2873e404c9a8ad2fd5160da5ab2fc5c813503d6c212bc3ab3fc346b8ae4e81acb9fa1a2a574992f83a9246b8ae4e81acb9fa46b8ae4e81acb9fae992ad2cc54b8aa8af305aadb1df8cebc93bf74210ee38d940e3fb81381f359178ba5f931b08c66aff38e8d292af81e50df103df0c26013a2ebf3cb6fd35a0ac71e7cb57bbcb8e0ff0c77052689da50ddc5322845a0cba1aba0ac8037e2b74f92da10fb74cac1eab2da10fb74cac1eab2da10fb74cac1eabdc5322845a0cba1a0df103df0c26013a037e1fbb3ea05095de87ad3b397f946b4c41e97fe93686ad38bc41f144dd3bd2980ebe1621c8ebff02c730c0109b9fbb5f696d4692d571cae60e498ae1c699330e28148569569b7923569110cbefb342e19d3cabfc0245fb2ebf3cb6fd35a0ac0df103df0c26013a28a353c4323c7a3aefcfb0a8b111019522b1a9c756be47f83de19da9ed218fe23de19da9ed218fe2ddb881eef125a8703b2a42e40573ac3c2a7fccdb0c19238d8fcce8ac3552f062; sx=H4sIAAAAAAAC%2F5zMza2DMAwA4F185mA78U%2ByTV6CkV6htELqBWX37tAFvhuyaHMl4fKHqVkO1yIh5KaDqHeoN3ygwvbIusW4Dj6l%2F6%2F7S%2Fx90N7leTpfAgusUMmYi4pzmgtEs2ZJRmBYQVP0wYTsmkQ5cftJRpvzGwAA%2F%2F%2FDnl%2BPtQAAAA%3D%3D; v=1722879407',
  'if-none-match': 'W/"29d561-qm/QDOoUgD0Ip/zlrWi46ytohRA"',
  'priority': 'u=0, i',
  'sec-fetch-dest': 'document',
  'sec-fetch-mode': 'navigate',
  'sec-fetch-site': 'none',
  'sec-fetch-user': '?1',
  'upgrade-insecure-requests': '1',
  'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15',
  'Referer': 'https://www.avito.ru/',
  'Origin': 'https://www.avito.ru',
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15',
  'content-type': 'text/plain;charset=UTF-8',
  'origin': 'https://www.avito.ru',
  'referer': 'https://www.avito.ru/',
  'if-modified-since': 'Tue, 30 Jul 2024 06:56:53 GMT',
  'x-requested-with': 'XMLHttpRequest',
  'x-source': 'client-browser',
  'access-control-request-headers': 'content-type,x-requested-with',
  'access-control-request-method': 'POST',
  'Content-Type': 'multipart/form-data;boundary="8578486537013887"'
}

# при необходимости подключаемся к прокси
# proxies = {
#    'https': 'http://190.158.210.102:8080'
# }

link_url = 'https://www.avito.ru/ufa/gotoviy_biznes'
urls_list = []

def pars_datetime(string):
    with open("page_offer_content.html", "r") as file:
        # soup = BeautifulSoup(file, 'html.parser')
        # publish_date = soup.find('span', {'data-marker': 'item-view/item-date'}).get_text().strip()[2:]
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

#процедура парсинга страницы, которая на выходе получет заголовок, количество просмотров сегодня, общее количество просмотров и дата публикации
def page_parse(url2):
    time.sleep(120) #задержка времени перед очередным парсингом страницы, для исключения блокировок сервера 429 - получено эксперементально
    response = requests.get(url2, headers=headers, verify=False)
    if response.status_code == 200:
        # data = []
        soup = BeautifulSoup(response.text, 'html.parser')
        url = url2.strip()
        title = soup.find("h1").get_text() #title
        category = soup.find_all('a', {'class': 'breadcrumbs-link-Vr4Nc'})[3].get_text() #category
        views_all = soup.find('span', {'data-marker': 'item-view/total-views'}).get_text().split()[0] #views_all
        views_today = soup.find('span', {'data-marker': 'item-view/today-views'}).get_text().split()[0].replace('(+', '') #views_today
        publish_date = pars_datetime(soup.find('span', {'data-marker': 'item-view/item-date'}).get_text().strip()[2:]) #publish_date

        # #Занесение данных в базу SQL
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
                insert_query = "INSERT INTO `user_data` (url, title, category, views_all, views_today, publish_date) VALUES (%s, %s, %s, %s, %s, %s);"
                cursor.execute(insert_query, (url, title, category, views_all, views_today, publish_date))
                connection.commit()
            finally:
              connection.close()
        except Exception as ex:
            print(ex)
            print("Не удалось установить соединение с", db_name)
    else:
        print('Не удалось получить контент страницы для определения значений элементов', response.status_code)

#Процедура формирования списка url из поисковой выдачи авито
def pages_list_parse(link_url, urls_list):
    time.sleep(60)
    response = requests.get(link_url, headers=headers, verify=False)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        for url in soup.find_all('a', {'data-marker': 'item-title'}):
            urls_list.append("https://avito.ru"+url['href'])
        return urls_list
    else:
        print('Не удалось получить список ссылок', response.status_code)

#Функция получения адреса последней страницы в поисковой выдачи avito
def next_page(u):
    time.sleep(60)
    response = requests.get(u, headers=headers, verify=False)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.find('a', {'data-marker': 'pagination-button/nextPage'}):
            np = "https://avito.ru"+soup.find('a', {'data-marker': 'pagination-button/nextPage'})['href']
            return np
    else:
        print('Не удалось получить контент страницы для определения наличия последней страницы', response.status_code)

def main():
    pages_list_parse(link_url, urls_list)
    u = link_url
    while next_page(u):
        u = next_page(u)
        print(u)
        time.sleep(60)
        pages_list_parse(u, urls_list)
        time.sleep(60)

    print(len(urls_list))

    with open(f'url-list.txt-{datetime.now()}', 'w+') as f:
        for items in urls_list:
            f.write('%s\n' % items)
        print("File written successfully")
    f.close()

    for u in urls_list:
        page_parse(u)

if __name__ == "__main__":
    main()