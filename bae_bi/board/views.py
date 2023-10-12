from django.shortcuts import render

from .models import Category
# Create your views here.


def main(request):  # 수정한 코드
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


def category(request):
    pass

    # cat_list = {
    #     'name': '치킨', 'store_list' : [
    #         {'name':'BHC 동판교점','company':'요기요' ,'coupon': '요기요 5% 할인'},
    #         {'name':'교촌치킨 동판교점','company':'배민', 'coupon': '배민 2,000원 할인'},
    #     ]
    # }
    # return render(request, 'board/category.html' , {'cat_list':cat_list})

