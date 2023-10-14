from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Category
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
            {'name':'BHC 동판교점', 'distance':'2.3km', 'review':'4.5'},
            {'name':'교촌치킨 동판교점', 'distance':'2.3km', 'review':'5.0'},
            {'name':'a치킨', 'distance':'2.7km', 'review':'3.5'},
            {'name':'b치킨', 'distance':'3.3km', 'review':'2.5'},
            {'name':'c치킨', 'distance':'6.3km', 'review':'3.4'},
            {'name':'d치킨', 'distance':'2.3km', 'review':'4.7'},
            {'name':'e치킨', 'distance':'1.3km', 'review':'4.2'},
        ]
    }
    return render(request, 'board/category.html' , {'cat_list':cat_list})
    
def update(request):
    # bhc를 눌렀다는 가정하에...
    if request.method == "POST":
        menu = [
        {'name':'뿌링클', 
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
            {'company':'쿠팡이츠', 'coupon': '5% 할인'},]},
        ]

        return HttpResponse(menu)

    return HttpResponse({"error": "invalid request"})

