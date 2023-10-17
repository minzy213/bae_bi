import os, sys
import json
PWD = os.path.abspath('.')

PROJ_MISSING_MSG = """Set an enviroment variable:\n
`DJANGO_PROJECT=your_project_name`\n
or call:\n
`init_django(your_project_name)`
"""

def init_django(project_name=None):
    os.chdir(PWD)
    project_name = project_name or os.environ.get('DJANGO_PROJECT') or None
    if project_name == None:
        raise Exception(PROJ_MISSING_MSG)
    sys.path.insert(0, os.getenv('PWD'))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'{project_name}.settings')
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
    import django
    django.setup()
    
init_django('bae_bi') #project name

from board.models import Category, Store, Delivery_info, Menu, Promotion, User, Review

# Category 저장, img path 추가 필요

categories = []
categories.append(Category(name="치킨", url = "chicken", img_path = 'static/bootstrap/images/chicken.png'))
categories.append(Category(name="중식", url = "chinese", img_path = 'bootstrap/images/chinese.png'))
categories.append(Category(name="일식", url = "japanese", img_path = './static/bootstrap/images/japanese.png'))
categories.append(Category(name="족발", url = "jokbal", img_path = './static/bootstrap/images/jokbal.png'))
categories.append(Category(name="한식", url = "korean", img_path = './static/bootstrap/images/korean.png'))
categories.append(Category(name="피자", url = "pizza", img_path = './static/bootstrap/images/pizza.png'))
Category.objects.bulk_create(categories)



def saveDB(filename, name):
    promotions = []
    reviews = []
    delivery_infos = []
    with open(f'../data/{filename}_infos.json', 'r', encoding='UTF8') as f:
        info = json.load(f)

    t_ct = Category.objects.filter(name=name)[0]
    idx = 0
    for rest in info['restaurants']:
        # store 추가
        t_store = Store.objects.create(name=rest['name'], address=rest['address'], avg_rate=rest['avg_rate'], category=t_ct, 
                            thumbnail_path=rest['logo'])
        
        # 요기요 배달정보 추가
        promo = rest['restaurant_promotions']['promotion_on_condition']
        if len(rest['restaurant_promotions']['additional_dc']) > 0:
            promo = rest['restaurant_promotions']['additional_dc']
        delivery_infos.append(Delivery_info(store=t_store, service='요기요', time=rest['delivery_time'], 
                                            fee=rest['delivery_tip'], prom=promo, available = rest['delivery_available_price'], 
                                            prom_cond=rest['restaurant_promotions']['on_condition']))        
        
        # menu 추가
        for name in rest['menu'].keys():
            t_menu = Menu.objects.create(store=t_store, name=name, price=rest['menu'][name]['price'],
                            info=rest['menu'][name]['description'], thumbnail_path=rest['menu'][name]['image'], 
                            is_soldout=rest['menu'][name]['out_of_stock'])
            # 메뉴 할인정보 추가
            if rest['menu'][name]['price_dc'] > 0:
                promotions.append(Promotion(menu=t_menu, service='요기요', discount=rest['menu'][name]['price_dc']))
            
        for review in rest['reviews_info']:
            us_name = review['review_id'][:2]
            t_user = User.objects.filter(name=us_name)
            # 유저 추가
            
            if len(t_user) == 0:
                t_user = User.objects.create(name=us_name)
            else:
                t_user = t_user[0]
            
            # 리뷰 추가
            rv_img = ''
            for img in review['img']:
                rv_img = img
            reviews.append(Review(store=t_store, content=review['review'], user=t_user, rate = review['rate'],
                                image_path = rv_img, created_at = '| ' + review['uploaded'], menu = review['order'], service = str(idx)))
            idx = (idx + 1) % 3
            
    Promotion.objects.bulk_create(promotions)
    Review.objects.bulk_create(reviews)
    Delivery_info.objects.bulk_create(delivery_infos)
    
saveDB('chicken', '치킨')
saveDB('chinese', '중식')
saveDB('japanese', '일식')
saveDB('jokbal', '족발')
saveDB('korean', '한식')
saveDB('pizza', '피자')

# 배민, 쿠팡이츠 저장
def saveOthers(filepath):
    with open(f'../data/{filepath}.json', 'r', encoding='UTF8') as f:
        info = json.load(f)
    
    delivery_infos = []

    for res in info['restaurants']:
        store = Store.objects.filter(name=res['name'])
        if len(store) == 0:
            print(f'there is no store named {res["name"]}')
            continue
        
        store = store[0]
        for serv in res['service']:
            fee_list = ''
            for fee in serv['delivery_tip_list']:
                fee_list += fee['condition'] + ': ' + str(fee['delivery_tip_on_condition']) + '|'
            fee_list = fee_list[:-1]
            prom_list = ''
            prom_cond = ''
            for prom in serv['promotions']:
                prom_list += str(prom['dc']) + '|'
                prom_cond += prom['on_condition'] + '|'
            if len(serv['additional_dc']) > 0:
                prom_list += serv['additional_dc']
            else:
                prom_list = prom_list[:-1]
            prom_cond = prom_cond[:-1]
            delivery_infos.append(Delivery_info(store=store, service=serv['name'], time=serv['delivery_time'], 
                                        fee=serv['delivery_tip'], fee_list = fee_list, prom=prom_list, 
                                        prom_cond=prom_cond, available = serv['delivery_available_price']))     

    Delivery_info.objects.bulk_create(delivery_infos)

saveOthers('chicken_baemin_coupang')
saveOthers('chinese_baemin_coupang')
saveOthers('japanese_baemin_coupang')
saveOthers('jokbal_baemin_coupang')
saveOthers('korean_baemin_coupang')
saveOthers('pizza_baemin_coupang')