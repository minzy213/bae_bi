from django.db import models


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    url = models.CharField(max_length=255, default="")
    img_path = models.CharField(max_length=255, default="")


class Store(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    avg_rate = models.FloatField(default=0)
    category = models.ForeignKey(  # 해당 카테고리 점포가 있으면 삭제되지 않음
        Category, on_delete=models.PROTECT, related_name="category_set"
    )
    thumbnail_path = models.CharField(max_length=350, null=True)


class Delivery_info(models.Model):
    id = models.AutoField(primary_key=True)
    store = models.ForeignKey(  # 해당 점포 삭제 시 배달 정보도 함께 삭제
        Store, on_delete=models.CASCADE, related_name="dlv_store_set"
    )
    service = models.CharField(max_length=255)
    available = models.IntegerField(default=0) # 얼마 이상 주문 시 배달 가능
    time = models.CharField(max_length=255)
    fee = models.CharField(max_length=255)
    fee_list = models.CharField(max_length=255)
    prom = models.CharField(max_length=255)
    prom_cond = models.CharField(max_length=255)

class Menu(models.Model):
    id = models.AutoField(primary_key=True)
    store = models.ForeignKey(  # 해당 점포 삭제 시 메뉴도 함께 삭제
        Store, on_delete=models.CASCADE, related_name="mn_store_set"
    )
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    info = models.CharField(max_length=300, null=True)
    thumbnail_path = models.TextField(null=True, default='')
    is_soldout = models.BooleanField(default = False)
    
class Promotion(models.Model):
    id = models.AutoField(primary_key=True)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='menu_set')
    service = models.CharField(max_length=255)
    discount = models.IntegerField()
    


class User(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)


class Review(models.Model):
    id = models.AutoField(primary_key=True)
    store = models.ForeignKey(  # 해당 점포 삭제 시 댓글도 함께 삭제
        Store, on_delete=models.CASCADE, related_name="rv_store_set"
    )
    content = models.CharField(max_length=500)
    user = models.ForeignKey(  # 해당 유저 삭제 시 id null로 둔다
        User, null=True, on_delete=models.SET_NULL, related_name="user_set"
    )
    service = models.CharField(max_length=255, null=True, default='')
    rate = models.CharField(max_length=255)
    image_path = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    menu = models.TextField(null=True)
