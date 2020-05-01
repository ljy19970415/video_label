from .models import userDB,user_videoDB,videoDB
from django.shortcuts import render,HttpResponse,render_to_response
import json
import os

class user(object):
	@staticmethod
	def personInitial(request):
		print("personIntial")
		jsontext=request.GET.get('jsontext')
		user=json.loads(jsontext)["user_id"]
		user_int=int(user)
		data={
		'unlabelAction':[],
		'labelAction':[],
		'unlabelObject':[],
		'labelObject':[]
		}
		try:
			videos = user_videoDB.objects.filter(user_id=user)
		except userDB.DoesNotExist:
			sample = json.dumps(data)  # json.dumps()把一个Python对象编，码转换成Json字符串。
			return HttpResponse(sample,content_type="application/json")
		for i in videos:
			video=videoDB.objects.get(id=i.video_id)
			if not video.action_label:
				data['unlabelAction'].append({'video_id':i.video_id,'user_id':user_int,'mysrc':video.firstFrame,'isObject':False})
			else:
				data['labelAction'].append({'video_id':i.video_id,'user_id':user_int,'mysrc':video.firstFrame,'isObject':False})
			if not video.object_label:
				data['unlabelObject'].append({'video_id':i.video_id,'user_id':user_int,'mysrc':video.firstFrame,'isObject':True})
			else:
				data['labelObject'].append({'video_id':i.video_id,'user_id':user_int,'mysrc':video.firstFrame,'isObject':True})
		sample = json.dumps(data)
		return HttpResponse(sample,content_type="application/json")
	@staticmethod
	def register(request):
		jsontext=request.GET.get('jsontext')
		name=json.loads(jsontext)["user_name"]
		password=json.loads(jsontext)["user_password"]
		newUser = userDB()
		newUser.user_name=name
		newUser.user_password=password
		newUser.save()
		#创建用户文件夹
		curPath = os.path.abspath(os.path.dirname(__file__))
		rootPath = curPath[:curPath.find("videoLabel_python\\")+len("videoLabel_python\\")]+'\\user_video\\' # 获取myProject，也就是项目的根路径
		userPath=rootPath+'user'+str(newUser.id)
		tmpPath=userPath+'\\tmp'
		#os.mkdir(userPath)
		os.makedirs(tmpPath)
		sample = json.dumps({"data":"success"})  # json.dumps()把一个Python对象编，码转换成Json字符串。
		return HttpResponse(sample,content_type="application/json")
	@staticmethod
	def login(request):
		jsontext=request.GET.get('jsontext')
		name=json.loads(jsontext)["user_name"]
		password=json.loads(jsontext)["user_password"]
		try:
			person = userDB.objects.get(user_name=name)
		except userDB.DoesNotExist:
			sample = json.dumps({"data":"no_user"})  # json.dumps()把一个Python对象编，码转换成Json字符串。
			return HttpResponse(sample,content_type="application/json")
		if person.user_password!=password:
			sample = json.dumps({"data":"wrong_password"})  # json.dumps()把一个Python对象编，码转换成Json字符串。
			return HttpResponse(sample,content_type="application/json")
		else:
			sample = json.dumps({"data":"success","id":person.id})  # json.dumps()把一个Python对象编，码转换成Json字符串。
			return HttpResponse(sample,content_type="application/json")