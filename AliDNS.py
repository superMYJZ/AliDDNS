# -*- coding: UTF-8 -*-
"""
@Author:Admin
@File:AliDNS.py
@DateTime:2022/8/25 15:36
@SoftWare:PyCharm
"""
# -*- coding: utf-8 -*-
# 阿里云域名解析 DDNS
# 参考:https://next.api.aliyun.com/api/Alidns/2015-01-09/AddDomainRecord?params={}
# Python包依赖alibabacloud_alidns20150109==3.0.0
import os
try:
    import alibabacloud_tea_openapi
except:
    os.system('pip install alibabacloud_alidns20150109==3.0.0')

import yaml
import requests
from alibabacloud_alidns20150109.client import Client as Alidns20150109Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_alidns20150109 import models as alidns_20150109_models
from alibabacloud_tea_util import models as util_models


class AliDNS:
    def __init__(self, access_key_id: str, access_key_secret: str):
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret

    def client(self) -> Alidns20150109Client:
        """
        使用AK&SK初始化账号Client
        @param access_key_id:
        @param access_key_secret:
        @return: Client
        @throws Exception
        """
        config = open_api_models.Config(
            # 您的 AccessKey ID,
            access_key_id=self.access_key_id,
            # 您的 AccessKey Secret,
            access_key_secret=self.access_key_secret
        )
        # 访问的域名
        config.endpoint = f'alidns.cn-beijing.aliyuncs.com'
        return Alidns20150109Client(config)

    def record(self, DomainName, RR):  # 'gmusk.top'
        currentIP = requests.get('https://checkip.amazonaws.com').text.strip()
        client = self.client()
        # 先查询是否有
        describe_domain_records_request = alidns_20150109_models.DescribeDomainRecordsRequest(
            domain_name=DomainName
        )
        runtime = util_models.RuntimeOptions()
        # 复制代码运行请自行打印 API 的返回值
        ret = client.describe_domain_records_with_options(describe_domain_records_request, runtime)
        # print(ret.body.domain_records.record)

        oIP = None
        recordId = None
        for record in ret.body.domain_records.record:
            # print(record)
            if record.rr == RR:
                recordId = record.record_id
                oIP = record.value
        if oIP is not None:
            if oIP == currentIP:  # 如果有RR记录，且当前的IP与解析记录不同，则更新解析记录
                return
            update_domain_record_request = alidns_20150109_models.UpdateDomainRecordRequest(
                record_id=recordId,
                rr=RR,
                type='A',
                value=currentIP
            )
            runtime = util_models.RuntimeOptions()
            try:
                # 复制代码运行请自行打印 API 的返回值
                ret = client.update_domain_record_with_options(update_domain_record_request, runtime)
                # print(ret.status_code)
                if ret.status_code == 200:
                    print('------------更新解析成功------------')
            except Exception as error:
                # 如有需要，请打印 error
                print('------------执行失败------------')
        else:
            add_domain_record_request = alidns_20150109_models.AddDomainRecordRequest(
                domain_name=DomainName,
                rr=RR,
                type='A',
                value=currentIP
            )
            runtime = util_models.RuntimeOptions()
            try:
                # 复制代码运行请自行打印 API 的返回值
                ret = client.add_domain_record_with_options(add_domain_record_request, runtime)
                # print(ret.status_code)
                if ret.status_code == 200:
                    print('------------添加解析成功------------')
            except Exception as error:
                # 如有需要，请打印 error
                print('------------执行失败------------')


if __name__ == '__main__':
    with open('./conf.yaml', 'r', encoding='utf8') as f:
        conf = yaml.load(f, Loader=yaml.FullLoader)

    # print(conf)
    accessKeyId = conf['User']['accessKeyId']
    accessKeySecret = conf['User']['accessKeySecret']
    aliDNS = AliDNS(accessKeyId, accessKeySecret)
    for domain in conf['Domain']:
        print(domain)
        aliDNS.record(domain['root'], domain['record'])
