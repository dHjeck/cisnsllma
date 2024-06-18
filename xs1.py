import argparse
from lib.helper.helper import *
from lib.helper.Log import *
from lib.core import *
from random import randint
from lib.crawler.crawler import *

def check(payload_level, payload):
    payload_level = int(payload_level)
    if payload_level > 6 and payload is None:
        Log.info("使用自定义负载 (Y/n)?")
        answer = input("> " + W)
        if answer.lower().strip() == "y":
            Log.info("写下XSS有效负载")
            payload = input("> " + W)
        else:
            payload = core.generate(randint(1, 6))
    else:
        payload = core.generate(payload_level)

    return payload

def start():
    print(logo)
    Log.info("开始 XSS扫描...")
    
    parse = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, usage="XSS -u <目标> [选项]",
                                        add_help=False)
    pos_opt = parse.add_argument_group("选项")
    pos_opt.add_argument("--help", action="store_true", default=False, help="显示使用方法和帮助参数")
    pos_opt.add_argument("-u", metavar="", help="Target url (e.g. http://testphp.vulnweb.com)")
    pos_opt.add_argument("--depth", metavar="", help="深度网页抓取，默认值: 2", default=2)
    pos_opt.add_argument("--payload-level", metavar="", help="有效负载生成器的级别，自定义有效负载的级别为 7。 {1...6}. 默认: 6", default=6)
    pos_opt.add_argument("--payload", metavar="", help="直接加载自定义负载 (e.g. <script>alert(2005)</script>)", default=None)
    pos_opt.add_argument("--method", metavar="", help="方法设置(s): \n\t0: GET\n\t1: POST\n\t2: GET and POST (default)", default=2, type=int)
    pos_opt.add_argument("--user-agent", metavar="", help="请求用户代理 (e.g. Chrome/2.1.1/...)", default=agent)
    pos_opt.add_argument("--single", metavar="", help="单次扫描。不抓取仅一个地址")
    pos_opt.add_argument("--proxy", default=None, metavar="", help="设置代理（例如 {'https':'https://11.11.1.10:1080'}）")
    pos_opt.add_argument("--about", action="store_true", help="输出有关XSS工具的信息")
    pos_opt.add_argument("--cookie", help="设置cookie（例如{'ID':'1026492380'}）", default='''{"ID":"1075480543"}''', metavar="")

    args = parse.parse_args()

    if args.about:
        print("""""")
    elif args.help or not args.u:
        parse.print_help()
    elif args.u:
        try:
            if args.u:
                payload = check(args.payload_level, args.payload)
                core.main(args.u, args.proxy, args.user_agent, payload, args.cookie, args.method)
                crawler.crawl(args.u, int(args.depth), args.proxy, args.user_agent, payload, args.method, args.cookie)
            elif args.single:
                payload = check(args.payload_level, args.payload)
                core.main(args.single, args.proxy, args.user_agent, payload, args.cookie, args.method)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    start()
