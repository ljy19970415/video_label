<template>
  <el-container class="mycanvas-container">
    <div style="background-color: #1da1f2; height:50px;  width:100%; " >
      <div style="display: table-cell;  line-height:60px;">
        <router-link :to="{ name: 'personalPage', query:{user_id:this.$route.query.user_id}}">
          <img src="../assets/logo1.png"  style="height:33px;width:145px;margin-left:20px;margin-top:10px">
        </router-link>
        <span style="font-size:20px;color:#E0FFFF">&#160; 数据标注平台</span>
      </div>
    </div>
    <div style="background-color: #1da1f2; height:10px;  width:100%; " ></div>
    <el-header></el-header>
    <!--操作窗口-->
    <el-main>
      <el-row>
        <el-col :span="6" style="margin-left:8%">当前为第{{this.image_id}}帧</el-col>
        <el-col :span="4" ><el-button type="primary" @click="saveLabels" icon="el-icon-download" size="medium">标注结果</el-button></el-col>
      </el-row>
      <el-row style="margin-top: 10px">
        <el-col :span="2">
          <el-button @click="formerImage" icon="el-icon-arrow-left"></el-button>
        </el-col>
        <el-col :span="20" style="margin-right: 10px">
          <div class="center" style="margin-left:40px">
            <div class="myedit" ref="myedit" @mousedown.prevent="onMousedown" @mousemove="onMousemove" @mouseup="onMouseup">
              <img :src="imageSrc" id="labelPic" @load="handleLoad"/>
              <div  v-for="(item, index) in mydata">
                <el-tooltip class="item" effect="dark" :content="'event '+item.actionID+' : '+item.label" placement="top">
        <span
          class="myedit-span"
          :key="index"
          :style="getSpanStyle(item)"
          @contextmenu.prevent="onContextmenu(item,$event)"
          @mousedown.prevent="startAdjust($event)"
          @mousemove.prevent="adjustBlock($event)"
        >
        </span>
                </el-tooltip>
              </div>
            </div>
          </div>
        </el-col>
        <el-col :span="1">
          <el-button @click="nextImage" icon="el-icon-arrow-right"></el-button>
        </el-col>
      </el-row>
      <!--操作窗口-->
      <!--菜单-->
      <!--<div class="myMenu" v-show="currentItem" :style="mymenu.style">-->
      <div  class="roundedRectangle" v-show="currentItem" :style="mymenu.style" >
        <el-row>
          <el-col :span="12">
            事件{{actionID}}：
          </el-col>
          <el-col :span="12">
            <el-select
              v-model="value"
              filterable
              remote
              reserve-keyword
              placeholder="请输入标签"
              :remote-method="matchLabel"
              :loading="loading" size="small">
              <el-option
                v-for="item in possibleLabel"
                :key="item.value"
                :label="item.label"
                :value="item.value">
              </el-option>
            </el-select>
          </el-col>
        </el-row>
        <!--<el-button @click="finishAdjust">结束调整</el-button>-->
        <el-row>
          <el-col :span="12">起始帧：</el-col>
          <el-col :span="12">
            <el-select filterable v-model="beginFrame" size="small">
              <el-option
                v-for="item in frame_options"
                :key="item.value"
                :label="item.label"
                :value="item.value">
              </el-option>
            </el-select>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="12">结束帧：</el-col>
          <el-col :span="12">
            <el-select filterable v-model="endFrame" size="small">
              <el-option
                v-for="item in frame_options"
                :key="item.value"
                :label="item.label"
                :value="item.value">
              </el-option>
            </el-select>
          </el-col>
        </el-row>
          <!--标识起始帧结束帧-->
          <el-button @click="chooseBlock">调整事件</el-button>
          <el-button @click="onRemoveItem">删除事件</el-button>
          <el-button type="primary" @click="addLabel">确认事件</el-button>
      </div>
      <!--</div>-->
      <!--菜单-->
      <br />  <br />    <br />  <br />    <br />  <br />
      <br />  <br />    <br />  <br />    <br />  <br />
      <br />  <br />    <br />  <br />    <br />  <br />
      <br />  <br />    <br />  <br />
    </el-main>
  </el-container>
</template>

<script>
  import axios from 'axios'
  export default {
    name: "labelPage",
    data: function () {
      return {
        loading:false,
        images:[], //存储了数据集中所有图片的信息， 每张图片的信息包括image_id与image_src
        imageSrc:"",  //当前显示图片的src
        image_id:0,  //当前图片id
        mysrc: "",
        dataset_label:[], //存储了所有事件的标注信息,元素为[[{label,x,y,x2,y2,frameID,beginFrame,endFrame},{},{}],...]
        mydata: [],  //存储当前图片中所有框的信息，每个框的信息由index与item构成，其中index为索引，item为拉框对象
        currentItem:null,  //表示目前选中的拉框
        isAdjust:false,  //是否在调整画框
        isDrag:true,  //是否是拖拽操作
        threshold:15,  //鼠标在框右下角的判断范围
        mymenu: { style: { left: 0, top: 0 } },  //标注框左上角位置
        value:"",  //当前框的标签内容
        options: [], //提供的可选标注
        possibleLabel:[],  //模糊匹配的标注
        actionID:0, //当前选择的事件id
        max_id:0,  //事件的最大id
        count:[], //记录现存事件及事件id
        frame_options:[],  //帧选项
        beginFrame:0, //起始帧
        endFrame:0  //结束帧
      }
    },
    mounted:function()
    {
      let _this=this
      let  obj={user_id:this.$route.query.user_id,video_id:this.$route.query.video_id,fps:this.$route.query.fps}
      var jsontext = encodeURIComponent(JSON.stringify(obj));
      this.$reqs.post('/keyActionInitial/?jsontext='+jsontext).then(res=>{
        this.$message.success('已成功上传视频，开始标注吧~')
        _this.image_id=0
        _this.images=res.data.images
        _this.imageSrc=_this.images[_this.image_id]
        _this.dataset_label=res.data.labels
        // 初始化可选标注
        _this.options=res.data.options
        //初始化帧标注
        _this.frame_options=res.data.frame_options
        //记录帧映射及总帧数
        _this.frame_map=res.data.frame_map
        _this.frameNum=res.data.frameNum
      });
    },
    methods: {
      /***模糊匹配标签****/
      matchLabel(query){
        var _this = this;
        if (query !== '') {
          _this.loading = true;
          setTimeout(() => {
            _this.loading = false;
            _this.possibleLabel = _this.options.filter(item => {
              return item.label.toLowerCase()
                .indexOf(query.toLowerCase()) > -1;
            });
          }, 200);
        }
        else if(_this.value.length!==0) {
          _this.possibleLabel = [{
            value:"other",
            label:"other"
          }];
        }
      },
      /****在加载完新图片后进行机器预识别****/
      //将base64编码转换为文件
      dataURLtoFile(dataurl, filename)
      {
        var arr = dataurl.split(','), mime = arr[0].match(/:(.*?);/)[1],
          bstr = atob(arr[1]), n = bstr.length, u8arr = new Uint8Array(n);
        while(n--)
        {u8arr[n] = bstr.charCodeAt(n);}
        return new File([u8arr], filename, {type:mime});
      },
      //请求机器预识别
      machineAssist()
      {
        // let _this=this;
        // var fd = new FormData();
        // fd.append('img', this.dataURLtoFile(this.imageSrc,"img"));
        // this.$reqs.post('http://s1.linkeserver.ml:5001/object-detection',fd).
        // then(function (response){
        //   _this.mydata = response.data;
        //   let temp = _this.clientWidth/_this.picWidth;
        //   for(let i = 0;i<_this.mydata.length;i++){
        //     _this.mydata[i].x *= temp;
        //     _this.mydata[i].y *= temp;
        //     _this.mydata[i].x2 *= temp;
        //     _this.mydata[i].y2 *= temp;
        //   }
        // }).catch(function(error){
        //   console.log(error);
        // });
      },
      /****获取下一张图片并保存上一张图片的标注结果****/
      nextImage(){
        //显示下一张图片
        if(this.image_id!==this.images.length-1)
        {
          this.image_id+=1
          this.imageSrc=this.images[this.image_id]
          this.mydata=this.dataset_label[this.image_id]
        }
        else
          this.$message('后面没有图了哦~');
      },
      /****获取上一张图片并保持下一张图片的标注结果*****/
      formerImage(){
        //显示下一张图片
        if(this.image_id!==0)
        {
          this.image_id-=1
          this.imageSrc=this.images[this.image_id]
          this.mydata=this.dataset_label[this.image_id]
        }
        else
          this.$message('已经是第一张图片啦~');
      },
      /****保存标注结果****/
      saveLabels(){
        //要判断有没有标签可保存
        let _this=this
        // 上传标注信息
        var obj ={labels:this.dataset_label,proportion:this.proportion ,frame_map:this.frame_map,frameNum:this.frameNum,uID:1,videoID:1,actionNum:this.count.length,count:this.count,user_id:this.$route.query.user_id,video_id:this.$route.query.video_id}
        var jsontext = encodeURIComponent(JSON.stringify(obj));
        window.open('http://localhost:5415/savekeyActions/?jsontext='+jsontext)
      },
      /****在加载完图片后获取图片宽高****/
      handleLoad(){
        this.picWidth = document.getElementById("labelPic").naturalWidth;
        this.clientWidth = document.getElementById("labelPic").clientWidth;
        this.clientHeight=document.getElementById("labelPic").clientHeight;
        this.proportion = this.picWidth/this.clientWidth;
      },
      /****新建拉框相关函数****/
      //获取鼠标在图片上的相对位置
      getXY(e) {
        let rect = this.$refs.myedit.getBoundingClientRect();
        return {
          x: e.clientX - rect.left,
          y: e.clientY - rect.top
        }
      },
      //当鼠标左键被按下，若此时在拉框，则记录初始位置，在mydata中加入新的拉框
      onMousedown(e) {
        //若是右键显示菜单或在调整拉框
        if(this.isAdjust||e.button === 2 )
        {
          console.log("在调整拉框或点击了鼠标右键")
          return;
        }
        let { x, y } = this.getXY(e)  //获得鼠标坐标
        this.newItem = {actionID:this.max_id,x, y, x2:x, y2:y,label:"" ,beginFrame:0,endFrame:0,frameID:this.image_id} //增加事件序号
        this.startPos = { x, y }   //记录鼠标初始位置
        this.dataset_label[this.image_id].push(this.newItem)
        this.mydata=this.dataset_label[this.image_id]
        this.newFlag=true  //标识刚刚有拉框被新建
      },
      //当鼠标移动时，若此时正在拉框，则更新拉框右下角的位置，否则不做操作
      onMousemove(e) {
        if (!this.newItem) return;
        this.newItem.x=Math.min(this.startPos.x,this.getXY(e).x);
        this.newItem.y=Math.min(this.startPos.y,this.getXY(e).y);
        this.newItem.x2=Math.max(this.startPos.x,this.getXY(e).x);
        this.newItem.y2=Math.max(this.startPos.y,this.getXY(e).y);
        //border constraint
        if(this.newItem.x<0)
          this.newItem.x=0;
        if(this.newItem.y<0)
          this.newItem.y=0;
      },
      //当鼠标左键释放，清空现有拉框与初始位置
      onMouseup(e) {
        this.dataset_label[this.image_id] = this.dataset_label[this.image_id].filter(_ => (_.x2-_.x) > 5 && (_.y2-_.y) > 5)  //过滤掉过小的标注框
        if(!this.isAdjust)
        {
          this.isAdjust=true;     //调整拉框标记置为true
          this.adjustItem=this.newItem;
          this.newItem=this.startPos = null;
        }
        else{
          this.startPos = null;//因为此时adjustBlock已经重置了startPos所以要再次置null
        }
      },
      //在拉框上点击右键时出现标注框
      onContextmenu(item,e) {
        this.currentItem=item;  //当前框置为此拉框
        if(item.label!=="") //若标签不为空，则说明为已存在事件，则显示此事件内容
        {
          this.value=item.label;  //将当前标签内容置为此拉框的标签内容
          this.beginFrame=item.beginFrame;
          this.endFrame=item.endFrame;
          this.actionID=item.actionID;
        }
        else{ //若标签为空，说明这是一个新建事件，则采用默认设置
          this.value=""
          this.beginFrame=this.image_id;
          this.endFrame=this.beginFrame;
          this.actionID=this.max_id
        }
        this.mymenu = {  //拉框左上角位置为当前鼠标点击位置
          style: {
            top: e.clientY + 'px',
            left: e.clientX + 'px'
          }
        }
      },
      //删除拉框
      onRemoveItem() {
        //如果删除一个刚新建的事件,则就在此帧内删除
        if(this.newFlag){
          this.dataset_label[this.image_id].splice(this.dataset_label[this.image_id].indexOf(this.currentItem),1);
          this.newFlag=false
        }
        //如果删除一个已经存在的事件,则逐帧删除事件
        else{
          for(let i=this.beginFrame;i<=this.endFrame;i++)
          {
            for(let j=0;j<this.dataset_label[i].length;)
            {
              if (this.dataset_label[i][j].actionID===this.actionID) {
                this.dataset_label[i].splice(j, 1); //indexOf找到该item的位置，1表示删除该元素
              }
              else{
                j++;
              }
            }
          }
          this.count.splice(this.count.indexOf(this.actionID),1) //删除此事件的ID
        }
        //刷新mydata
        this.mydata=this.dataset_label[this.image_id]
        this.currentItem=null;  //清空当前拉框与此拉框初始状态
        this.isAdjust=false;
      },
      /****修改拉框相关函数****/
      //点击确认键后，当前拉框的标注内容改为labelContent的内容，修改mydata中此拉框的标注信息
      addLabel() {
        //若填写有误
        if(this.value.length===0) this.$message.warning('没有填写标签信息');
        else if(this.endFrame<this.beginFrame) this.$message.warning('时间段不合法');
        //若填写无误
        else
        {
          if(this.newFlag)
          {
            //若为新建事件
            for(let i=this.beginFrame;i<=this.endFrame;i++){
                let temp={actionID:this.max_id,x:this.currentItem.x, y:this.currentItem.y, x2:this.currentItem.x2, y2:this.currentItem.y2,label:this.value ,beginFrame:this.beginFrame,endFrame:this.endFrame,frameID:i}
                this.dataset_label[i].push(temp)
              }
            this.count.push(this.max_id)//事件ID新增一个
            this.max_id++;
            this.dataset_label[this.image_id].splice(this.dataset_label[this.image_id].indexOf(this.currentItem),1);
            //刷新mydata中的数据给前端显示
            this.mydata=this.dataset_label[this.image_id]
            this.newFlag=false
          }
          else
            {
            //若不是新建事件，只是对某一帧的某一个拉框进行修改
            //改变了标签，起始帧时要做处理
              let begin=this.currentItem.beginFrame
              let end=this.currentItem.endFrame
              let x=this.currentItem.x
              let y=this.currentItem.y
              let x2=this.currentItem.x2
              let y2=this.currentItem.y2
              if(this.beginFrame<begin && this.endFrame>=begin && this.endFrame<=end) //起帧前移，尾帧仍在原范围
              {
                console.log("起帧前移，尾帧仍在原范围")
                //原起帧之前的加入
                for(let i=this.beginFrame;i<begin;i++)
                {
                  let temp={actionID:this.actionID,x:x, y:y, x2:x2, y2:y2,label:this.value ,beginFrame:this.beginFrame,endFrame:this.endFrame,frameID:i}
                  this.dataset_label[i].push(temp)
                }
                //重叠部分更改起始帧与标签
                for(let i=begin;i<=this.endFrame;i++)
                {
                  for(let j=0;j<this.dataset_label[i].length;j++)
                  {
                    if (this.dataset_label[i][j].actionID===this.actionID)
                    {
                      this.dataset_label[i][j].beginFrame=this.beginFrame;
                      this.dataset_label[i][j].endFrame=this.endFrame;
                      this.dataset_label[i][j].label=this.value;
                    }
                  }
                }
                //现尾帧后删除
                for(let i=this.endFrame+1;i<=end;i++)
                {
                  for(let j=0;j<this.dataset_label[i].length;)
                  {
                    if (this.dataset_label[i][j].actionID===this.actionID) {
                      this.dataset_label[i].splice(j, 1);
                    }
                    else{
                      j++;
                    }
                  }
                }
              }
              else if(this.endFrame>end && this.beginFrame>=begin && this.beginFrame<=end) //起帧仍在原范围，尾帧后移
              {
                console.log("起帧仍在原范围，尾帧后移")
                //原起始帧之前删除
                for(let i=begin;i<this.beginFrame;i++)
                {
                  for(let j=0;j<this.dataset_label[i].length;)
                  {
                    if (this.dataset_label[i][j].actionID===this.actionID) {
                      this.dataset_label[i].splice(j, 1);
                    }
                    else{
                      j++;
                    }
                  }
                }
                //重叠部分改变起始帧及标签
                for(let i=this.beginFrame;i<=end;i++)
                {
                  for(let j=0;j<this.dataset_label[i].length;j++)
                  {
                    if (this.dataset_label[i][j].actionID===this.actionID)
                    {
                      this.dataset_label[i][j].beginFrame=this.beginFrame;
                      this.dataset_label[i][j].endFrame=this.endFrame;
                      this.dataset_label[i][j].label=this.value;
                    }
                  }
                }
                //原尾帧之后插入
                for(let i=end+1;i<=this.endFrame;i++)
                {
                  let temp={actionID:this.actionID,x:x, y:y, x2:x2, y2:y2,label:this.value ,beginFrame:this.beginFrame,endFrame:this.endFrame,frameID:i}
                  this.dataset_label[i].push(temp)
                }
              }
              else if((this.endFrame!==end||this.beginFrame!==begin)&& this.beginFrame>=begin && this.endFrame<=end) //起帧和尾帧都在原范围内，但至少有一项改变了
              {
                //现起帧前删除
                for(let i=begin;i<this.beginFrame;i++)
                {
                  for(let j=0;j<this.dataset_label[i].length;)
                  {
                    if (this.dataset_label[i][j].actionID===this.actionID) {
                      this.dataset_label[i].splice(j, 1);
                    }
                    else{
                      j++;
                    }
                  }
                }
                //重叠部分更改
                for(let i=this.beginFrame;i<=this.endFrame;i++)
                {
                  for(let j=0;j<this.dataset_label[i].length;j++)
                  {
                    if (this.dataset_label[i][j].actionID===this.actionID)
                    {
                      this.dataset_label[i][j].beginFrame=this.beginFrame;
                      this.dataset_label[i][j].endFrame=this.endFrame;
                      this.dataset_label[i][j].label=this.value;
                    }
                  }
                }
                //现尾帧后删除
                for(let i=this.endFrame+1;i<=end;i++)
                {
                  for(let j=0;j<this.dataset_label[i].length;)
                  {
                    if (this.dataset_label[i][j].actionID===this.actionID) {
                      this.dataset_label[i].splice(j, 1);
                    }
                    else{
                      j++;
                    }
                  }
                }
              }
              else if(this.beginFrame<begin && this.endFrame>end) //起帧前移，尾帧后移
              {
                //原起帧前插入
                for(let i=this.beginFrame;i<begin;i++)
                {
                  let temp={actionID:this.actionID,x:x, y:y, x2:x2, y2:y2,label:this.value ,beginFrame:this.beginFrame,endFrame:this.endFrame,frameID:i}
                  this.dataset_label[i].push(temp)
                }
                //重叠部分修改
                for(let i=begin;i<=end;i++)
                {
                  for(let j=0;j<this.dataset_label[i].length;j++)
                  {
                    if (this.dataset_label[i][j].actionID===this.actionID)
                    {
                      this.dataset_label[i][j].beginFrame=this.beginFrame;
                      this.dataset_label[i][j].endFrame=this.endFrame;
                      this.dataset_label[i][j].label=this.value;
                    }
                  }
                }
                //原尾帧后插入
                for(let i=end+1;i<=this.endFrame;i++)
                {
                  let temp={actionID:this.actionID,x:x, y:y, x2:x2, y2:y2,label:this.value ,beginFrame:this.beginFrame,endFrame:this.endFrame,frameID:i}
                  this.dataset_label[i].push(temp)
                }
              }
              else if(this.beginFrame>end||this.endFrame<begin) //起帧，尾帧都后移，且起帧不在原范围内
              {
                //原部分删除
                for(let i=begin;i<=end;i++)
                {
                  for(let j=0;j<this.dataset_label[i].length;)
                  {
                    if (this.dataset_label[i][j].actionID===this.actionID) {
                      this.dataset_label[i].splice(j, 1);
                    }
                    else{
                      j++;
                    }
                  }
                }
                //新部分增加
                for(let i=this.beginFrame;i<=this.endFrame;i++)
                {
                  let temp={actionID:this.actionID,x:x, y:y, x2:x2, y2:y2,label:this.value ,beginFrame:this.beginFrame,endFrame:this.endFrame,frameID:i}
                  this.dataset_label[i].push(temp)
                }
              }
              else if(this.value!==this.currentItem.label) //起始帧没变，但标签改变
              {
                for(let i=this.currentItem.beginFrame;i<=this.currentItem.endFrame;i++)
                {
                  for(let j=0;j<this.dataset_label[i].length;j++)
                  {
                    if (this.dataset_label[i][j].actionID===this.actionID)
                    {
                      this.dataset_label[i][j].label=this.value;
                    }
                  }
                }
              }
              this.mydata=this.dataset_label[this.image_id] //刷新视图
          }
          this.currentItem=null
        }
        if(this.isAdjust) this.isAdjust=false
      },
      //点击修改按钮后，标记调整开始
      chooseBlock()
      {
        this.isAdjust=true;     //调整拉框标记置为true
        this.adjustItem=this.currentItem;
        this.currentItem=null;
      },
      //在拉框内按下鼠标左键时即选中此拉框准备调整（拖拽或放缩）
      startAdjust(e){
        if(!this.isAdjust) return;  //若不是调整拉框操作，则返回
        let { x, y } = this.getXY(e);  //获取鼠标当前位置
        this.startPos={x,y};    //记录鼠标初始位置
        this.startSize={w:this.adjustItem.x2-this.adjustItem.x,h:this.adjustItem.y2-this.adjustItem.y,
          x1:this.adjustItem.x,y1:this.adjustItem.y,x2:this.adjustItem.x2,y2:this.adjustItem.y2}; //记录框的初始长宽
        /*判断是否为放缩操作*/
        this.isDrag=!(
          (x-this.startSize.x1<=this.threshold&&y-this.startSize.y1<=this.threshold)||
          (this.startSize.x2-x<=this.threshold&&y-this.startSize.y1<=this.threshold)||
          (x-this.startSize.x1<=this.threshold&&this.startSize.y2-y<=this.threshold)||
          (this.startSize.x2-x<=this.threshold&&this.startSize.y2-y<=this.threshold)
        );
        if(this.isDrag)  //若为拖拽操作
        {
          this.startPos={x:x-this.adjustItem.x,y:y-this.adjustItem.y}   //记录鼠标在拉框内的位置（即，鼠标相对拉框的坐标）
        }
      },
      //在拉框内移动鼠标时，表示对此拉框正在进行拖拽或放缩操作，针对不同操作函数做出不同处理
      adjustBlock(e){
        if(!this.isAdjust||!this.startPos) return;  //若没有开始标注，则返回
        let{x,y}=this.getXY(e);   //记录鼠标当前位置
        let t=this.threshold;
        if(this.isDrag)  //若为拖拽操作
        {
          this.adjustItem.x=x-this.startPos.x;   //鼠标移动时，鼠标在拉框内的位置不变（即，拉框与鼠标相对静止）
          this.adjustItem.y=y-this.startPos.y;
          this.adjustItem.x2=this.adjustItem.x+this.startSize.w;
          this.adjustItem.y2=this.adjustItem.y+this.startSize.h;
        }
        else if(!this.newFlag) {   //若为放缩操作
          if(x-this.adjustItem.x<=t&&y-this.adjustItem.y<=t){this.adjustItem.x=x-t/2; this.adjustItem.y=y-t/2;}
          if(this.adjustItem.x2-x<=t&&y-this.adjustItem.y<=t){this.adjustItem.x2=x+t/2; this.adjustItem.y=y-t/2;}
          if(x-this.adjustItem.x<=t&&this.adjustItem.y2-y<=t){this.adjustItem.x=x-t/2; this.adjustItem.y2=y+t/2;}
          if(this.adjustItem.x2-x<=t&&this.adjustItem.y2-y<=t){this.adjustItem.x2=x+t/2; this.adjustItem.y2=y+t/2;}
        }
        /*border constraint*/
        if(this.adjustItem.x<=0)
          this.adjustItem.x=0;
        if(this.adjustItem.y<=0)
          this.adjustItem.y=0
        if(this.adjustItem.x2>=this.clientWidth)
          this.adjustItem.x2=this.clientWidth
        if(this.adjustItem.y2>=this.clientHeight)
          this.adjustItem.y2=this.clientHeight
      },
      /****拉框显示相关函数****/
      //将拉框的位置信息转变为样式显示在界面上
      getSpanStyle(item) {
        return {
          width: `${Math.abs(item.x2-item.x)}px`,
          height: `${Math.abs(item.y2-item.y)}px`,
          top: `${item.y}px`,
          left: `${item.x}px`
        };
      }
    }
  }
</script>

<style lang="less" scoped>
  .roundedRectangle
  {
    //height: 70px;
    width: 240px;
    background-color: #EEE5DE;//背景色
    //border-width: 10px;	//边缘的宽度，如果要分别设置可以这样：
    border-width: 15px 5px 15px 5px;//依次为上、右、下、左
    border-style: solid;
    border-radius: 0px 10px 10px 10px;	//圆角的大小
    border-color: #EEE5DE;	//边框颜色，依次为上、右、下、左
    position:fixed;
    padding: 8px
  }
  // 设置绘图样式2
  .mycanvas-container
  {
    background:url(../assets/background-t.jpg)  no-repeat center center;
    background-size:cover;
    background-attachment:fixed;
    background-color:#CCCCCC;
    display: flex;
    justify-content: center;
    align-items: center;
    .center
    {
      width: 450px;
      margin-left:20%;
      //border: 1px solid #000;
      .myedit
      {
        width: 100%;
        //height: 500px;
        //border: 1px solid #020;
        position: relative;
        .myedit-span
        {
          position: absolute;
          border: 3px dashed #fff;
          background-size: contain;
        }
        img
        {
          width: 100%;
        }
      }
    }
  }

</style>

