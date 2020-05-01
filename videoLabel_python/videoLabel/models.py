from django.db import models

# Create your models here.
# 用户表videolabel_userdb
class  userDB(models.Model):
    id = models.AutoField(primary_key=True) # 该字段可以不写，它会自动补全
    user_name = models.CharField(max_length=20)
    user_password = models.CharField(max_length=50)

    def __str__(self):  # 重写直接输出类的方法
        return "<user:{id=%s,user_name=%s,user_password=%s}>"\
               %(self.id,self.user_name,self.user_password)

# 用户表videolabel_user_videodb
class  user_videoDB(models.Model):
    user_id = models.IntegerField()
    video_id = models.IntegerField()

    def __str__(self):
        return "<user_video:{user_id=%d,video_id=%d}>"\
               %(self.user_id,self.video_id)

# 用户表videolabel_user_videodb
class  videoDB(models.Model):
	id = models.AutoField(primary_key=True) # 该字段可以不写，它会自动补全
	video_name = models.CharField(max_length=25)
	action_label = models.BooleanField(default=False)
	object_label = models.BooleanField(default=False)
	fps = models.FloatField()
	frame_num = models.IntegerField()
	firstFrame = models.TextField(default="")

	def __str__(self):
		return "<video:{id=%s,video_name=%s,fps=%f,frame_num=%d}>"\
            	%(self.id,self.video_name,self.fps,self.frame_num)
