import time
from datetime import datetime
from parser import pages_list_parse, next_page, page_parse

link_url = 'https://www.avito.ru/ufa/gotoviy_biznes'
urls_list = []

def main():
    pages_list_parse(link_url, urls_list)
    u = link_url
    while next_page(u):
        time.sleep(60)
        u = next_page(u)
        print(u)
        time.sleep(60)
        pages_list_parse(u, urls_list)
        time.sleep(60)

    print(len(urls_list))

    with open(f'url-list-{datetime.now()}.txt', 'w+') as f:
        for items in urls_list:
            f.write('%s\n' % items)
        print("File written successfully")
    f.close()

    for u in urls_list:
        time.sleep(60)
        page_parse(u)

if __name__ == "__main__":
    main()