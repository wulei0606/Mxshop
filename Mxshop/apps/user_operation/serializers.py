from rest_framework import serializers
from user_operation.models import UserFav,UserLeavingMessage,UserAddress
from goods.serializers import GoodsSerializer


class UserFavSerializer(serializers.Serializer):
    class Meta:
        model = UserFav
        fields = ("user","goods")

class UserFavDetailSerializer(serializers.ModelSerializer):
    #通过goods_id拿到商品信息，需要嵌套的Serializer
    goods = GoodsSerializer()
    class Meta:
        model = UserFav
        fields = ("goods","id")

class LeavingMessageSerializer(serializers.Serializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    add_time = serializers.DateTimeField(read_only=True,format='%Y-%m-%d %H:%M')
    class Meta:
        model = UserLeavingMessage
        fields = ("user","message_type","subject","message","file","id","add_time")


class AddressSerializer(serializers.Serializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    add_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M')

    class Meta:
        model = UserAddress
        fields = ("id","user","province","city","district","address","signer_name","add_time","signer_mobile")
