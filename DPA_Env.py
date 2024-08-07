import gym
from gym import spaces
import numpy as np
import subprocess
import configparser
import time
import os
import main as CTB
import baidu_chatglm2
import commandrun
import logging
import sys

timeout = 10
command_line = []
comand_line = ''
Program_root_path = os.path.abspath(__file__)
command_num = 0
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

##读取命令

def Read_command_num():
    command = configparser.ConfigParser()
    command.read('command.ini')
    command_num = command.getint('Command', 'command_num')
    return command_num

class Readcommand(object):
    def __init__(self):
        self.command_line = []
        self.command_num = 0

    def read_command(self):
        command = configparser.ConfigParser()
        command.read('command.ini')
        self.command_num = command.getint('Command', 'command_num')
        for i in range(self.command_num):
            self.command_line.append(command.get('Command', 'command' + str(i)))
        return self.command_line
    def read_command_num(self):
        command = configparser.ConfigParser()
        command.read('command.ini')
        self.command_num = command.getint('Command', 'command_num')
        return self.command_num

##读取配置（目前只有主机ip）
class Readconfig(object):
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('./settings/ip.ini')
        self.host = self.config.get('server', 'ip')

    def read_host(self):
        self.config = configparser.ConfigParser()
        self.config.read('./settings/ip.ini')
        self.host = self.config.get('server', 'ip')
        return self.host
##结合指令
class Composecommandconfig(object):
    def __init__(self):
        self.command_num = Readcommand.read_command_num(self)
        self.command_line = []
        self.config = Readconfig.read_host(self)

    def mix_command(self):
        self.command_num = Readcommand.read_command_num(self)
        self.config = Readconfig.read_host(self)
        for i in range(0,self.command_num):
            self.command_line[i]= self.command_line[i] + " " + self.config
        return self.command_line

    def outputcommand(self):
        for i in range(self.command_line):
            command_line.append(self.command_line[i])
            print(command_line[i])
        return command_line
    
    def Cf_main(self):
        Readcommand.read_command(self)
        Composecommandconfig.mix_command(self)
        return self.command_line
        ##return Composecommandconfig.outputcommand(self)
#智能体环境主体
class Network_explorer(gym.Env):
    def __init__(self):
        super(Network_explorer, self).__init__()

        self.observation_Space = spaces.Discrete(5)

        self.action_space = spaces.Discrete(3)

        self.state = None

        self.goal_state = 2

        self.command_line = []

        self.flags = 0
    #创建智能体动作
    def step(self, action):
        global result
        ip = CTB.get_ip()
        command_line = "error"
        if self.flags==0:
            Composecommandconfig.Cf_main(self)
            self.flags = 1
        # for i in range(0,3):
        #     if action == i:
        #         print(i)
        #         command_line = self.command_line[i]
        #         result = subprocess.run(command_line, shell=True, stdout=subprocess.PIPE, text=True, universal_newlines=True)
        if action == 0:
            while command_line == "error":
                command_line = baidu_chatglm2.chat_with_baidu_command(ip)
            command_line = command_line.replace("\n", "")
            CTB.save_log(command_line)
            CTB.save_result(command_line)
            result_c = commandrun.run_command_with_timeout(command_line, timeout)
            tmp = result_c
            while result_c == tmp:
                result_c = baidu_chatglm2.chat_with_baidu_nmap(result_c)
            CTB.save_result(result_c)
            CTB.save_log(result_c)
        
        if action == 1:
            password = "./settings/password2.txt"
            logging.info("进入ftp处理")
            logging.info("每次执行间隔10s")
            with open("./settings/users.txt", encoding='utf-8') as file:
                for user in file.readlines():
                    while command_line == "error":
                        command_line = baidu_chatglm2.chat_with_baidu_ftp(ip, user, password)
                    command_line = command_line.replace("\n", "")
                    result_c = commandrun.run_command_with_timeout(command_line, timeout)
                    CTB.save_result(result_c)
                    CTB.save_log(command_line)
                    CTB.save_log(result_c)
                    time.sleep(10)
        
        if action == 2:
            while command_line == "error":
                command_line = baidu_chatglm2.chat_with_baidu_sql(ip)
            command_line = command_line.replace("\n", "")
            result_c = commandrun.run_command_with_timeout(command_line, timeout)
            CTB.save_result(result_c)
            CTB.save_log(command_line)
            CTB.save_log(result_c)

        if action == 3:
            xss_path = os.getcwd()
            xss_path = xss_path + "/xs1.py"
            python_exe_path = sys.executable
            print(python_exe_path)
            while command_line == "error":
                command_line = baidu_chatglm2.chat_with_baidu_xss(ip, xss_path, python_exe_path)
            command_line = command_line.replace("\n", "")
            result_c = commandrun.run_command_with_timeout(command_line, timeout)
            CTB.save_result(result_c)
            CTB.save_log(command_line)
            CTB.save_log(result_c)

        # out_to_file = result.stdout

        # with open("scan_port_list.txt", "w") as output_file:
        #     output_file.write(out_to_file)
        self.state = 2

        if self.state == self.goal_state:
            reward = 1.0
            done = True
        else:
            reward = 0.0
            done = False

        return self.state, reward, done

    def reset(self):

        self.state = [0,0,0,0,0]
        return self.state

    def render(self, mode='test'):
        print(f"Current State: {self.state}")

env = Network_explorer()
