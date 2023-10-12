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


# def main(request):

#     cat_list = Category.objects.all()
#     category = []

#     for cat in cat_list:
#         category = {
#             'id': cat.id,
#             'name': cat.name,
#             'url': cat.url,
#             'img_path': cat.img_path,
#         }
#         category.append(category)

#     return render(request, 'board/main.html', {'category': category})

    # dict_category = [
    #     {'name': '치킨', 'url': 'chicken',
    #         'path': "https://nenechicken.com/17_new/images/menu/30005.jpg"},
    #     {'name': '한식', 'url': 'korean',
    #         'path': "http://www.hotelrestaurant.co.kr/data/photos/20180205/art_15175330519518_43b250.bmp"},
    # ]

    # return render(request, 'board/main.html', {'category': category})


# def category(request):
#     cat_list = Category.objects.all()
#     category = []

#     for cat in cat_list:
#         category = {
#             'id': cat.id,
#             'name': cat.name,
#             'url': cat.url,
#             'img_path': cat.img_path,
#         }
#         category.append(category)

#     return {'category': category}


# 해야할것
# 1. main 에 옮기기 (o)
# 2. 리턴 형태 (o)
# 3. 카테고리스 -> 카테고리로 바꾸기 (o)
