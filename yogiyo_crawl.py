from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import re
import json

# 일부 요소가 어떨 땐 click interception이 되는 경우가 있어서 이를 처리하기 위한 함수
def click_interception_handling(element):
    exception_encountered_cnt = 0
    while True:
        try:
            time.sleep(3)
            element.click()
            break
        except Exception as e:
            if type(e).__name__ == 'ElementClickInterceptedException':
                exception_encountered_cnt += 1
                print(f'Trial {exception_encountered_cnt}: Click Intercepted')
                continue
            else:
                print('Other types of exception occurred.')
                print(type(e).__name__)


def restaurant_search_by_query(query, category, restaurant_no):
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    # options.add_argument('--headless')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36')
    driver = webdriver.Chrome(
        options = options
    )
    
    category_dict = {
        '1인분 주문': 3,
        '프랜차이즈': 4,
        '치킨': 5,
        '피자/양식': 6,
        '중국집': 7,
        '한식': 8,
        '일식/돈까스': 9,
        '족발/보쌈': 10,
        '야식': 11,
        '분식': 12,
        '카페/디저트': 13,
        '편의점/마트': 14
    }

    driver.get('https://www.yogiyo.co.kr/mobile/#/')
    driver.implicitly_wait(5)
    time.sleep(3)

    search_window = driver.find_element(By.XPATH, '//*[@id="search"]/div/form/input')
    search_window.clear()
    search_window.send_keys(query + Keys.ENTER)
    time.sleep(1)
    # 이상하게 주소 클릭하는 게 안 돼서 될 때까지 반복 돌려보자
    location = driver.find_element(By.XPATH, '//*[@id="search"]/div/form/ul/li[3]/a')
    click_interception_handling(location)

    tab = driver.find_element(By.XPATH, f'//*[@id="category"]/ul/li[{category_dict[category]}]/span')
    click_interception_handling(tab)
    time.sleep(1)

    # 1. 음식점 목록
    
    # 스크롤 맨 끝까지 내리기
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # 음식점 목록 구하기
    restaurants = [restaurant.text for restaurant in driver.find_elements(By.CLASS_NAME, 'restaurant-name')[:restaurant_no]]
    # 음식점별 세부 정보 링크
    restaurant_links = driver.find_elements(By.CSS_SELECTOR, '[ng-click="select_restaurant(restaurant, $index)"]')[:restaurant_no]
    
    # 다시 스크롤 맨 위로 올리기
    driver.execute_script("window.scrollTo(0, 0);")

    return driver, restaurants, len(restaurant_links), restaurant_links


def get_restaurant_infos(query, category):
    running_driver, restaurants, links_no, lst = restaurant_search_by_query(query = query, category = category, restaurant_no = 15)
    links_lst = lst
    infos_by_restaurant = {}

    for i in range(links_no):
        running_driver.implicitly_wait(5)
        infos = {}

        # 2. 배달 시간
        infos['delivery_time'] = running_driver.find_element(By.XPATH,
                                                f'//*[@id="content"]/div/div[4]/div/div[2]/div[{i + 1}]/div/table/tbody/tr/td[2]/div/ul/li[4]').text
        
        # 점포 링크 접속
        scroll_y_coord = 0
        while True:
            try:
                click_interception_handling(links_lst[i])
                break
            except Exception as e:
                 # 스크롤이 안 내려가서 클릭이 안 되면 클릭
                if type(e).__name__ == 'ElementClickInterceptedException':
                    scroll_y_coord += 500
                    running_driver.execute_script(f'window.scrollTo(0, {scroll_y_coord});')

        time.sleep(3)

        # 3. 배달팁
        try:
            infos['delivery_tip'] = running_driver.find_element(By.XPATH, '//*[@id="content"]/div[2]/div[2]/ng-include/div/div[2]/div[4]/span[1]').text
        except Exception as e:
            if type(e).__name__ == 'NoSuchElementException':
                infos['delivery_tip'] = None

        # 4. 최소주문금액
        infos['delivery_available_price'] = running_driver.find_element(By.XPATH, '//*[@id="content"]/div[2]/div[1]/div[1]/div[2]/ul/li[3]/span').text

        # 5. 할인 정보 - 할인 정보 없으면 '추가할인 0%'라는 텍스트가 저장됨
        infos['promotions'] = running_driver.find_element(By.XPATH, '//*[@id="content"]/div[2]/div[1]/div[1]/div[2]/ul/li[7]/span[2]').text
        
        # 6. 로고 이미지
        logo_element = running_driver.find_element(By.XPATH, '//*[@id="content"]/div[2]/div[1]/div[1]/div[2]/div[1]').get_attribute('style')
        infos['logo'] = re.findall('\"(.+?)\"', logo_element)[0]
        
        # 7. 메뉴 및 썸네일 크롤링
        menus = []
        imgs = []
        prices_dc = []
        menu_tabs = running_driver.find_elements(By.CSS_SELECTOR, 'span.menu-name')

        for button_idx in range(2, len(menu_tabs)):
            click_interception_handling(menu_tabs[button_idx])
            time.sleep(1)

            j = 1
            list_valid = True
            while list_valid:
                parent_xpath = f'//*[@id="menu"]/div/div[{button_idx + 1}]/div[2]/div/ul'
                shared_children_xpath = '/table/tbody/tr'
                try:
                    # 7-1 메뉴 크롤링
                    menus.append(running_driver.find_element(By.XPATH,
                                parent_xpath + f'/li[{j}]' + shared_children_xpath + '/td[1]/div[2]').text)

                    # 7-2 썸네일 URL 크롤링 - 썸네일 없으면 None
                    img_element = running_driver.find_element(By.XPATH,
                                                parent_xpath + f'/li[{j}]' + shared_children_xpath + '/td[2]/div').get_attribute('style')
                    img_url = re.findall('\"(.+?)\"', img_element)[0]
                    if img_url.startswith('https://'):
                        imgs.append(img_url)
                    else:
                        imgs.append(None)
                    
                    # 7-3 가격 크롤링
                    prices_dc.append(running_driver.find_element(By.XPATH,
                                     parent_xpath + f'/li[{j}]' + shared_children_xpath + '/td[1]/div[4]/span[2]').get_attribute('innerHTML'))
                    
                    j += 1
                except Exception as e:
                    if type(e).__name__ == 'NoSuchElementException':
                        list_valid = False

            infos['menus_info'] = list(zip(menus, imgs, prices_dc))
        

        # 8. 리뷰 및 별점 크롤링
        review_tab = running_driver.find_element(By.XPATH, '//*[@id="content"]/div[2]/div[1]/ul/li[2]/a')
        click_interception_handling(review_tab)

        # 리뷰 30개는 띄울 수 있도록 '더 보기' 버튼 3번 클릭
        for _ in range(3):
            try:
                running_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                view_more = running_driver.find_element(By.XPATH, '//*[@id="review"]/li[12]/a')
                click_interception_handling(view_more)
            except Exception as e: # 리뷰가 30개보다 적으면 알아서 끊어짐
                if type(e).__name__ == 'NoSuchElementException':
                    break
                else: 
                    print(type(e).__name__)
                    break

        reviews_info = []

        j = 2
        list_valid = True
        while list_valid:
            try:
                info_dict = {}
                # 8-1. 주문 메뉴 크롤링
                info_dict['menu'] = running_driver.find_element(By.XPATH, f'//*[@id="review"]/li[{j}]/div[3]').text
                # 8-2. 별점 크롤링
                rate_cnt = 0
                for k in range(1, 6):
                    star_mark = running_driver.find_element(By.XPATH, f'//*[@id="review"]/li[{j}]/div[2]/div/span[1]/span[{k}]')
                    if star_mark.get_attribute('class').split()[0] == 'full':
                        rate_cnt += 1

                info_dict['rate'] = rate_cnt

                # 8-3. 리뷰 크롤링
                info_dict['review'] = running_driver.find_element(By.XPATH, f'//*[@id="review"]/li[{j}]/p').text

                j += 1
                reviews_info.append(info_dict)
            except Exception as e:
                if type(e).__name__ == 'NoSuchElementException':
                        list_valid = False
        
        infos['reviews_info'] = reviews_info

        infos_by_restaurant[restaurants[i]] = infos
        

        # 같은 드라이버로 뒤로가기를 누른 후 다른 음식점으로 접속하려 하면 Stale Element Exception이 발생하기 때문에
        # 새 드라이버를 열고 재접속
        running_driver.close()
        if i < links_no - 1:
            running_driver, _, _, links_lst = restaurant_search_by_query(query = query, category = category, restaurant_no = 15)

    return infos_by_restaurant


if __name__ == '__main__':
    restaurant_categories = {
        '치킨': 'chicken',
        '피자/양식': 'pizza',
        '중국집': 'chinese',
        '한식': 'korean',
        '야식': 'latenight',
        '분식': 'snack'
    }

    for cat, filename in restaurant_categories.items():
        with open(f'{filename}_infos.json', 'w', encoding = 'utf-8') as f:
            json.dump(get_restaurant_infos(query = '경기스타트업캠퍼스', category = cat), f, ensure_ascii = False)