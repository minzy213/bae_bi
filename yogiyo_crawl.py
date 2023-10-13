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
            element.click()
            time.sleep(1)
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

    # 1. 음식점 목록

    # 음식점 목록 구하기
    restaurants = [restaurant.text for restaurant in driver.find_elements(By.CLASS_NAME, 'restaurant-name')[:restaurant_no]]
    # 음식점별 세부 정보 링크
    restaurant_links = driver.find_elements(By.CSS_SELECTOR, '[ng-click="select_restaurant(restaurant, $index)"]')[:restaurant_no]

    return driver, restaurants, len(restaurant_links), restaurant_links


def get_restaurant_infos(query, category):
    running_driver, restaurants, links_no, lst = restaurant_search_by_query(query = query, category = category, restaurant_no = 15)
    links_lst = lst
    infos_by_restaurant = {}

    for i in range(links_no):
        infos = {}

        # 2. 배달 시간
        infos['delivery_time'] = running_driver.find_element(By.XPATH,
                                                f'//*[@id="content"]/div/div[4]/div/div[2]/div[{i + 1}]/div/table/tbody/tr/td[2]/div/ul/li[4]').text
        
        # 점포 링크 접속
        if i > 10:
            running_driver.execute_script('window.scrollTo(0, 300);')
        click_interception_handling(links_lst[i])
        time.sleep(3)
        
        # 3. 배달팁 - 배달팁이 없으면 '0원'으로 저장됨
        delivery_tip = running_driver.find_element(By.XPATH, '//*[@id="content"]/div[2]/div[2]/ng-include/div/div[2]/div[4]/span[1]').get_attribute('innerHTML')
        infos['delivery_tip'] = re.findall('[\d,]+원', delivery_tip)[0]

        # 4. 최소주문금액
        infos['delivery_available_price'] = running_driver.find_element(By.XPATH, '//*[@id="content"]/div[2]/div[1]/div[1]/div[2]/ul/li[3]/span').text

        # 5. 할인 정보 - 할인 정보 없으면 '추가할인 0%'라는 텍스트가 저장됨
        infos['promotions'] = running_driver.find_element(By.XPATH, '//*[@id="content"]/div[2]/div[1]/div[1]/div[2]/ul/li[2]/span').text
        
        # 6. 로고 이미지
        logo_element = running_driver.find_element(By.XPATH, '//*[@id="content"]/div[2]/div[1]/div[1]/div[2]/div[1]').get_attribute('style')
        infos['logo'] = re.findall('\"(.+?)\"', logo_element)[0]
        
        # 7. 메뉴 및 썸네일 크롤링
        menus_info_dict = {}
        menus = []
        descs = []
        imgs = []
        prices = []
        prices_dc = []

        menu_tabs = running_driver.find_elements(By.CSS_SELECTOR, '[ng-repeat="category in restaurant.menu"]')[2:]
        for menu_infos in menu_tabs:

            # 7-1 메뉴 크롤링
            for menu_element in menu_infos.find_elements(By.CSS_SELECTOR, 'div.menu-name'):
                menus.append(menu_element.get_attribute('innerHTML'))

            # 7-2. 메뉴 소개 크롤링
            for desc_element in menu_infos.find_elements(By.CLASS_NAME, 'menu-desc'):
                descs.append(desc_element.get_attribute('innerHTML'))

            # 7-3. 썸네일 크롤링
            img_elements = menu_infos.find_elements(By.CLASS_NAME, 'photo')
            for element in img_elements:
                img_attr = element.get_attribute('style') 
                filtered = re.findall('(https://.+?)\"', img_attr)
                if len(filtered) > 0:
                    img_url = filtered[0]
                else:
                    img_url = ''
                imgs.append(img_url)
            
            # 7-4. 할인 전 가격 크롤링
            for price_element in menu_infos.find_elements(By.CSS_SELECTOR, '[ng-bind="item.price|krw"]'):
                prices.append(price_element.get_attribute('innerHTML'))

            # 7-5. 할인 후 가격 크롤링
            for dc_element in menu_infos.find_elements(By.CLASS_NAME, 'color-price'):
                prices_dc.append(dc_element.get_attribute('innerHTML'))
        
        for menu, desc, img, price, price_dc in zip(menus, descs, imgs, prices, prices_dc):
            menus_info_dict[menu] = {'desc': desc, 'img': img, 'price': price, 'price_dc': price_dc}

        infos['menu'] = menus_info_dict

        # 8. 리뷰 및 별점 크롤링
        review_tab = running_driver.find_element(By.XPATH, '//*[@id="content"]/div[2]/div[1]/ul/li[2]/a')
        click_interception_handling(review_tab)

        # 리뷰 30개는 띄울 수 있도록 '더 보기' 버튼 최대 3번 클릭
        reviews = int(running_driver.find_element(By.XPATH, '//*[@id="content"]/div[2]/div[1]/ul/li[2]/a/span').text)
        
        if reviews > 10: # 더 보기 버튼은 리뷰가 10개 넘게 있을 때만 존재
            if reviews <= 30:
                clicks = (reviews - 1) // 10 # 11~20개 리뷰는 클릭 한 번, 21~30개 리뷰는 클릭 두 번
            else:
                clicks = 3 # 그보다 많은 리뷰는 클릭 세 번

            button_row = 12 # XPath 상에서의 버튼 위치 - 리뷰 더 볼 때마다 10씩 증가
            for _ in range(clicks):
                running_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                view_more = running_driver.find_element(By.XPATH, f'//*[@id="review"]/li[{button_row}]/a')
                click_interception_handling(view_more)
                button_row += 10
            

        review_ids = []
        uploaded_times = []
        ordered_menus = []
        rates = []
        review_texts = []
        review_imgs = []

        # 8-1. 리뷰어 아이디 크롤링
        for review_id in running_driver.find_elements(By.CLASS_NAME, 'review-id'):
            review_ids.append(review_id.text)

        # 8-2. 리뷰 날짜 크롤링
        for upload_time in running_driver.find_elements(By.CLASS_NAME, 'review-time'):
            uploaded_times.append(upload_time.text)

        # 8-3. 주문 메뉴 크롤링
        for orders in running_driver.find_elements(By.CLASS_NAME, 'order-items'):
            ordered_menus.append(orders.text)

        # 8-4. 별점 크롤링
        stars = running_driver.find_elements(By.CSS_SELECTOR, 'div.star-point')
        for star_area in stars:
            star = star_area.find_element(By.CSS_SELECTOR, 'span.total')
            rate = len(star.find_elements(By.CLASS_NAME, 'full'))
            rates.append(rate)

        # 8-5. 리뷰 크롤링
        reviews = running_driver.find_elements(By.CSS_SELECTOR, '[ng-show="review.comment"]')
        for review in reviews:
            review_texts.append(review.text)

        # 8-6. 리뷰 이미지 크롤링
        review_panels = running_driver.find_elements(By.CSS_SELECTOR, '.list-group-item.ng-scope')
        for panel in review_panels:
            try:
                img = panel.find_element(By.TAG_NAME, 'img').get_attribute('ng-src')
                review_imgs.append(img)
            except Exception as e:
                if type(e).__name__ == 'NoSuchElementException':
                    review_imgs.append('')

        reviews_info = [{'review_id': r_id, 'uploaded': uploaded, 'order': order, 'rate': star_rate, 'review': review_text, 'img': review_img}
                        for r_id, uploaded, order, star_rate, review_text, review_img in zip(review_ids, uploaded_times, ordered_menus, rates, review_texts, review_imgs)]
        
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
        '일식/돈까스': 'japanese',
        '족발/보쌈': 'jokbal'
    }

    for cat, filename in restaurant_categories.items():
        with open(f'{filename}_infos.json', 'w', encoding = 'utf-8') as f:
            json.dump(get_restaurant_infos(query = '경기스타트업캠퍼스', category = cat), f, ensure_ascii = False)