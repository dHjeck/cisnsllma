import os
import baidu_chatglm2
import time
import logging
import configparser
import commandrun

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

log_path = "./log"
result_path = "./result"
input1 = ""

time_current_YMD = time.strftime('%Y-%m-%d', time.localtime())
time_current_HMS = time.strftime('%H-%M-%S', time.localtime())

os.makedirs(log_path, exist_ok=True)
os.makedirs(result_path, exist_ok=True)

def save_log(result):
    file_name = log_path + "/" + time_current_YMD + '.txt'
    with open(file_name, 'a') as file:
        file.write(result)
    logging.info("Log save done!")

def save_result(result):
    file_name = result_path + "/" + time_current_YMD + time_current_HMS + '.txt'
    with open(file_name, 'w') as file:
        file.write(result)
    logging.info("Result save done!")

def get_ip():
    config = configparser.ConfigParser()
    config.read('./settings/ip.ini', encoding='utf-8')
    ip = config.get('target', 'ip')
    return ip

def ftp_deal():
    ip = get_ip()
    password = "./settings/password2.txt"
    with open("./settings/users.txt", encoding='utf-8') as file:
        for user in file.readlines():
            command = baidu_chatglm2.chat_with_baidu_ftp(ip, user, password)
            if command == "error":
                logging.warning("FTP command error, retrying...")
                continue
            result = commandrun.run_command(command)
            save_result(result)
            save_log(command)
            save_log(result)
    return 

def xss_deal():
    ip = get_ip()
    command = baidu_chatglm2.chat_with_baidu_xss(ip)
    if command == "error":
        logging.warning("XSS command error, retrying...")
        return xss_deal()
    result = commandrun.run_command(command)
    save_result(result)
    save_log(command)
    save_log(result)
    return

def sql_deal():
    ip = get_ip()
    command = baidu_chatglm2.chat_with_baidu_sql(ip)
    if command == "error":
        logging.warning("SQL command error, retrying...")
        return sql_deal()
    result = commandrun.run_command(command)
    save_result(result)
    save_log(command)
    save_log(result)
    return

def judge_env():
    if os.stat('./settings/env.txt').st_size <= 1:
        return "empty"
    else:
        return "not empty"

def env_check():
    with open('./settings/env.txt') as file:
        for lin in file.readlines():
            if "ftp" in lin:
                ftp_deal()
            elif "HTTP" in lin:
                xss_deal()
            elif any(db in lin for db in ["MySQL", "SQL server", "Oracle", "SQLite"]):
                sql_deal()
    return

def get_command():
    global input1
    ip = get_ip()
    if judge_env() == "empty":
        logging.warning("env is empty!")
        input1 = ip
        result = baidu_chatglm2.chat_with_baidu_command(input1)
        if result == "error":
            return get_command()
        else:
            save_result(result)
            save_log(input1)
            save_log(result)
            result = commandrun.run_command(result)
            result = baidu_chatglm2.chat_with_baidu_nmap(result)
            if result == "error":
                return get_command()
            else:
                save_result(result)
                save_log(result)
                return 
    else:
        logging.info("env is not empty!")
        env_check()
        return

if __name__ == "__main__":
    for i in range(10):
        get_command()
