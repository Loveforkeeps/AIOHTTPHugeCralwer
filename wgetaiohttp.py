#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Erdog

import asyncio

import aiohttp

import os, sys

from pprint import pprint

from collections import OrderedDict

import datetime

import argparse

from itertools import islice

import ssl


# 时间装饰器
def functime(func):
    def wap(*args, **kw):
        local_time = datetime.datetime.now()
        func(*args, **kw)
        times = (datetime.datetime.now() - local_time)
        print('{} : Runing time is {}'.format(func.__name__, times))

    return wap


# log 配置
import inspect
import logging
logging.basicConfig(filename="{}.log".format(''.join(
    __file__.split('.')[:-1])),
                    filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def set_proxy(ip, port):
    # 设置系统代理变量,减少代理请求代码复杂度
    os.environ['ALL_PROXY'] = 'socks5://{}:{}'.format(ip, port)
    os.environ['HTTPS_PROXY'] = 'http://{}:{}'.format(ip, port)
    os.environ['https_proxy'] = 'http://{}:{}'.format(ip, port)
    os.environ['HTTP_PROXY'] = 'http://{}:{}'.format(ip, port)
    os.environ['http_proxy'] = 'http://{}:{}'.format(ip, port)


class AsyncXGrab(object):
    """
    用协程进行大批量Url信息爬取
    Attributes:
        urls: 需要爬取的Url队列
        concurrent: 并发量
    """
    # 请求头
    Headers = {
        "Upgrade-Insecure-Requests": '1',
        "User-Agent":
        "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0",
        "Connection": "keep-alive"
    }

    Mobil_Headers = {
        "Upgrade-Insecure-Requests": '1',
        "User-Agent":
        "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1",
        "Connection": "keep-alive"
    }

    # 设置类中的重连次数和最大重定向次数
    RETRY_TIMES = 3
    MAX_REDIRECTS = 5
    TIME_OUT = aiohttp.ClientTimeout(20)

    def __init__(self, urls, concurrent):
        self.concurrent = concurrent
        self.coros = (self.get_session_resp(url) for url in urls)

    def launch(self):
        asyncio.run(self.callback_when_done(self.coros, self.concurrent))

    async def callback_when_done(self, tasks, conc):
        for res in self.limited_as_completed(tasks, conc):
            res = await res
            if res:
                # 结果处理
                print("Result %s" % res['Status'])

    def limited_as_completed(self, coros, limit):
        futures = [asyncio.ensure_future(c) for c in islice(coros, 0, limit)]

        async def first_to_finish():
            await asyncio.sleep(0)
            for f in futures:
                if f.done():
                    futures.remove(f)
                    try:
                        newf = next(coros)
                        futures.append(asyncio.ensure_future(newf))
                    except StopIteration as e:
                        pass
                    return f.result()

        while len(futures) > 0:
            yield first_to_finish()

    async def get_session_resp(self, url):
        # 高级请求函数，支持代理
        print('starting: ' + url)
        try:
            async with aiohttp.ClientSession(trust_env=True) as session:
                async with session.get(url,
                                       headers=self.Headers,
                                       max_redirects=self.MAX_REDIRECTS,
                                       ssl=False,
                                       timeout=self.TIME_OUT) as resp:
                    res = await self.parse_resp(resp)
                    return res
        except asyncio.TimeoutError:
            print("TimeoutError: {}".format(url))
            logging.error("TimeoutError: {}".format(url))
        except Exception as e:
            print('error: ' + url)
            logging.error(e)

    async def get_resp(self, url):
        # 低级请求函数，无法设置代理，默认不校验ssl
        # 由于没有完善会出现如:Unclosed client session的Case所以目前暂用get_session_resp
        print('starting: ' + url)
        try:
            async with aiohttp.request('GET',
                                       url,
                                       headers=self.Headers,
                                       max_redirects=self.MAX_REDIRECTS,
                                       timeout=self.TIME_OUT) as resp:
                res = await self.parse_resp(resp)
                return res
        except asyncio.TimeoutError:
            print('请求超时', url)
        except Exception as e:
            print('error: ' + url)
            raise

    async def parse_resp(self, resp):
        # 解析请求
        data = await resp.read()
        # data = data.decode(resp.charset)
        url = str(resp.url)
        method = resp.method
        status = resp.status
        headers = dict(resp.headers)
        # print(data)
        redirects = list()
        for i in resp.history:
            redirects.append(
                OrderedDict({
                    'Url': i.url,
                    'Method': i.method,
                    'Status': i.status,
                    'Headers': dict(i.headers)
                }))
        return OrderedDict({
            'Url': url,
            'Method': method,
            'Status': status,
            'Headers': headers,
            # 'Data': data,
            'Redirects': redirects
        })


@functime
def main():
    urllists = [
        'https://edmundmartin.com', 'https://www.udemy.com',
        'https://github.com/', 'https://zhangslob.github.io/',
        'https://www.zhihu.com/', 'http://pastebin.com',
        'https://jianzhibuzunci.com'
    ]
    if args.file:
        urllists = args.file.read().splitlines()

    try:
        cralwer = AsyncXGrab(urllists, args.coroutine)
        cralwer.launch()
    except KeyboardInterrupt:
        print("User Terminated!\n")
        sys.exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=u'WEB请求信息获取-协程版 Beta1.0',
                                     add_help=False)
    parser.add_argument('-h', '--help', action='help', help=u'显示帮助信息')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-f',
                       '--file',
                       type=argparse.FileType('r'),
                       help=u'选定要请求的URL文件(内容按行分割)')
    parser.add_argument('-c',
                        '--coroutine',
                        default=10000,
                        type=int,
                        help=u'协程任务数量,默认10000')
    parser.add_argument('--debug', action='store_true', help=u'调试模式,开启控制台打印')
    args = parser.parse_args()

    if not args.debug:
        print = logging.info

    main()