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
                <el-tooltip class="item" effect="dark" :content="item.label" placement="top">
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
      <el-form  class="roundedRectangle" v-show="currentItem" :style="mymenu.style" >
        <el-form-item>
          <el-select
            v-model="value"
            multiple
            filterable
            remote
            reserve-keyword
            placeholder="请输入标签"
            :remote-method="matchLabel"
            :loading="loading"
            >
            <el-option
              v-for="item in possibleLabel"
              :key="item.value"
              :label="item.label"
              :value="item.value">
            </el-option>
          </el-select>
        </el-form-item>
          <!--<el-button @click="finishAdjust">结束调整</el-button>-->
        <el-form-item>
          <el-button @click="chooseBlock">调整拉框</el-button>
          <el-button @click="onRemoveItem">删除拉框</el-button>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="addLabel">完成标注</el-button>
        </el-form-item>
      </el-form>
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
  export default {
    name: "labelPage",
    data: function () {
      return {
        loading:false,
        images:[], //存储了数据集中所有图片的信息， 每张图片的信息包括image_id与image_src
        imageSrc:"",  //当前显示图片的src
        image_id:0,  //当前图片id
        mysrc: "",
        dataset_label:[], //存储了一个数据集中所有图片的标注信息
        mydata: [],  //存储了一个图片中所有框的信息，每个框的信息由index与item构成，其中index为索引，item为拉框对象
        currentItem:null,  //表示目前选中的拉框
        isAdjust:false,  //是否在调整画框
        isDrag:true,  //是否是拖拽操作
        threshold:15,  //鼠标在框右下角的判断范围
        mymenu: { style: { left: 0, top: 0 } },  //标注框左上角位置
        value:[],  //当前框的标签内容
        options: [], //提供的可选标注
        possibleLabel:[],  //模糊匹配的标注
      }
    },
    mounted:function() {
      var _this=this;
      let  obj={user_id:this.$route.query.user_id,video_id:this.$route.query.video_id,fps:this.$route.query.fps}
      var jsontext = encodeURIComponent(JSON.stringify(obj));
      this.$reqs.get("/videoToImage/?jsontext="+jsontext).then(res => {
        this.$message.success('已成功上传视频，开始标注吧~')
        //初始化图片及图片标签
        _this.images=res.data.images
        _this.imageSrc=_this.images[_this.image_id]
        _this.dataset_label=res.data.labels
        _this.mydata=_this.dataset_label[_this.image_id]
        _this.options=res.data.options
        _this.frame_map=res.data.frame_map
        //初始化可选标注
      })
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
        var obj ={labels:this.dataset_label,proportion:this.proportion,user_id:this.$route.query.user_id,video_id:this.$route.query.video_id,frame_map:this.frame_map}
        var jsontext = encodeURIComponent(JSON.stringify(obj));
        window.open('http://localhost:5415/saveLabels/?jsontext='+jsontext)
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
        if(this.isAdjust||e.button === 2 )
        {
          return;
        }  //若是右键显示菜单，则不做处理
        let { x, y } = this.getXY(e)  //获得鼠标坐标
        this.newItem = { x, y, x2:x, y2:y,label:"" }
        this.startPos = { x, y }   //记录鼠标初始位置
        this.dataset_label[this.image_id].push(this.newItem)
        this.mydata=this.dataset_label[this.image_id]
        this.newFlag=true
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
          this.startPos = null;
        }
      },
      //在拉框上点击右键时出现标注框
      onContextmenu(item,e) {
        this.currentItem=item;  //当前框置为此拉框
        if(item.label!=="")
        {
          this.value=item.label.split(',');  //将当前标签内容置为此拉框的标签内容
        }
        else{ //若标签为空，说明这是一个新建事件，则采用默认设置
          this.value=[]
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
        if(this.newFlag){this.newFlag=false}
        this.dataset_label[this.image_id].splice(this.dataset_label[this.image_id].indexOf(this.currentItem),1);
        //刷新mydata
        this.mydata=this.dataset_label[this.image_id]
        this.currentItem=null;  //清空当前拉框与此拉框初始状态
        this.isAdjust=false;
      },
      /****修改拉框相关函数****/
      //点击确认键后，当前拉框的标注内容改为labelContent的内容，修改mydata中此拉框的标注信息
      addLabel() {
        if(this.value.length===0)
        {
          this.$message({
            message: '您没有填写标签',
            type: 'warning'
          });
        }
        else{
          this.currentItem.label=this.value.join(",");
          //刷新mydata中的数据给前端显示
          this.mydata=this.dataset_label[this.image_id]
          this.currentItem=null;
          if(this.isAdjust) this.isAdjust=false
          if(this.newFlag){this.newFlag=false}
        }
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
