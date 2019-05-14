import time
import bs4
import re
from selenium import webdriver
import traceback
import unidecode
import io
def get_driver(driver_width=600, driver_height=300, limit=300):
    connections_attempted = 0
    while connections_attempted < limit:
        try:
            driver = webdriver.Chrome('chromedriver.exe')
            driver.set_window_size(driver_width, driver_height)
            return driver
        except Exception as e:
            connections_attempted += 1
            print('Getting driver again...')
            print('  connections attempted: {}'.format(connections_attempted))
            print('  exception message: {}'.format(e))
            traceback.print_exc()

def process_whole_page( limit=1000,
                       connections_to_attempt=30,    scrolls_to_attempt=300,
                       sleep_interval=0.01):
    url = 'https://divar.ir/tehran/%D8%AA%D9%87%D8%B1%D8%A7%D9%86/browse/%D9%85%D8%A7%D8%B4%DB%8C%D9%86-%D8%B3%D9%88%D8%A7%D8%B1%DB%8C/%D8%AE%D9%88%D8%AF%D8%B1%D9%88/%D9%88%D8%B3%D8%A7%DB%8C%D9%84-%D9%86%D9%82%D9%84%DB%8C%D9%87/'
    driver = get_driver()
    connections_attempted = 0
    while connections_attempted < connections_to_attempt:
        try:
            driver.get(url)
            soup = bs4.BeautifulSoup(driver.page_source)
            results = soup.findAll('div',{'class' : "ui card post-card"})

            all_scrolls_attempted = 0

        # If we fetch more than limit results already, we're done.
        # Otherwise, try to get more results by scrolling.
        # We give up after some number of scroll tries.
        # If we do get more results, then the scroll count resets.
            if len(results) < limit:
                scrolls_attempted = 0
                while (scrolls_attempted < scrolls_to_attempt and
                        len(results) < limit):
                    all_scrolls_attempted += 1
                    scrolls_attempted += 1

                # Scroll and parse results again.
                # The old results are still on the page, so it's fine
                # to overwrite.
                    #driver.execute_script(
                     #   "return document.body.scrollHeight")
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                    soup = bs4.BeautifulSoup(driver.page_source)
                    new_results = soup.findAll('div', {'class': "ui card post-card"})

                    if len(new_results) > len(results):
                        results = new_results
                        scrolls_attempted = 0

            print('Obtained {} results after {} scrolls'.format(
                len(results), all_scrolls_attempted))
            if len(results) > limit:
                results = results[:limit]
            return results

        except Exception as e:
            connections_attempted += 1
            print('URL failed: {}'.format(url))
            print('  connections attempted: {}'.format(connections_attempted))
            print('  exception message: {}'.format(e))
            traceback.print_exc()
            time.sleep(sleep_interval)
            driver = get_driver()


    print('URL skipped: {}'.format(url))
    return None

def extraxt_data(item):
    item = str(item)
    title_regex = re.compile(r'<\s*h2[^>]*>(.*?)<\s*/\s*h2>')
    title_list_regex = re.findall(title_regex,item)
    car_title = title_list_regex[0]
    price_regex_1 = re.compile(r'<\s*label[^>]*>(.*?)<\s*/\s*label')
    price_regex_list_1 = re.findall(price_regex_1,item)
    test = price_regex_list_1[1]
    test2 = test.split('react-text')
    price = test2[5].split(' ')[2][3:]
    if (price.__contains__('۰۰۰٫۰۰۰')):
        price = str(((int(unidecode.unidecode(price).split('.')[0]) * 1000000)))
    else:
        price = 'xxxxx'
    return [car_title,price]

x  = process_whole_page()

titles = []
prices = []
for item in x:
    test = (extraxt_data(item))
    if (test[1] != 'xxxxx'):
        titles.append(test[0])
        prices.append(test[1])

with io.open('data.txt', "w", encoding="utf-8") as f:
    for i in range(len(titles)):
        f.write(titles[i] + "\t" + prices[i] +"\n")