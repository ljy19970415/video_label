from django.shortcuts import render,HttpResponse,render_to_response
import json
import cv2
import base64
import numpy as np
from django.http import FileResponse #传输文件
import zipfile  #生成压缩文件
import os
from .models import videoDB #数据库类
import shutil #删除文件

# Create your views here.
class videoImageLabel(object):
    @staticmethod
    def image_to_base64(image_np):     
        image = cv2.imencode('.jpg',image_np)[1]    
        image_code = str(base64.b64encode(image))[2:-1]
        return 'data:image/jpeg;base64,'+image_code
    @staticmethod
    def base64_to_image(base64_code):
        # base64解码    
        img_data = base64.b64decode(base64_code)    
        # 转换为np数组    
        img_array = np.fromstring(img_data, np.uint8)
        # 转换成opencv可用格式    
        img = cv2.imdecode(img_array, cv2.COLOR_RGB2BGR)     
        return img
    @staticmethod
    def writeAllFileToZip(absDir,zipFile):
        for f in os.listdir(absDir): 
            absFile=os.path.join(absDir,f)
            if os.path.isdir(absFile):
                relFile=absFile[len(os.getcwd())+2:]
                zipFile.write(relFile)
                videoImageLabel.writeAllFileToZip(absFile,zipFile)
            else:
                relFile=absFile[len(os.getcwd())+2:] #改成相对路径
                zipFile.write(relFile)
        return
    @staticmethod
    def clearDir(dirPath):
        shutil.rmtree(dirPath)
        os.mkdir(dirPath)
    @staticmethod
    def videoToImage(request):
        jsontext=request.GET.get('jsontext')
        user_id=json.loads(jsontext)["user_id"]
        video_id=json.loads(jsontext)["video_id"]
        ufps=int(json.loads(jsontext)["fps"])
        #初始化变量
        images=[]  #图片
        labels=[]  #图片的标注信息
        frame_map=[] #用户帧和真实帧的对应信息
        options=[{ "value":"other", "label":"other"},{ "value":"people", "label":"people"},{ "value":"basketball", "label":"basketball"}] #可选标签
        #获取视频的fps信息
        video = videoDB.objects.get(id=video_id)
        fps=video.fps
        #读取存储图片base64编码的json文件
        curPath = os.path.abspath(os.path.dirname(__file__))
        rootPath = curPath[:curPath.find("videoLabel_python\\")+len("videoLabel_python\\")]+'\\user_video\\'  # 获取myProject，也就是项目的根路径
        imgPath=rootPath+'user'+str(user_id)+'\\video'+str(video_id)+'\\frames.json'
        with open(imgPath,'r',encoding='utf8')as f:
            frames = json.load(f)
            a = 1
            if(ufps!=0 and ufps<fps):
                a=round(fps/ufps)
            for i in range(len(frames)):
                if i%a==0:
                    images.append([frames[i]['frame']])
                    labels.append([])
                    frame_map.append(i)
        f.close()
        #将读取的图片返回给前端
        data = {}
        data['images'] = images
        data['labels'] = labels
        data['options'] = options
        data['frame_map'] = frame_map
        sample = json.dumps(data)  # json.dumps()把一个Python对象编，码转换成Json字符串。
        return HttpResponse(sample,content_type="application/json")
    @staticmethod
    def keyActionInitial(request):
        jsontext=request.GET.get('jsontext')
        user_id=json.loads(jsontext)["user_id"]
        video_id=json.loads(jsontext)["video_id"]
        ufps=int(json.loads(jsontext)["fps"])
        data = {}
        images=[]  #图片
        frame_options=[] #帧选项
        labels=[] #保存好的标注
        frame_map=[] #frame[i]为用户看到的第i帧对应的原视频的帧
        options=[{ "value":"other", "label":"other"},{ "value":"fight", "label":"fight"},{ "value":"play cards", "label":"play cards"}] #可选标签
        #获取视频的fps信息
        video = videoDB.objects.get(id=video_id)
        fps=video.fps
        #读取存储图片base64编码的json文件
        curPath = os.path.abspath(os.path.dirname(__file__))
        rootPath = curPath[:curPath.find("videoLabel_python\\")+len("videoLabel_python\\")]+'\\user_video\\'  # 获取myProject，也就是项目的根路径
        imgPath=rootPath+'user'+str(user_id)+'\\video'+str(video_id)+'\\frames.json'
        with open(imgPath,'r',encoding='utf8')as f:
            frames = json.load(f)
            a = 1
            count=0
            if(ufps!=0 and ufps<fps):
                a=round(fps/ufps)
            for i in range(len(frames)):
                if i%a==0:
                    images.append([frames[i]['frame']])
                    labels.append([])
                    frame_options.append({"value":count,"label":str(count)})
                    frame_map.append(i)
                    count+=1
        f.close()
        #将结果返回给前端 
        data['images'] = images
        data['options'] = options
        data['frame_options'] = frame_options
        data['labels']=labels
        data['frame_map']=frame_map
        data['frameNum']=i #视频总帧数
        sample = json.dumps(data)  # json.dumps()把一个Python对象编，码转换成Json字符串。
        return HttpResponse(sample,content_type="application/json")
    @staticmethod
    def savekeyActions(request):
        jsontext=request.GET.get('jsontext')
        #labels[i]表示用户第i帧中的所有拉框
        #每个拉框为{actionID,x, y, x2,y2,label,beginFrame,endFrame,frameID}
        labels=json.loads(jsontext)["labels"]
        proportion=round(float(json.loads(jsontext)["proportion"])) #比例
        count=json.loads(jsontext)["count"] #事件映射
        actionNum=int(json.loads(jsontext)["actionNum"]) #事件总个数
        frameNum=int(json.loads(jsontext)["frameNum"]) #原视频总帧数
        frame_map=json.loads(jsontext)["frame_map"] #frame_map[i]表示用户帧数i对应的原视频帧
        user_id=json.loads(jsontext)["user_id"]
        video_id=json.loads(jsontext)["video_id"]

        curPath = os.path.abspath(os.path.dirname(__file__))
        rootPath = curPath[:curPath.find("videoLabel_python\\")+len("videoLabel_python\\")]+'\\user_video\\' # 获取myProject，也就是项目的根路径
        imgPath=rootPath+'user'+str(user_id)+'\\tmp'
        framePath=rootPath+'user'+str(user_id)+'\\video'+str(video_id)+'\\frames.json'
        zipPath=os.path.abspath(rootPath+'user'+str(user_id)+'\\events.zip')
        #设置视频事件已标注
        video = videoDB.objects.get(id=video_id)
        video.action_label=True
        video.save()
        #清空tmp文件夹
        videoImageLabel.clearDir(imgPath)
        #初始化结果数组及位置记录数组
        result=[]
        tmp_pos=[]
        for i in range(actionNum):
            result.append({
                'actionID':i,
                'label':"",
                'beginFrame':0,
                'endFrame':0,
                'position':[]
                })
            tmp_pos.append({"beginFrame":0,"endFrame":0,"x":0,"y":0,"x2":0,"y2":0})
        #遍历得result
        for i in range(len(labels)): #对每一帧的事件进行遍历
            for j in labels[i]:
                actualID=count.index(j['actionID'])
                uendFrame=False
                if i==len(labels)-1:
                    uendFrame=True
                if result[actualID]['label']=="": #若第一次遇见该事件，则初始化事件信息
                    result[actualID]['label']=j['label']
                    result[actualID]['beginFrame']=frame_map[j['beginFrame']]
                    tmp_pos[actualID]['beginFrame']=result[actualID]['beginFrame']
                    if not uendFrame:
                        tmp_pos[actualID]['endFrame']=frame_map[j['frameID']+1]-1
                    if j['endFrame']!=len(labels)-1:
                        result[actualID]['endFrame']=frame_map[j['endFrame']+1]-1
                    tmp_pos[actualID]['x']=round(j['x']*proportion)
                    tmp_pos[actualID]['y']=round(j['y']*proportion)
                    tmp_pos[actualID]['x2']=round(j['x2']*proportion)
                    tmp_pos[actualID]['y2']=round(j['y2']*proportion)
                else: #若第二次遇见事件，则检查位置
                    if( tmp_pos[actualID]['x']==round(j['x']*proportion) and tmp_pos[actualID]['y']==round(j['y']*proportion) and 
                        tmp_pos[actualID]['x2']==round(j['x2']*proportion) and tmp_pos[actualID]['y2']==round(j['y2']*proportion)):
                        if not uendFrame:
                            tmp_pos[actualID]['endFrame']=frame_map[j['frameID']+1]-1
                    else:
                        result[actualID]['position'].append({"beginFrame":tmp_pos[actualID]['beginFrame'],"endFrame":frame_map[j['frameID']]-1,"x":tmp_pos[actualID]['x'],"y":tmp_pos[actualID]['y'],"x2":tmp_pos[actualID]['x2'],"y2":tmp_pos[actualID]['y2']})
                        tmp_pos[actualID]['beginFrame']=frame_map[j['frameID']]
                        if not uendFrame:
                            tmp_pos[actualID]['endFrame']=frame_map[j['frameID']+1]-1
                        tmp_pos[actualID]['x']=round(j['x']*proportion)
                        tmp_pos[actualID]['y']=round(j['y']*proportion)
                        tmp_pos[actualID]['x2']=round(j['x2']*proportion)
                        tmp_pos[actualID]['y2']=round(j['y2']*proportion)
                if uendFrame: #若已到用户视角最后一帧，则补全位置到原视频帧尾
                    result[actualID]['endFrame']=frameNum
                    tmp_pos[actualID]['endFrame']=frameNum
        for i in range(actionNum):
            result[i]['position'].append(tmp_pos[i])
        with open(imgPath+'\\Action.json', "w", encoding='utf-8') as f:
            json.dump(result, f,indent=2,sort_keys=True, ensure_ascii=False)#写为多行
        #将事件包含的所有帧写入tmp文件
        for i in range(actionNum):
            #截取区域所有的图片写入tmp\\eventx-label文件夹中
            eventPath=imgPath+'\\event'+str(i)+'-'+result[i]['label']
            os.mkdir(eventPath)
            with open(framePath,'r',encoding='utf8')as fp:
                frames = json.load(fp)
                for j in range(result[i]['beginFrame'],result[i]['endFrame']+1):
                    img=videoImageLabel.base64_to_image(frames[j]['frame'].replace('data:image/jpeg;base64,',''))
                    cv2.imwrite(eventPath+'\\frame'+str(j)+'.jpg',img)
        #生成压缩文件并返回给前端下载
        zipFile = zipfile.ZipFile(zipPath, 'w', zipfile.ZIP_DEFLATED)
        videoImageLabel.writeAllFileToZip(imgPath,zipFile)
        zipFile.close()
        file=open(zipPath,"rb")
        response = HttpResponse(file, content_type='application/x-zip-compressed ')
        # response['Content-Disposition'] = 'attachment;filename="{0}"'.format(the_file_name)
        response['Content-Disposition'] = 'attachment; filename=events.zip'
        file.close()
        return response
    @staticmethod
    def saveLabels(request):
        jsontext=request.GET.get('jsontext')
        user_id=json.loads(jsontext)["user_id"]
        video_id=json.loads(jsontext)["video_id"]
        labels=json.loads(jsontext)["labels"]
        proportion=float(json.loads(jsontext)["proportion"])
        frame_map=json.loads(jsontext)["frame_map"]
        #初始化写入文件路径
        curPath = os.path.abspath(os.path.dirname(__file__))
        rootPath = curPath[:curPath.find("videoLabel_python\\")+len("videoLabel_python\\")]+'\\user_video\\'  # 获取myProject，也就是项目的根路径
        imgPath=rootPath+'user'+str(user_id)+'\\tmp'
        framePath=rootPath+'user'+str(user_id)+'\\video'+str(video_id)+'\\frames.json'
        zipPath=os.path.abspath(rootPath+'user'+str(user_id)+'\\roi_labels.zip')
        #清空tmp文件夹
        videoImageLabel.clearDir(imgPath)
        #获得视频帧数
        video = videoDB.objects.get(id=video_id)
        fps=video.fps
        video.object_label=True
        video.save()
        #labels为所有图片的拉框信息，labels[i]表示第i+1张图片的信息，labels[i][0]为第i+1张图片的id，labels[i][1]为第i+1张图片的拉框信息
        #labels[i][1][j]为第i+1张图片第j+1个拉框的信息
        #labels[i][1][j]['x']为左上角x坐标，labels[i][1][j]['y']为左上角y坐标
        #labels[i][1][j]['x2']为右下角x坐标,labels[i][1][j]['y2']为右下角x坐标
        #labels[i][1][j]['label']为该拉框标签信息
        regionID=[]  #区域的id image_id-region-id
        regionLabel=[] #区域的标签
        with open(framePath,'r',encoding='utf8')as fp:
            frames = json.load(fp)
            for u,i in enumerate(frame_map):
                if len(labels[u])!=0: #若当前图片有标注信息
                        img=videoImageLabel.base64_to_image(frames[i]['frame'].replace('data:image/jpeg;base64,',''))
                        for j,region in enumerate(labels[u]):
                            roi=img[int(region['y']*proportion):int(region['y2']*proportion),int(region['x']*proportion):int(region['x2']*proportion)]
                            cv2.imwrite(imgPath+'\\'+str(i)+'-'+str(j)+'-'+str(region['label'])+'.jpg',roi)
                            regionID.append(str(i)+'-'+str(j))
                            regionLabel.append(region['label'])
        region={
        'regionID':regionID,
        'regionLabel':regionLabel
        }
        with open(imgPath+'\\regionLabels.json', "w", encoding='utf-8') as f:
            json.dump(region, f,indent=2,sort_keys=True, ensure_ascii=False)  # 写为多行
        #生成压缩文件并返回给前端下载
        zipFile = zipfile.ZipFile(zipPath, 'w', zipfile.ZIP_DEFLATED)
        videoImageLabel.writeAllFileToZip(imgPath,zipFile)
        zipFile.close()
        file=open(zipPath,"rb")
        response = HttpResponse(file, content_type='application/x-zip-compressed ')
        response['Content-Disposition'] = 'attachment; filename=roi_labels.zip'
        file.close()
        return response