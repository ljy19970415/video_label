from .models import user_videoDB,videoDB
from .views import videoImageLabel
from django.shortcuts import render,HttpResponse,render_to_response
import json
import os
import cv2
import shutil

class video(object):
	@staticmethod
	def removeVideo(request):
		jsontext=request.GET.get('jsontext')
		user_id=str(json.loads(jsontext)["user_id"])
		video_id=int(json.loads(jsontext)["video_id"])
		video=videoDB.objects.get(id=video_id)
		data={'action_label':video.action_label,'object_label':video.object_label}
		videoDB.objects.get(id=video_id).delete()
		user_videoDB.objects.get(video_id=video_id).delete()
		#删除此视频文件夹
		curPath = os.path.abspath(os.path.dirname(__file__))
		rootPath = curPath[:curPath.find("videoLabel_python\\")+len("videoLabel_python\\")]+'\\user_video\\'  # 获取myProject，也就是项目的根路径
		imgPath=rootPath+'user'+user_id+'\\video'+str(video_id)
		shutil.rmtree(imgPath)
		sample = json.dumps(data)  # json.dumps()把一个Python对象编，码转换成Json字符串。
		return HttpResponse(sample,content_type="application/json")
	@staticmethod
	def uploadVideo(request):
		video=request.FILES.get('file') #获取视频文件
		user_id=request.POST.get('user') #获取用户id
		#将视频文件写入文件夹中
		curPath = os.path.abspath(os.path.dirname(__file__))
		rootPath = curPath[:curPath.find("videoLabel_python\\")+len("videoLabel_python\\")]+'\\user_video\\' # 获取myProject，也就是项目的根路径
		tmpPath=rootPath+'user'+user_id+'\\tmp\\'+video.name
		f=open(tmpPath,'wb')
		for chunk in video.chunks():
			f.write(chunk)
		f.close()
		cap = cv2.VideoCapture(tmpPath)
		isOpened = cap.isOpened()
		newVideo = videoDB()
		newVideo.video_name=video.name
		newVideo.action_label=False
		newVideo.object_label=False
		newVideo.fps=cap.get(cv2.CAP_PROP_FPS)
		newVideo.frame_num=0
		newVideo.save()
		#更新user_video
		user_video=user_videoDB()
		user_video.user_id=user_id
		user_video.video_id=newVideo.id
		user_video.save()
		#将图片写入文件夹
		imgPath=rootPath+'user'+user_id+'\\video'+str(newVideo.id)
		os.mkdir(imgPath)
		i=0
		pictures=[]
		while(isOpened):  #当视频被打开了
			(flag,frame) = cap.read() #读取每一张 flag<读取是否成功> frame<内容>
			if flag == True:  #读取成功的话且符合帧率
				pictures.append({'id':i,'frame':videoImageLabel.image_to_base64(frame)})
				i+=1
			else:  #读取失败则跳出循环
				break
		with open(imgPath+'\\frames.json', "w", encoding='utf-8') as f:
			json.dump(pictures, f,indent=2,sort_keys=True, ensure_ascii=False)
		f.close()
        #更新frame_num及firstFrame
		newVideo.frame_num=i
		newVideo.firstFrame=pictures[0]['frame']
		newVideo.save()
		#生成新视频信息
		data={
		'unlabelAction':{'video_id':newVideo.id,'user_id':int(user_id),'mysrc':newVideo.firstFrame,'isObject':False},
		'unlabelObject':{'video_id':newVideo.id,'user_id':int(user_id),'mysrc':newVideo.firstFrame,'isObject':True}
		}
		sample = json.dumps(data)  # json.dumps()把一个Python对象编，码转换成Json字符串。
		return HttpResponse(sample,content_type="application/json")