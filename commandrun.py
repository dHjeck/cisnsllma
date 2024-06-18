import subprocess
import threading
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


#创建一个计时的指令执行工具
def run_command_with_timeout(command, timeout):
    #run不直接支持超时
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    timer = threading.Timer(timeout, process.kill())
    timer.start()

    try:
        stdout, stderr = process.communicate()
        timer.cancel()
    except subprocess.TimeoutExpired:
        #线程超时
        process.kill()
        stdout, stderr = process.communicate()
        logging.warning(f"Command {command} timed out")
    finally:
        process.stdout.close()
        process.stderr.close()

        result = stdout.decode() + '\n' + stderr.decode()
        return result

# def run_command(command):
#     process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
#     output, error = process.communicate()
#     result = output.decode() + '\n' + error.decode()
#     return result