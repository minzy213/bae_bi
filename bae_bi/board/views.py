from django.shortcuts import render

# Create your views here.
def main(request):

    category = [
        {'name':'치킨', 'url':'chicken', 'path':"https://nenechicken.com/17_new/images/menu/30005.jpg"},
        {'name':'한식', 'url':'korean', 'path':"http://www.hotelrestaurant.co.kr/data/photos/20180205/art_15175330519518_43b250.bmp"},
    ]
    return render(request, 'board/main.html', {"category":category} )

def category(request, category_name):
    #카테고리에 맞는 데이터를 받아와서 넘겨줘야 합니다.
    cat_list = {
        'name': '치킨', 'store_list' : [
            {'name':'BHC 동판교점','company':'요기요' ,'coupon': '요기요 5% 할인'},
            {'name':'교촌치킨 동판교점','company':'배민', 'coupon': '배민 2,000원 할인'},
        ]
    }
    return render(request, 'board/category.html' , {'cat_list':cat_list})
