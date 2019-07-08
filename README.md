# Aiohttp Cralwer


## About:

基于协程的海量可控实时并发Web请求类的实现



## Deployment:

Python3.7

* aiohttp 3.5.4



## Install:

```shell
git clone https://github.com/Loveforkeeps/aiohttphugecralwer
```



## Using:

```shell
usage: wgetaiohttp.py [-h] [-f FILE] [-c COROUTINE] [--debug]

WEB请求信息获取-协程版 Beta1.0

optional arguments:
  -h, --help            显示帮助信息
  -f FILE, --file FILE  选定要请求的URL文件(内容按行分割)
  -c COROUTINE, --coroutine COROUTINE
                        协程任务数量,默认10000
  --debug               调试模式,开启控制台打印
```

sample：

```shell
python wgetaiohttp.py -f 100000url.txt -c 10000 
```



## Update:

- None



### Issure Log:

- None



### Todo List:

- None



## Running  screenshot:

- ![carbon-2](/README.assets/carbon-2.png)



## License:

This project is licensed under the [MIT license](http://opensource.org/licenses/mit-license.php) 



## Acknowledgments：

- None
