import os

path = ".\\result"
lists=os.listdir(path)
lists.sort(key=lambda fn: os.path.getmtime(path + "\\" + fn)
          if not os.path.isdir(path + "\\" + fn) else 0)
file = os.path.join(path, lists[-1])
print("完整路径", file)