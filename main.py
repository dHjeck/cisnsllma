import os
import baidu_chatglm2
import time
import logging
import configparser
import commandrun
import sys

timeout = 10

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

log_path = "./log"

result_path = "./result"

input1 = ""

time_current_YMD = time.strftime('%Y-%m-%d', time.localtime())
time_current_HMS = time.strftime('%H-%M-%S', time.localtime())


def save_log(result):
    file_name = log_path + "/" + time_current_YMD + '.txt'
    with open(file_name, 'a') as file:
        file.write(result + "\n")
        file.close()
    logging.info("Log save done!")


def save_result(result):
    file_name = result_path + "/" + time_current_YMD + time_current_HMS + '.txt'
    with open(file_name, 'w') as file:
        file.write(result + "\n")
        file.close()
    logging.info("Result save done!")

#获取目标ip地址
def get_ip():
    config = configparser.ConfigParser()
    config.read('./settings/ip.ini', encoding='utf-8')
    ip = config.get('target', 'ip')
    return ip


#ftp处理
def ftp_deal():
    ip = get_ip()
    password = "./settings/password2.txt"
    logging.info("进入ftp处理")
    logging.info("每次执行间隔10s")
    with open("./settings/users.txt", encoding='utf-8') as file:
        for user in file.readlines():
            command = baidu_chatglm2.chat_with_baidu_ftp(ip, user, password)
            if command == "error":
                ftp_deal()
            command = command.replace("\n", "")
            result = commandrun.run_command_with_timeout(command, timeout)
            save_result(result)
            save_log(command)
            save_log(result)
            time.sleep(10)
    return 


#xss处理
def xss_deal():
    ip = get_ip()
    xss_path = os.getcwd()
    xss_path = xss_path + "/xs1.py"
    python_exe_path = sys.executable
    print(python_exe_path)
    command = baidu_chatglm2.chat_with_baidu_xss(ip, xss_path, python_exe_path)
    if command == "error":
        xss_deal()
    command = command.replace("\n", "")
    result = commandrun.run_command_with_timeout(command, timeout)
    save_result(result)
    save_log(command)
    save_log(result)
    return


#sql处理
def sql_deal():
    ip = get_ip()
    command = baidu_chatglm2.chat_with_baidu_sql(ip)
    if command == "error":
        sql_deal()
    command = command.replace("\n", "")
    result = commandrun.run_command_with_timeout(command, timeout)
    save_result(result)
    save_log(command)
    save_log(result)
    return


#判断是否存在环境信息
def judge_env():
    if os.stat('./settings/env.txt').st_size <=1:
        return "empty"
    else:
        return "not empty"

#执行其他命令
def env_check():
    with open('./settings/env.txt') as file:
        for lin in file.readlines():
            if "ftp" in lin:
                ftp_deal()
            elif "FTP" in lin:
                ftp_deal()
            elif "HTTP" in lin:
                xss_deal()
            elif "MySQL" in lin or "SQL server" in lin or "Oracle" in lin or "SQLite" in lin:
                sql_deal()
    return



#从chatglm2中获取命令
def get_command():
    ip = get_ip()
    if judge_env() == "empty":
        logging.warning("env is empty!")
        input1 = ip
        result = baidu_chatglm2.chat_with_baidu_command(input1)
        if result == "error":
            get_command()
        else:
            save_result(result)
            save_log(input1)
            save_log(result)
            result = result.replace("\n", "")
            result = commandrun.run_command_with_timeout(result, timeout)
            result = baidu_chatglm2.chat_with_baidu_nmap(result)
            if result == "error":
                get_command()
            else:
                save_result(result)
                save_log(result)
                return 
    else:
        logging.info("env is not empty!")
        env_check()
        return
    #     logging.info("env is not empty!")
    #     with open('.\settings\env.txt', 'r', encoding='utf-8') as file:
    #         env = file.read()
    #         input1 = env + " " + ip
    #     result = baidu_chatglm2.chat_with_baidu_nmap(input1)
    # save_result(result)
    # save_log(input1)
    # save_log(result)
    # return result

    


if __name__ == "__main__":
    #尝试10次
    for i in range(10):
        get_command()



