from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Category
import json
# Create your views here.
def main(request):
    # cat_list = Category.objects.all()
    # category = []

    # for cat in cat_list:
    #     cat_dict = {
    #         'id': cat.id,
    #         'name': cat.name,
    #         'url': cat.url,
    #         'img_path': cat.img_path,
    #     }
    #     category.append(cat_dict)
        
    ## Test Code
    category = [
        {'name':'치킨', 'url':'chicken', 'path':"https://nenechicken.com/17_new/images/menu/30005.jpg"},
        {'name':'한식', 'url':'korean', 'path':"http://www.hotelrestaurant.co.kr/data/photos/20180205/art_15175330519518_43b250.bmp"},
    ]
    
    return render(request, 'board/main.html', {'category': category})

def category(request, category_name):
    # pass
    if request.method == "POST":
        cart_list = request.GET['test']
        return redirect(request, 'board/temp2.html' , {'cart_list':cart_list})

    cat_list = {
        'name': '치킨', 'store_list' : [
            {'name':'BHC 동판교점', 'adrs':'서울특별시 ~~', 'sale':'~~~~~'},
            {'name':'교촌치킨 동판교점', 'adrs':'서울특별시 ~~', 'sale':'dfsdfsdf'},
            {'name':'a치킨', 'adrs':'서울특별시 ~~', 'sale':'gsdfbsdcv'},
            {'name':'b치킨', 'adrs':'서울특별시 ~~', 'sale':'sdfasdfvxc'},
            {'name':'c치킨', 'adrs':'서울특별시 ~~', 'sale':'asdfvvc'},
            {'name':'d치킨', 'adrs':'서울특별시 ~~', 'sale':'dsafvacv'},
            {'name':'e치킨', 'adrs':'서울특별시 ~~', 'sale':'asdfvvbsfhg'},
        ]
    }
    return render(request, 'board/category.html' , {'cat_list':cat_list})
    
def update(request):
    # bhc를 눌렀다는 가정하에...
    if request.method == "POST":
        menu = {
            'store' : 'BHC', 
            'dil_time':'배민: 40분 | 요기요: 50분',
        'menus':
            [{'name':'뿌링클', 
            'coupon':[
            {'company':'요기요', 'coupon': '5% 할인'},
            {'company':'배달의 민족', 'coupon': '5% 할인'},
            {'company':'쿠팡이츠', 'coupon': '5% 할인'},]},
            {'name':'치킨 1', 
         'coupon':[
            {'company':'요기요', 'coupon': '5% 할인'},
            {'company':'배달의 민족', 'coupon': '5% 할인'},
            {'company':'쿠팡이츠', 'coupon': '5% 할인'},]},
        {'name':'치킨 2', 
         'coupon':[
            {'company':'요기요', 'coupon': '5% 할인'},
            {'company':'배달의 민족', 'coupon': '5% 할인'},
            {'company':'쿠팡이츠', 'coupon': '5% 할인'},]}]
        }   
        return HttpResponse(json.dumps(menu))

    return HttpResponse({"error": "invalid request"})

def review_update(request):
    if request.method == "POST":
        menu = ''
        return HttpResponse(json.dumps(menu))

    return HttpResponse({"error": "invalid request"})