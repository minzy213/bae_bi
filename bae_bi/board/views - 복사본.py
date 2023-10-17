from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Category, Store, Delivery_info, User
import json
# Create your views here.
def main(request):
    cat_list = Category.objects.all()
    category = []

    for cat in cat_list:
        cat_dict = {
            'id': cat.id,
            'name': cat.name,
            'url': cat.url,
            'img_path': cat.img_path,
        }
        category.append(cat_dict)

    
    return render(request, 'board/main.html', {'category': category})

from jamo import h2j, j2hcj

def category(request, category_name):
    if category_name == 'comp_cart':
        return comp_cart(request)
    cat_list = Category.objects.get(url=category_name)  # 한식 id 5
    cat_dict = {
        'name': j2hcj(h2j(cat_list.name)),
        'eng_name': category_name,
        'store_list': []
    }
    for sto in cat_list.category_set.all():
        store_dict = {
            'name': sto.name,
            'adrs': sto.address,
            'sale': ''
        }
        for ino in sto.dlv_store_set.all():
            if (len(ino.prom.split('|')) > 1) & (len(ino.prom_cond.split('|')) > 1):
                s_cond = ino.prom_cond.split('|')[0]
                s_prom = ino.prom.split('|')[0]
                store_dict['sale'] += f' | {ino.service}: {s_cond} {s_prom}'
            elif len(ino.prom) > 0:
                store_dict['sale'] += f' | {ino.service}: {ino.prom_cond} {ino.prom}'
        
        if len(store_dict['sale']) > 0:
            store_dict['sale'] += ' |'
        cat_dict['store_list'].append(store_dict)
    return render(request, 'board/category.html', {'cat_list': cat_dict})
    
def update(request):
    # bhc를 눌렀다는 가정하에...
    if request.method == "POST":
        detail = {'service':['배민', '요기요', '쿠팡이츠'], 'time':['']*3, 'fee':['']*3, 
                'coupon':['']*3, 'menu_list':[], 'review_list':[]}
        detail['name'] = request.POST.get('store_name')
        st_list = Store.objects.filter(name = detail['name'])
        
        for store in st_list:
            for delivery in store.dlv_store_set.all():
                idx = 1
                if delivery.service.find('배민'):
                    idx = 0
                elif delivery.service.find('쿠팡이츠'):
                    idx = 2
                detail['service'][idx] = delivery.service
                detail['time'][idx] = delivery.time
                detail['fee'][idx] = delivery.fee
                if len(delivery.prom.split('|')) > 0:
                    p_sp = delivery.prom.split('|')
                    cd_sp = delivery.prom_cond.split('|')
                    detail['coupon'][idx] = cd_sp[0] + ' ' + p_sp[0]   
                elif (len(delivery.prom) > 0) & (len(delivery.prom_cond) > 0)   :
                    detail['coupon'][idx] = delivery.prom_cond + ' ' + delivery.prom
                elif len(delivery.prom) > 0:
                    detail['coupon'][idx] = delivery.prom_cond                 
            
            for menu in store.mn_store_set.all():
                prom = ''
                promotion = menu.menu_set.all()
                if len(promotion) > 0:
                    promotion = promotion[0]
                    prom = '|' + promotion.service + ' ' + str(promotion.discount) + '원 할인 |'
                detail['menu_list'].append({'name':menu.name, 'price':menu.price, 'info':menu.info, 
                                            'thumbnail_path':menu.thumbnail_path, 'coupon':prom})
            
            for review in store.rv_store_set.all():
                img_path = ''
                if len(review.image_path.split('|')) > 0:
                    img_path = review.image_path.split('|')[0]
                else:
                    img_path = review.image_path
                detail['review_list'].append({ 'platform':int(review.service) , 'author':User.objects.filter(pk=review.user_id)[0].name + '** 님', 'content':review.content, 
                                              'rate':review.rate, 'path':img_path, 'created_at':review.created_at, 'menu':review.menu})
        return HttpResponse(json.dumps(detail))

    return HttpResponse({"error": "invalid request"})


def comp_cart(request):
    cart = request.POST.get('cart_list')
    return render(request,'board/compare.html', {'cart':cart})


def review_update(request):
    if request.method == "POST":
        menu = ''
        return HttpResponse(json.dumps(menu))

    return HttpResponse({"error": "invalid request"})

