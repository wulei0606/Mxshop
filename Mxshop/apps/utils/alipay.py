
# pip install pycryptodome
from datetime import datetime
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from base64 import b64encode, b64decode
from urllib.parse import quote_plus
from urllib.parse import urlparse, parse_qs
from urllib.request import urlopen
from base64 import decodebytes, encodebytes

import json


class AliPay(object):
    """
    支付宝支付接口
    """

    def __init__(self, appid, app_notify_url, app_private_key_path,
                 alipay_public_key_path, return_url, debug=False):
        #应用id
        self.appid = appid
        #用户扫码创建订单未支付，用户再回订单用户界面支付的话，return_url就没用
        #支付了，支付宝给你发一个异步的请求
        #异步的请求就是说比如我们把页面关了之后，支付宝发了一个通知告诉你该账单已经被用户支付了。
        #需要去系统里更改订单的状态啊等一些后续的工作。
        #那时候的url已经和支付宝产生一个异步的交互了。是不可能给浏览器再返回页面的。
        #所以我们也需要一个异步接收的接口。return是一个同步接收的接口
        self.app_notify_url = app_notify_url
        #私钥文件路径
        self.app_private_key_path = app_private_key_path
        #读文件，生成key
        self.app_private_key = None
        #支付成功的返回页面，支付宝自动跳转的页面
        self.return_url = return_url
        #读取私钥文件生成key
        with open(self.app_private_key_path) as fp:
            self.app_private_key = RSA.importKey(fp.read())
        #读取支付宝公钥文件，生成key
        #验证支付宝返回消息（最主要的key）
        self.alipay_public_key_path = alipay_public_key_path
        with open(self.alipay_public_key_path) as fp:
            self.alipay_public_key = RSA.import_key(fp.read())

        if debug is True:
            self.__gateway = "https://openapi.alipaydev.com/gateway.do"
        else:
            self.__gateway = "https://openapi.alipay.com/gateway.do"
    #订单字段的数据，传递一些参数进来。交易标题，我们的订单号，总金额。
    def direct_pay(self, subject, out_trade_no, total_amount, return_url=None, **kwargs):
        biz_content = {
            "subject": subject,
            "out_trade_no": out_trade_no,
            "total_amount": total_amount,
            "product_code": "FAST_INSTANT_TRADE_PAY",
            # "qr_pay_mode":4
        }

        biz_content.update(kwargs)
        data = self.build_body("alipay.trade.page.pay", biz_content, self.return_url)
        return self.sign_data(data)
    #支付宝公共请求参数
    def build_body(self, method, biz_content, return_url=None):
        data = {
            "app_id": self.appid,
            "method": method,
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "biz_content": biz_content
        }

        if return_url is not None:
            data["notify_url"] = self.app_notify_url
            data["return_url"] = self.return_url

        return data
    #签名（核心）
    def sign_data(self, data):
        #支付宝文档中，签名前先要把sign字段去掉
        data.pop("sign", None)
        # 排序后的字符串
        unsigned_items = self.ordered_data(data)
        #排序后的tuple需要用&符号连接起来（支付宝文档归定）生成字符串，如下
        #app_id=沙箱appid&biz_content={"subject":"\u6d4b\u8bd5\u8ba2\u5355","out_trade_no":"20180312mtianyan001","total_amount":9999,"product_code":"FAST_INSTANT_TRADE_PAY"}&charset=utf-8&method=alipay.trade.page.pay&notify_url=http://127.0.0.1:8000/alipay/return/&return_url=http://127.0.0.1:8000/alipay/return/&sign_type=RSA2&timestamp=2018-03-12 18:59:09&version=1.0
        unsigned_string = "&".join("{0}={1}".format(k, v) for k, v in unsigned_items)
        #拿到签名字符串
        sign = self.sign(unsigned_string.encode("utf-8"))
        #quote_plus会将url做一定的处理。区别在于不会让参数签名带http: // 等多余字符。
        quoted_string = "&".join("{0}={1}".format(k, quote_plus(v)) for k, v in unsigned_items)

        # 获得最终的订单信息字符串
        signed_string = quoted_string + "&sign=" + quote_plus(sign)
        return signed_string

    def ordered_data(self, data):
        complex_keys = []
        for key, value in data.items():
            if isinstance(value, dict):
                complex_keys.append(key)

        # 将字典类型的数据dump出来
        print(complex_keys)
        for key in complex_keys:
            data[key] = json.dumps(data[key], separators=(',', ':'))
        print(data)
        #对data里面的参数进行排序（详情看支付宝文档），不排序会出错
        return sorted([(k, v) for k, v in data.items()])

    def sign(self, unsigned_string):
        # 开始计算签名
        key = self.app_private_key
        signer = PKCS1_v1_5.new(key)
        signature = signer.sign(SHA256.new(unsigned_string))
        # base64 编码，转换为unicode表示并移除回车
        sign = encodebytes(signature).decode("utf8").replace("\n", "")
        return sign

    def _verify(self, raw_content, signature):
        # 开始计算签名
        key = self.alipay_public_key
        signer = PKCS1_v1_5.new(key)
        digest = SHA256.new()
        digest.update(raw_content.encode("utf8"))
        if signer.verify(digest, decodebytes(signature.encode("utf8"))):
            return True
        return False
    #用来验证支付宝返回的数据是否有效，因为这个数据有可能是被别人截获。它会修改里面的数据，让订单状态变为成功支付。
    def verify(self, data, signature):
        if "sign_type" in data:
            sign_type = data.pop("sign_type")
        # 排序后的字符串
        unsigned_items = self.ordered_data(data)
        message = "&".join(u"{}={}".format(k, v) for k, v in unsigned_items)
        return self._verify(message, signature)


if __name__ == "__main__":

    # 测试用例
    alipay = AliPay(
        # appid在沙箱环境中就可以找到
        appid="",
        # 这个值先不管，在与vue的联调中介绍
        app_notify_url="",
        # 我们自己商户的密钥
        app_private_key_path="../trade/keys/private_2048.txt",
        # 支付宝的公钥
        alipay_public_key_path="../trade/keys/alipay_key_2048.txt",  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        # debug为true时使用沙箱的url。如果不是用正式环境的url
        debug=True,  # 默认False,

        # 先不用管，后面vue解释
        return_url=""
    )
    #验证返回的url

    # #支付宝返回的url
    # return_url = ''
    # #将返回的url传入
    # o = urlparse(return_url)
    # #取出url中的值
    # query = parse_qs(o.query)
    # processed_query = {}
    #删除掉sign，用于进行签名验证，调用上面的verify函数
    # ali_sign = query.pop("sign")[0]
    # for key, value in query.items():
    #     processed_query[key] = value[0]
    # print (alipay.verify(processed_query, ali_sign))

    # 直接支付:生成请求的字符串。
    url = alipay.direct_pay(
        # 订单标题
        subject="测试订单",
        # 我们商户自行生成的订单号
        out_trade_no="20180314006",
        # 订单金额
        total_amount=9999,
        return_url=""
    )
    # 将生成的请求字符串拿到我们的url中进行拼接
    re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(data=url)

    print(re_url)
