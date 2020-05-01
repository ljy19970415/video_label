<template>

  <div class="is-background">
    <div style="background-color: #1da1f2; height:50px;  width:100%; " >
      <div style="display: table-cell;  line-height:60px;">
          <img src="../assets/logo1.png"  style="height:33px;width:145px;margin-left:20px;margin-top:10px">
        <span style="font-size:20px;color:#E0FFFF">&#160; 数据标注平台</span>
      </div>
    </div>
    <div style="background-color: #1da1f2; height:10px;  width:100%; " ></div>
    <el-container style="height: 100%;" direction="vertical">
      <el-aside width="200px"></el-aside>
      <el-main :gutter="10">
        <el-row style="margin-top:2px">
          <el-col :span="3" style="margin-left:25%"><input id="video" type="file" accept="video/*"/></el-col>
          <el-col :span="4"><el-button type="primary" @click="uploadVideo" size="small" >上传<i class="el-icon-upload el-icon--right"></i></el-button></el-col>
          <el-col :span="6" style="margin-left:2%">
            <el-select v-model="showWhat" placeholder="请选择">
              <el-option
                v-for="item in show_options"
                :key="item.value"
                :label="item.label"
                :value="item.value">
              </el-option>
            </el-select>
          </el-col>
        </el-row>
        <div v-if="showWhat===0" v-for="item in unlabelAction" style="margin-top:40px">
          <el-col :span="6">
            <showDB v-bind="item" v-on:removeVideo="removeVideo"></showDB>
          </el-col>
        </div>
        <div v-if="showWhat===1" v-for="item in unlabelObject" style="margin-top:40px">
         <el-col :span="6">
           <showDB v-bind="item" v-on:removeVideo="removeVideo"></showDB>
         </el-col>
       </div>
        <div v-if="showWhat===2" v-for="item in labelAction" style="margin-top:40px">
          <el-col :span="6">
            <showDB v-bind="item" v-on:removeVideo="removeVideo"></showDB>
          </el-col>
        </div>
        <div v-if="showWhat===3" v-for="item in labelObject" style="margin-top:40px">
          <el-col :span="6">
            <showDB v-bind="item" v-on:removeVideo="removeVideo"></showDB>
          </el-col>
        </div>

      </el-main>
      <el-aside width="200px"></el-aside>
    </el-container>
      <br />  <br />    <br />  <br />    <br />  <br />
      <br />  <br />    <br />  <br />    <br />  <br />
      <br />  <br />    <br />  <br />    <br />  <br />
      <br />  <br />    <br />  <br />    <br />  <br />
    <br />  <br />    <br />  <br />    <br />  <br />
    <br />  <br />    <br />  <br />    <br />  <br />
  </div>
</template>

<script>
  import showDB from './showDB'
    export default {
      name: "personalPage",
      data()
      {
        return{
          unlabelAction:[],
          labelAction:[],
          unlabelObject:[],
          labelObject:[],
          uid:this.$route.query.uid,
          islabel:'unlabel',
          labelType:'action',
          showWhat:0,
          show_options:[{value:0, label:'未标注过事件的视频'},{value:1, label:'未标注过对象的视频'},{value:2, label:'已标注过事件的视频'},{value:3, label:'已标注过对象的视频'}]
        };
      },
      components:{
        showDB
      },
      mounted:function()
      {
        let _this=this
        let obj={user_id:this.$route.query.uid}
        var jsontext = encodeURIComponent(JSON.stringify(obj));
        this.$reqs.post('/personInitial/?jsontext='+jsontext).then(res=>{
          _this.unlabelAction=res.data.unlabelAction
          _this.labelAction=res.data.labelAction
          _this.unlabelObject=res.data.unlabelObject
          _this.labelObject=res.data.labelObject
        })
      },
      methods:
        {
          removeVideo(obj)
          {
            var _this=this
            let tmp={user_id:obj.user_id,video_id:obj.video_id}
            var jsontext = encodeURIComponent(JSON.stringify(tmp));
            this.$reqs.post('/removeVideo/?jsontext='+jsontext).then(res=>{
              if(res.data.action_label===true){_this.labelAction.splice(obj,1)}
              else{_this.unlabelAction.splice(obj,1)}
              if(res.data.object_label===true){_this.labelObject.splice(obj,1)}
              else{_this.unlabelObject.splice(obj,1)}
              _this.$message.success("移除数据集成功~");
            })
          },
          uploadVideo(){
            let _this=this
            let form_data = new FormData();
            var video = document.getElementById('video').files[0];
            form_data.append('file',video);
            form_data.append('user',this.uid);
            this.$reqs.post('/uploadVideo/',form_data).then(res=>{
              this.$message.success('成功上传文件~')
              _this.unlabelAction.push(res.data.unlabelAction)
              _this.unlabelObject.push(res.data.unlabelObject)
            })
          }
        }
    }
</script>

<style scoped>
  .is-background{

    background:url(../assets/background-t.jpg)  no-repeat center center;
    background-size:cover;
    background-attachment:fixed;
    background-color:#CCCCCC;
  }

</style>
