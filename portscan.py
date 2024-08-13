import queue  # queue模块提供了线程安全的队列数据结构的实现，用于在多线程环境中进行线程间的数据交换和通信
import socket  # 实现网络编程模块
import threading  # threading模块提供了创建和管理线程的功能
import argparse
import re
import os
import numpy
from scapy.layers.inet import IP, TCP
from scapy.sendrecv import sr, sr1


def tcp_scan(ip, port):
    """
    功能介绍：
        通过TCP connect进行端口扫描，需要用户输入ip,port,
    函数介绍:
        portscan_print(ip)                              #结果排序打印
        portscan_fun(ip)                          #线程分配函数
        portscan_tcp_connect(ip, p)                      #扫描功能实现
        portscan_threadnum(ip,num=10)                   #控制线程数量
        Portscan_portlist(ip,userport)                  #扫描端口处理
    """

    def portscan_fun(ip):  # 队列扫描顺序模块
        while True:
            if q.empty():  # 判断队列是否为空
                break
            else:
                port = q.get()  # 取出一个端口
                portscan_tcp_connect(ip, port)

    def portscan_tcp_connect(ip, p):  # TCP connect功能实现
        try:  # try...except...异常函数
            port = int(p)
            # socket模块是Python标准库中用于进行网络编程的模块。
            # socket.socket()
            # 函数用于创建一个新的套接字对象。它接受两个参数，分别是地址簇（Address
            # Family）和套接字类型（Socket
            # Type）。
            # socket.AF_INET是地址簇的参数，表示使用IPv4地址族。
            # socket.SOCK_STREAM是套接字类型的参数，表示使用TCP协议进行通信。
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 用于创建套接字（socket）对象的接口，创建一个基于TCP的IPv4套接字对象
            if port == 3306 or port == 22 or port == 23 or port == 1521:  # 端口为3306、22、23、1521时设置超时时间为4秒
                s.settimeout(4)  # 3306端口通常用于MySQL数据库服务；22端口通常用于SSH（Secure Shell）远程登录协议；
            else:  # 23端口通常用于Telnet远程登录协议；1521端口通常用于Oracle数据库服务
                s.settimeout(1)
            s.connect((ip, port))  # connect()函数接受一个元组参数，尝试与指定的目标建立 TCP 连接
            openport_list.append(port)  # 将扫描结果中开放的端口号添加到 openport_list 列表
        except Exception as e:  # Exception所有类型的异常
            closeport_list.append(port)  # closeport_list列表用于存储连接失败或关闭的端口号
        finally:
            s.close()

    def portscan_print(ip):  # 打印函数，排序
        openport_list.sort()  # openport_list（开放端口列表）进行升序排序
        for i in openport_list:  # 输出开放端口
            print(ip + "\t" + str(i) + " open(TCP)\t\t")
        closeport_list.sort()  # closeport_list（关闭端口）进行升序排序
        for i in closeport_list:  # 输出关闭端口
            print(ip + "\t" + str(i) + " close(TCP)")

    def portscan_threadnum(ip, num=10):  # 控制线程函数
        thread_joinlist = []
        for i in range(0, num):  # 控制线程数
            new_thread = threading.Thread(target=portscan_fun,
                                          args=(ip,))  # 多线程模块下的Thread父类继承函数，父类函数：portscan_fun，传入参数ip
            new_thread.start()  # 运行新线程
            thread_joinlist.append(new_thread)  # 将新线程加入thread_joinlist列表
        for i in thread_joinlist:
            i.join()  # 循环等待每个线程完成任务，之后在进行打印工作

    def portscan_portlist(ip, threadnum, userport):  # 端口处理函数
        global q
        global openport_list
        global closeport_list
        q = queue.Queue()  # 创建一个队列对象，用于存储端口
        openport_list = []  # 创建一个空列表，用于存储开放的端口
        closeport_list = []  # 创建一个空列表，用于存储关闭的端口
        if userport:  # 如果指定了端口
            if ',' in userport:  # 如果端口是以逗号分隔的多个端口
                ports = userport.split(',')  # 将端口字符串按逗号分隔成列表
            elif '-' in userport:  # 如果端口是以连字符表示的范围
                ports = userport.split('-')  # 将端口字符串按连字符分隔成列表
                tmpports = []
                [tmpports.append(i) for i in range(int(ports[0]), int(ports[1]) + 1)]  # 将连续范围内的端口添加到临时列表
                ports = tmpports  # 将范围内的所有端口赋值给ports
            else:  # 如果端口是单个端口
                ports = [userport]  # 将端口作为单个元素的列表
        else:
            print('默认端口')  # 如果用户没有指定端口，则使用默认端口列表
            ports = [21, 22, 23, 53, 80, 111, 139, 161, 389, 443, 445, 512, 513, 514,
                     873, 1025, 1433, 1521, 3128, 3306, 3311, 3312, 3389, 5432, 5900,
                     5984, 6082, 6379, 7001, 7002, 8000, 8080, 8081, 8090, 9000, 9090,
                     8888, 9200, 9300, 10000, 11211, 27017, 27018, 50000, 50030, 50070]
        [q.put(i) for i in ports]  # 将端口逐个加入队列
        portscan_threadnum(ip, threadnum)
        portscan_print(ip)  # 打印输出函数

    thread = 10
    threadnum = thread
    portscan_portlist(ip, threadnum, port)


def syn_scan(ip, ports):
    """
    功能介绍：
    通过SYN进行端口扫描，需要用户输入ip,port,线程数(默认10)
    """

    def Portscan_Threadfun(ip):
        while True:
            if q.empty():  # 判断队列是否为空
                break
            else:
                port = q.get()  # 取出一个端口
                Portscan_SYN(ip, port)

    def Portscan_SYN(ip, port):
        try:
            temp = sr(IP(dst=ip) /
                      TCP(dport=(int(port)), flags='S'),
                      timeout=2, verbose=False)
            if temp[0].res:
                result = temp[0].res  # temp分回复和无回显
                if result[0][1].payload.flags == 'SA':
                    openport_list.append(port)
                    return 1
                else:
                    closeport_list.append(port)
            else:
                closeport_list.append(port)
                return 0
        except:
            closeport_list.append(port)
            return 0

    def Portscan_print(ip):  # 打印函数，排序
        openport_list.sort()
        for i in openport_list:
            print(ip + "\t" + str(i) + " open(SYN)\t\t")
        closeport_list.sort()
        for i in closeport_list:
            print(ip + "\t" + str(i) + " close(SYN)")

    def Portscan_threadnum(ip, num=10):  # 控制线程函数
        thread_joinlist = []
        for i in range(0, num):  # 控制线程数
            new_thread = threading.Thread(target=Portscan_Threadfun, args=(ip,))
            new_thread.start()
            thread_joinlist.append(new_thread)
        for i in thread_joinlist:
            i.join()  # 循环等待每个线程完成任务，之后在进行打印工作

    def Portscan_synport(ip, userport, threadnum=10):
        global q
        global openport_list
        global closeport_list
        openport_list = []
        closeport_list = []
        q = queue.Queue()
        if userport:
            if ',' in userport:
                ports = userport.split(',')
            elif '-' in userport:
                ports = userport.split('-')
                tmpports = []
                [tmpports.append(i) for i in range(int(ports[0]), int(ports[1]) + 1)]
                ports = tmpports
            else:
                ports = [userport]
        else:
            print('Default Ports')
            ports = [21, 22, 23, 53, 80, 111, 139, 161, 389, 443, 445, 512, 513, 514,
                     873, 1025, 1433, 1521, 3128, 3306, 3311, 3312, 3389, 5432, 5900,
                     5984, 6082, 6379, 7001, 7002, 8000, 8080, 8081, 8090, 9000, 9090,
                     8888, 9200, 9300, 10000, 11211, 27017, 27018, 50000, 50030, 50070]

        [q.put(i) for i in ports]  # 将端口加入队列
        Portscan_threadnum(ip, threadnum)
        Portscan_print(ip)

    Portscan_synport(ip, ports)


def udp_scan(ip, port):
    def udp_scan(ip, port):
        open_ports = []  # 存储开放的端口
        closed_ports = []  # 存储关闭的端口
        ignored_ports = []  # 存储被忽略的端口
        no_response_ports = []  # 存储无响应的端口
        ports2 = 0
        if port:
            if ',' in port:
                ports1 = port.split(',')
            elif '-' in port:
                ports2 = port.split('-')
            else:
                ports1 = [port]
        else:
            print('默认端口')
            ports = [21, 22, 23, 53, 80, 111, 139, 161, 389, 443, 445, 512, 513, 514,
                     873, 1025, 1433, 1521, 3128, 3306, 3311, 3312, 3389, 5432, 5900,
                     5984, 6082, 6379, 7001, 7002, 8000, 8080, 8081, 8090, 9000, 9090,
                     8888, 9200, 9300, 10000, 11211, 27017, 27018, 50000, 50030, 50070]
        if ports2:
            # 创建UDP socket
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # 设置超时时间（单位：秒）
            udp_socket.settimeout(1)

            for port in range(int(ports2[0]), int(ports2[1]) + 1):
                try:
                    # 发送数据到目标IP和端口
                    udp_socket.sendto(b"", (ip, port))

                    # 接收数据（缓冲区大小为1024字节）
                    data, addr = udp_socket.recvfrom(1024)

                    # 端口开放
                    open_ports.append(port)
                    print(f"port {port}: open(UDP)")

                except socket.timeout:
                    # 端口无响应
                    no_response_ports.append(port)
                    print(f"port {port}: no-responce(UDP)")

                except socket.error:
                    # 端口关闭（其他错误）
                    closed_ports.append(port)
                    print(f"port {port}: close（UDP other error）")

                except:
                    # 端口被忽略
                    ignored_ports.append(port)
                    print(f"port {port}: igron(UDP)")
        else:
            for port in ports1:
                # 创建UDP socket
                udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

                # 设置超时时间（单位：秒）
                udp_socket.settimeout(1)
                try:
                    # 发送数据到目标IP和端口
                    udp_socket.sendto(b"", (ip, port))

                    # 接收数据（缓冲区大小为1024字节）
                    data, addr = udp_socket.recvfrom(1024)

                    # 端口开放
                    open_ports.append(port)
                    print(f"port {port}: open(UDP)")

                except socket.timeout:
                    # 端口无响应
                    no_response_ports.append(port)
                    print(f"port {port}: no-responce(UDP)")

                except socket.error:
                    # 端口关闭（其他错误）
                    closed_ports.append(port)
                    print(f"port {port}: close（UDP other error）")

                except:
                    # 端口被忽略
                    ignored_ports.append(port)
                    print(f"port {port}: igron(UDP)")

        print("-" * 30)
        print(f"UDP scan success，{ip}reults is")
        print(f"open ports: {open_ports}")
        print(f"close ports: {closed_ports}")
        print(f"igron: {ignored_ports}")
        print(f"no-responce: {no_response_ports}")
        print("-" * 30)

        # 关闭UDP socket
        udp_socket.close()

    udp_scan(ip, port)  # 执行UDP端口扫描


def fin_scan(ip, port):
    """
    通过设置flags位为'FIN',不回复则表示端口开启，回复并且回复的标志位为RST表示端口关闭
    """
    port1 = numpy.zeros(1, dtype=int, order='C')
    port2 = numpy.zeros(1, dtype=int, order='C')
    if port:
        if ',' in str(port):
            port1 = port.split(',')
        elif '-' in str(port):
            port2 = port.split('-')
        else:
            port2 = [port]

    if len(port):
        for port in port1:
            p = IP(dst=ip) / TCP(dport=int(port), flags="F")
            ans = sr1(p, timeout=1, verbose=1)
            print(ans)
            if ans is None:
                print(ip, "port", port, "open(FIN)")
            elif ans is not None and ans[TCP].flags == 'RA':
                ans.display()
                print(ip, "port", port, "close(FIN)")
    else:
        for port in range(int(port2[0]), int(port2[1]) + 1):
            p = IP(dst=ip) / TCP(dport=int(port), flags="F")
            ans = sr1(p, timeout=1, verbose=1)
            print(ans)
            if ans is None:
                print(ip, "port", port, "close(FIN)")
            elif ans is not None and ans[TCP].flags == 'RA':
                ans.display()
                print(ip, "port", port, "close(FIN)")






#
# def main():
#     print('(TCP SYN UDP FIN )')
#     command = input("请输入指令:")
#     ip = input('请输入IP地址：')
#     port = input("端口：")
#
#     if command == "TCP":
#         tcp_scan(ip, port)
#     elif command == "SYN":
#         syn_scan(ip, port)
#     elif command == "UDP":
#         udp_scan(ip, port)
#     elif command == "FIN":
#         fin_scan(ip, port)
#     elif command == "":
#         # 没有输入命令时默认按照顺序进行扫描
#         tcp_scan(ip, port)
#         syn_scan(ip, port)
#         udp_scan(ip, port)
#         fin_scan(ip, port)
#     else:
#         print("无效的命令")


# def main():
#     parser = argparse.ArgumentParser(description='My script description')
#
#     # 添加一个位置参数，用于接收指令（TCP、SYN、UDP、FIN）
#     command = parser.add_argument('command', type=str, choices=['TCP', 'SYN', 'UDP', 'FIN'], help='Type of scan')
#
#     # 添加一个参数，用于接收端口范围，格式为80-100
#     port = parser.add_argument('port_range', type=str, help='Port range in the format of start-end')
#
#     # 添加一个参数，用于接收IP地址
#     ip = parser.add_argument('ip_address', type=str, help='IP address')
#
#     args = parser.parse_args()
#
#     if command == "TCP":
#         tcp_scan(ip, port)
#     elif command == "SYN":
#         syn_scan(ip, port)
#     elif command == "UDP":
#         udp_scan(ip, port)
#     elif command == "FIN":
#         fin_scan(ip, port)
#     elif command == "":
#         # 没有输入命令时默认按照顺序进行扫描
#         tcp_scan(ip, port)
#         syn_scan(ip, port)
#         udp_scan(ip, port)
#         fin_scan(ip, port)
#     else:
#         print("无效的命令")

def main():
    parser = argparse.ArgumentParser(description='My script description')

    # 添加一个位置参数，用于接收指令（TCP、SYN、UDP、FIN）
    parser.add_argument('command', type=str, choices=['TCP', 'SYN', 'UDP', 'FIN', 'A'], help='Type of scan')

    # 添加一个参数，用于接收端口范围，格式为80-100
    parser.add_argument('port_range', type=str, help='Port range in the format of start-end')

    # 添加一个参数，用于接收IP地址
    parser.add_argument('ip_address', type=str, help='IP address')

    args = parser.parse_args()

    if args.command == "TCP":
        tcp_scan(args.ip_address, args.port_range)
    elif args.command == "SYN":
        syn_scan(args.ip_address, args.port_range)
    elif args.command == "UDP":
        udp_scan(args.ip_address, args.port_range)
    elif args.command == "FIN":
        fin_scan(args.ip_address, args.port_range)
    elif args.command == "A":
        # 没有输入命令时默认按照顺序进行扫描
        tcp_scan(args.ip_address, args.port_range)
        syn_scan(args.ip_address, args.port_range)
        udp_scan(args.ip_address, args.port_range)
        fin_scan(args.ip_address, args.port_range)
    else:
        print("无效的命令")


if __name__ == "__main__":
    main()
