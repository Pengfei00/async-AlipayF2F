# encoding: utf-8


"""
@author: Wnstar
@time: 2017/10/15 14:00
"""

import base64
import collections
import copy
import json
from datetime import datetime
from urllib import request, parse
from operator import itemgetter
from collections import OrderedDict
import rsa
import aiohttp
import asyncio
import logging
from datetime import datetime


class Alipay:
    def __init__(self, app_id, private_key, public_key, need_check_sign=False, format='json', charset='UTF-8',
                 sign_type='RSA2', version='1.0', notify_url=None, app_auth_token=None, *, loop=None, DEBUG=False):
        if DEBUG:
            logging.basicConfig(level=logging.DEBUG)
        self.need_check_sign = need_check_sign
        self.loop = loop or asyncio.get_event_loop()

        self.sign_type = sign_type.upper()
        self.url = 'https://openapi.alipay.com/gateway.do' if not DEBUG else "https://openapi.alipaydev.com/gateway.do"
        self.private_key = rsa.PrivateKey.load_pkcs1(private_key)
        self.public_key = rsa.PublicKey.load_pkcs1_openssl_pem(public_key)
        self.params = self._sort(
            dict(app_id=app_id, biz_content={}, method='alipay', format=format, charset=charset,
                 sign_type=sign_type, timestamp='', version=version, notify_url=notify_url,
                 app_auth_token=app_auth_token))

    async def _request(self, method, params):
        method = method.lower()
        async with aiohttp.ClientSession(loop=loop) as session:
            async with getattr(session, method)(url=self.url, params=params) as response:
                response = await response.json(content_type='utf-8')

                if not self.need_check_sign:
                    # 检查验签
                    self.check_sign("{}_response".format(method.replace('.', '_')), response)

                return response

    def _sort(self, params):
        """
            参数过滤+排序
        :param params:
        :return:
        """
        params = params.items()
        params = filter(lambda x: x[1] is not None, params)
        return OrderedDict(sorted(params, key=itemgetter(0)))

    def _make_sign(self, method, biz_content):
        """
            计算签名
        :param biz_content:
        :return:
        """

        params = copy.deepcopy(self.params)
        params['method'] = method
        params['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        params['biz_content'] = json.dumps(self._sort(biz_content))
        query = '&'.join("{}={}".format(k, v) for k, v in params.items())
        logging.debug(f"query: {query}")
        sign = base64.b64encode(
            rsa.sign(query.encode(), self.private_key, "SHA-1" if self.sign_type == "RSA" else "SHA-256")).decode(
            'utf-8')
        params['sign'] = sign
        logging.debug(f"sign: {sign}")
        return params

    def check_sign(self, method, response):
        """
            验证签名
        :param response:支付宝返回信息
        """

        sign = response.pop('sign')
        query = json.dumps(response[method])
        rsa.verify(query.replace(' ', '').replace(r'/', r'\/').encode(), base64.b64decode(sign), self.public_key)

    async def trade_precreate(self, out_trade_no, total_amount, subject, *, seller_id=None,
                              discountable_amount=None, goods_detail=None, body=None, operator_id=None, store_id=None,
                              disable_pay_channels=None, enable_pay_channels=None, terminal_id=None, extend_params=None,
                              timeout_express=None,
                              business_params=None):
        """

        :param out_trade_no:    商户订单号,64个字符以内、只能包含字母、数字、下划线；需保证在商户端不重复
        :param total_amount:    订单总金额，单位为元，精确到小数点后两位，取值范围[0.01,100000000] 如果同时传入了【打折金额】，【不可打折金额】，【订单总金额】三者，则必须满足如下条件：【订单总金额】=【打折金额】+【不可打折金额】
        :param subject:         订单标题
        :param seller_id:       卖家支付宝用户ID。 如果该值为空，则默认为商户签约账号对应的支付宝用户ID
        :param discountable_amount: 可打折金额. 参与优惠计算的金额，单位为元，精确到小数点后两位，取值范围[0.01,100000000] 如果该值未传入，但传入了【订单总金额】，【不可打折金额】则该值默认为【订单总金额】-【不可打折金额】
        :param goods_detail:    订单包含的商品列表信息.Json格式. 其它说明详见：“商品明细说明”
        :param body:            对交易或商品的描述
        :param operator_id:     商户操作员编号
        :param store_id:        商户门店编号
        :param disable_pay_channels: 禁用渠道，用户不可用指定渠道支付 当有多个渠道时用“,”分隔 注，与enable_pay_channels互斥
        :param enable_pay_channels: 可用渠道，用户只能在指定渠道范围内支付 当有多个渠道时用“,”分隔 注，与disable_pay_channels互斥
        :param terminal_id:     商户机具终端编号
        :param extend_params:   业务扩展参数
        :param timeout_express: 该笔订单允许的最晚付款时间，逾期将关闭交易。取值范围：1m～15d。m-分钟，h-小时，d-天，1c-当天（1c-当天的情况下，无论交易何时创建，都在0点关闭）。 该参数数值不接受小数点， 如 1.5h，可转换为 90m。
        :param business_params: 商户传入业务信息，具体值要和支付宝约定，应用于安全，营销等参数直传场景，格式为json格式
        """
        method = 'alipay.trade.precreate'
        total_amount = round(float(total_amount), 2) if total_amount is not None else None
        discountable_amount = round(float(discountable_amount), 2) if discountable_amount is not None else None
        biz_content = {'out_trade_no': str(out_trade_no)[:64],
                       'seller_id': seller_id,
                       'total_amount': total_amount,
                       'discountable_amount': discountable_amount,
                       'subject': subject,
                       'goods_detail': goods_detail,
                       'body': body,
                       'operator_id': operator_id,
                       'store_id': store_id,
                       'disable_pay_channels': disable_pay_channels,
                       'enable_pay_channels': enable_pay_channels,
                       'terminal_id': terminal_id,
                       'extend_params': extend_params,
                       'timeout_express': timeout_express,
                       'business_params': business_params}
        params = self._make_sign(method=method, biz_content=biz_content)
        response = await self._request('get', params)
        return response
