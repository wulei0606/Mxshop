
#获取微博登录页面url
def get_auth_url():
    weibo_auth_url = "https://api.weibo.com/oauth2/authorize"
    redirect_url = "http://127.0.0.1:8001/complete/weibo/"
    client_id = "1191798388"
    auth_url = weibo_auth_url + "?client_id={client_id}&redirect_uri={re_url}".format(client_id=client_id,
                                                                                      re_url=redirect_url)
    print(auth_url)

#获取登录的token，这里是拿到登录的code
def get_access_token(code):
    access_token_url = "https://api.weibo.com/oauth2/access_token"
    import requests
    re_dict = requests.post(access_token_url,data={
        "client_id": 1191798388,
        "client_secret": "790ce03f2e0139874925a6fb2379f8fb",
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "http://127.0.0.1:8001/complete/weibo/",
    })
   # '{"access_token":"2.00oneFMGeMfeSB08890236f2BNW_BB","remind_in":"157679999","expires_in":157679999,"uid":"5675461512","isRealName":"true"}'
    pass
#获取带有微博用户json信息的url
def get_user_info(access_token):
    user_url = "https://api.weibo.com/2/users/show.json"
    uid = "5675461512"
    get_url = user_url + "?access_token={at}&uid={uid}".format(at=access_token, uid=uid)
    print(get_url)

if __name__ == '__main__':
    # get_auth_url()
    # get_access_token("c53bd7b5af51ec985952a3e23c03de3b")
    get_user_info("2.00oneFMGeMfeSB08890236f2BNW_BB")