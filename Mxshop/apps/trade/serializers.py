from datetime import time

from rest_framework import serializers
from goods.models import Goods
from .models import ShoppingCart,OrderInfo,OrderGoods

class ShopCartSerializer(serializers.Serializer):
    #使用Serializer本身最好，因为它灵活性最高
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    nums = serializers.IntegerField(
        required=True,label="数量",min_value=1,error_messages={
            "min_value":"商品数量不能小于一",
            "required":"请选择购买数量",
        }
    )
    goods = serializers.PrimaryKeyRelatedField(required=True,queryset=Goods.objects.all())

    def create(self, validated_data):
        user = self.context["request"].user
        nums = validated_data["nums"]
        goods = validated_data["goods"]

        existed = ShoppingCart.objects.filter(user=user,goods=goods)

        if existed:
            existed = existed[0]
            existed.nums += nums
            existed.save()
        else:
            existed = ShoppingCart.objects.create(**validated_data)

        return existed

    def update(self, instance, validated_data):
        #修改商品数量
        instance.nums = validated_data["nums"]
        instance.save()
        return instance



class OrderSerializer(serializers.ModelSerializer):

    def generate_order_sn(self):
        #当前时间 + userID + 随机数
        from random import Random
        random_ins = Random()
        order_sn = "{time_str}{userid}{ranstr}".format(time_str=time.strftime("%Y%m%d%H%M%S"),
                                                       userid=self.context["request"].user.id,
                                                       ranstr=random_ins.randint(10,99))
        return order_sn
    def validate(self, attrs):
        attrs["order_sn"] = self.generate_order_sn()
        return attrs

    class Meta:
        model = OrderInfo
        fields = "__all__"



