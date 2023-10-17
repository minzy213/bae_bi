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
    cat_list = {
        'name': '치킨', 'store_list' : [
            {'name':'BHC aaa', 'adrs':'서울특별시 ~~', 'sale':'~~~~~'},
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
    print("update")
    # bhc를 눌렀다는 가정하에...
    if request.method == "POST":
        print(request.POST.get('store_name'))
        menu = {
            'name': 'BHC 동판교점', 
            'service': ['배민', '요기요', '쿠팡이츠'],
            'time': ['','45-55분', '53-55분'],
            'fee': ['2,300원','', '2,500원'],
            'coupon': ['1,000원 할인', '',''],
            'menu_list':[
                {'name':'뿌링클', 'price':'18,000', 'info':'뿌링뿌링, 세상에 없던 마법의 맛 뿌링클', 'thumbnail_path':'path', 'coupon':'| 요기요: 5% 할인 | 배민: 2,000원 할인 |'},
                {'name':'마법클', 'price':'17,000', 'info':'마늘, 버터와 크런치한 후레이크의 마법같은 조합', 'thumbnail_path':'path', 'coupon':''},],
            'review_list':[
                { 'platform':0 , 'author':'mi**', 'content':'맛있어요', 'rate':3, 'img_path':'http://www.bhc.co.kr/upload/bhc/menu/%EB%BF%8C%EB%A7%81%ED%81%B4_410x271.png', 'created_at':'2023.10.12 16:00', 'menu':'뿌링클 콤보'},
                { 'platform':1, 'author':'nina**', 'content':'진짜 맛있음 bb', 'rate':4, 'img_path':'http://www.bhc.co.kr/upload/bhc/menu/%ED%95%AB%ED%9B%84%EB%9D%BC%EC%9D%B4%EB%93%9C-%EC%BD%A4%EB%B3%B4_410x271.png', 'created_at':'2023.9.12 17:00', 'menu':'후라이드 콤보'},
                { 'platform':1, 'author':'nina**', 'content':'진짜 맛있음 bb', 'rate':4, 'img_path':'http://www.bhc.co.kr/upload/bhc/menu/%ED%95%AB%ED%9B%84%EB%9D%BC%EC%9D%B4%EB%93%9C-%EC%BD%A4%EB%B3%B4_410x271.png', 'created_at':'2023.9.12 17:00', 'menu':'후라이드 콤보'},
                { 'platform':1, 'author':'nina**', 'content':'진짜 맛있음 bb', 'rate':4, 'img_path':'http://www.bhc.co.kr/upload/bhc/menu/%ED%95%AB%ED%9B%84%EB%9D%BC%EC%9D%B4%EB%93%9C-%EC%BD%A4%EB%B3%B4_410x271.png', 'created_at':'2023.9.12 17:00', 'menu':'후라이드 콤보'},
                { 'platform':2, 'author':'nono**', 'content':'진짜 맛있어요 강추!', 'rate':5, 'img_path':'http://www.bhc.co.kr/upload/bhc/menu/%ED%95%AB%ED%9B%84%EB%9D%BC%EC%9D%B4%EB%93%9C-%EC%BD%A4%EB%B3%B4_410x271.png', 'created_at':'2023.11.12 17:00', 'menu':'써브웨이 클럽 （15cm세트）/1(빵선택(허니오트),치즈선택(모차렐라치즈),빵／미'},]
            }

        return HttpResponse(json.dumps(menu))

    return HttpResponse({"error": "invalid request"})


def comp_cart(request):
    print("comp_cart")
    cart = request.POST.get('cart_list')
    print(cart)
    return render(request,'board/compare.html', {'cart':cart})


def review_update(request):
    if request.method == "POST":
        menu = ''
        return HttpResponse(json.dumps(menu))

    return HttpResponse({"error": "invalid request"})