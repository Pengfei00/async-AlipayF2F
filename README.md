# async-AlipayF2F

支付宝当面付协程版

## Test Example

```python
    from alipay import Alipay
    import uuid

    private_key="""-----BEGIN RSA PRIVATE KEY-----
    ...
    -----END RSA PRIVATE KEY-----"""

    public_key="""-----BEGIN PUBLIC KEY-----
    ...
    -----END PUBLIC KEY-----"""

    loop = asyncio.new_event_loop()
    loop.run_until_complete(Alipay(app_id="2016072900115434",private_key=private_key,public_key=public_key,loop=loop,sign_type='RSA2',DEBUG=True).trade_precreate("2017101500000000", 10, '测试商品'))
```

## 参数

class Alipay
===

|参数名        | 是否必填  | 默认   |解释      |
|:--------:   | :-----:   | :----: |:----:     |
|app_id       | 是        |        |应用id    |
|private_key  |是         |        |私钥      |
|public_key |是||支付宝公钥 |
|need_check_sign||False|是否验签|
|format||json|必填json|
|charset||UTF-8|编码|
|sign_type||RSA2|加密方法|
|version||1.0|加密版本|
|DEBUG||False|debug模式|



def trade_precreate
====
|参数名        | 是否必填  | 默认   |解释      |
|:--------:   | :-----:   | :----: |:----:     |
|out_trade_no | 是 ||商户订单号|
|total_amount  |是 ||订单总金额 |
|subject |是||subject |
|·····|||其他参数看注释或https://docs.open.alipay.com/api_1/alipay.trade.precreate|

