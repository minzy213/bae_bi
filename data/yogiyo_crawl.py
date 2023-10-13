from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import re
import json

# 가격을 정수형으로 바꾸기
def price_to_int(price_str):
    filter_won = re.findall('([\d,]+)원', price_str)[0]
    digits = ''
    for cs_str in filter_won.split(','):
        digits += cs_str
    return int(digits)


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
        infos['delivery_time'] = running_driver.find_elements(By.CLASS_NAME, 'delivery-time')[i].text
        
        # 점포 링크 접속
        if i > 10:
            running_driver.execute_script('window.scrollTo(0, 300);')
        click_interception_handling(links_lst[i])
        time.sleep(3)
        
        # 3. 배달팁 - 배달팁이 없으면 0으로 저장됨
        delivery_tip = running_driver.find_element(By.XPATH, '//*[@id="content"]/div[2]/div[2]/ng-include/div/div[2]/div[4]/span[1]').get_attribute('innerHTML')
        infos['delivery_tip'] = price_to_int(delivery_tip)

        # 4. 최소주문금액
        price_for_delivery = running_driver.find_element(By.XPATH, '//*[@id="content"]/div[2]/div[1]/div[1]/div[2]/ul/li[3]/span').text
        infos['delivery_available_price'] = price_to_int(price_for_delivery)

        ### 5. 메뉴 전체 적용 할인 정보
        promotion_info = running_driver.find_element(By.XPATH, '//*[@id="content"]/div[2]/div[1]/div[1]/div[2]/ul/li[2]/span').text
        if promotion_info:
            infos['promotion_on_condition'] = price_to_int(promotion_info)
            
            on_condition_lst = re.findall('[\d,]+원 이상 주문 시', promotion_info)
            # '~ 이상 주문 시' 문구 있으면 조건 추가
            if on_condition_lst:
                on_condition = on_condition_lst[0]
                infos['condition'] = on_condition
            else: # 해당 문구가 없으면 최소주문금액 이상 주문 시 할인인 것으로 확인됨 (요기요 앱 참고)
                infos['condition'] = f'{infos["delivery_available_price"]}원 이상 주문 시'

        else:
            infos['promotion_on_condition'] = ''
            infos['on_condition'] = ''

        # 추가할인 - 추가할인 없으면 '0%'로 저장
        additional_promo = running_driver.find_element(By.XPATH, '//*[@id="content"]/div[2]/div[1]/div[1]/div[2]/ul/li[7]/span[2]').text
        infos['additional_dc'] = re.findall('[\d]+%', additional_promo)

        # 6. 로고 이미지
        logo_element = running_driver.find_element(By.XPATH, '//*[@id="content"]/div[2]/div[1]/div[1]/div[2]/div[1]').get_attribute('style')
        infos['logo'] = re.findall('\"(.+?)\"', logo_element)[0]
        
        # 7. 메뉴 및 썸네일 크롤링
        menus_info_dict = {}
        menus = []
        out_of_stock = []
        descs = []
        imgs = []
        prices = []
        dcs = []

        menu_tabs = running_driver.find_elements(By.CSS_SELECTOR, '[ng-repeat="category in restaurant.menu"]')[1:]
        for menu_infos in menu_tabs:
            # 맨 위 두 탭은 건너뛰기
            tab_name = menu_infos.find_element(By.CSS_SELECTOR, '[ng-class="get_menu_class(category.slug)"]').text
            if tab_name.startswith('[요기서결제 시]') or tab_name == '인기메뉴':
                continue

            # 7-1. 메뉴 크롤링
            for menu_element in menu_infos.find_elements(By.CSS_SELECTOR, 'div.menu-name'):
                menus.append(menu_element.get_attribute('innerHTML'))
            
            # 7-2. 품절 여부 크롤링
            for menu_row in menu_infos.find_elements(By.CSS_SELECTOR, '[ng-repeat="item in category.items"]'):
                if menu_row.get_attribute('class').split()[-1] == 'out-of-stock':
                    out_of_stock.append(True)
                else:
                    out_of_stock.append(False)

            # 7-3. 메뉴 소개 크롤링
            for desc_element in menu_infos.find_elements(By.CLASS_NAME, 'menu-desc'):
                descs.append(desc_element.get_attribute('innerHTML'))

            # 7-4. 썸네일 크롤링
            img_elements = menu_infos.find_elements(By.CLASS_NAME, 'photo')
            for element in img_elements:
                img_attr = element.get_attribute('style') 
                filtered = re.findall('(https://.+?)\"', img_attr)
                if len(filtered) > 0:
                    img_url = filtered[0]
                else:
                    img_url = ''
                imgs.append(img_url)
            
            # 7-5. 원가 및 할인가 크롤링
            price_elements = menu_infos.find_elements(By.CSS_SELECTOR, '[ng-bind="item.price|krw"]')
            dc_elements = menu_infos.find_elements(By.CLASS_NAME, 'color-price')

            for price_element, dc_element in zip(price_elements, dc_elements):
                price = price_to_int(price_element.get_attribute('innerHTML'))
                dc = price_to_int(dc_element.get_attribute('innerHTML'))
                prices.append(price)
                dcs.append(price - dc)
            

        for menu, oos, desc, img, price, dc in zip(menus, out_of_stock, descs, imgs, prices, dcs):
            menus_info_dict[menu] = {'oos': oos, 'desc': desc, 'img': img, 'price': price, 'price_dc': dc}

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

            for _ in range(clicks):
                running_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                view_more = running_driver.find_element(By.CSS_SELECTOR, '[ng-show="check_more_review()"]')
                click_interception_handling(view_more)
            

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

        # 8-6. 리뷰 이미지 크롤링 - 이미지 여러장인 경우
        review_panels = running_driver.find_elements(By.CSS_SELECTOR, '.list-group-item.ng-scope')
        for panel in review_panels:
            try:
                img_elements = panel.find_elements(By.TAG_NAME, 'img')
                imgs_per_review = []
                for img_element in img_elements:
                    img = img_element.get_attribute('src')
                    imgs_per_review.append(img)
                review_imgs.append(imgs_per_review)
            except Exception as e:
                if type(e).__name__ == 'NoSuchElementException':
                    review_imgs.append('')

        reviews_info = [{'review_id': r_id, 'uploaded': uploaded, 'order': order, 'rate': star_rate, 'review': review_text, 'img': review_img}
                        for r_id, uploaded, order, star_rate, review_text, review_img\
                        in zip(review_ids, uploaded_times, ordered_menus, rates, review_texts, review_imgs)]
        
        infos['reviews_info'] = reviews_info

        ### 9. 점포 주소 크롤링
        r_info_button = running_driver.find_element(By.XPATH, '//*[@id="content"]/div[2]/div[1]/ul/li[3]/a')
        click_interception_handling(r_info_button)

        address_line = running_driver.find_element(By.CSS_SELECTOR, '[ng-show="restaurant.address.length > 0"]')
        address_text = address_line.find_element(By.TAG_NAME, 'span').text
        infos['address'] = address_text

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
