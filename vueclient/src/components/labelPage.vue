<template>
  <el-container class="mycanvas-container">
      <div style="background-color: #1da1f2; height:50px;  width:100%; " >
        <div style="display: table-cell;  line-height:60px;">
          <router-link :to="{ name: 'personalPage', query:{uid:this.uid}}">
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
        <el-col :span="12" style="font-size:20px">当前图片id：{{image_id}}</el-col>
        <el-col :span="40" style="margin-left: 65px"><el-button @click="saveLabels" type="primary">上传数据集标注结果</el-button></el-col>
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
            value="labelContent">
            <el-option
              v-for="item in possibleLabel"
              :key="item.value"
              :label="item.label"
              :value="item.value">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
       <el-button @click="chooseBlock">调整拉框</el-button>
        <el-button @click="finishAdjust">结束调整</el-button>
        </el-form-item>
        <el-form-item>
          <el-button @click="onRemoveItem">删除拉框</el-button>
          <el-button type="primary" @click="addLabel">提交标注</el-button>
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
          image_id:1,  //当前图片id
          datasetid:this.$route.query.datasetid,
          uid:this.$route.query.uid,
          mysrc: "",
          dataset_label:[], //存储了一个数据集中所有图片的标注信息
          mydata: [],  //存储了一个图片中所有框的信息，每个框的信息由index与item构成，其中index为索引，item为拉框对象
          currentItem:null,  //表示目前选中的拉框
          originItem:null,  //更改前的拉框
          isAdjust:false,  //是否在调整画框
          isDrag:true,  //是否是拖拽操作
          threshold:15,  //鼠标在框右下角的判断范围
          mymenu: { style: { left: 0, top: 0 } },  //标注框左上角位置
          value:[],  //当前框的标签内容
          options: [], //提供的可选标注
          possibleLabel:[]  //模糊匹配的标注
        }
      },
      mounted:function()
      {
        /****获取所有图片****/
        var _this=this
        this.$reqs.get('/personal/getImageandLabel',{params:{datasetid:_this.datasetid,uid:_this.uid}}).then(res=>{
          _this.images=res.data.image
          _this.imageSrc=_this.images[_this.image_id-1].image_src
          _this.dataset_label=res.data.label
          _this.mydata=_this.dataset_label[_this.image_id-1].label
          if(_this.mydata.length===0) //若图片没有标签，则调用机器预识别
          {
            _this.machineAssist()
          }
        }).catch(error=>{
          console.log(error)
        })
        /****获取标签内容****/
        this.$reqs.get('/personal/getlabelContent').then(res=>{
          _this.options=res.data.options
        }).catch(err=>{
          console.log(err)
        })
      },
      methods: {
        //监听input框输入事件
        matchLabel(query){
          console.log(this.labelContent)
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
          let _this=this;
          var fd = new FormData();
          fd.append('img', this.dataURLtoFile(this.imageSrc,"img"));
          this.$reqs.post('http://s1.linkeserver.ml:5001/object-detection',fd).
          then(function (response){
            _this.mydata = response.data;
            let temp = _this.clientWidth/_this.picWidth;
            for(let i = 0;i<_this.mydata.length;i++){
              _this.mydata[i].x *= temp;
              _this.mydata[i].y *= temp;
              _this.mydata[i].x2 *= temp;
              _this.mydata[i].y2 *= temp;
            }
          }).catch(function(error){
            console.log(error);
          });
        },
        /****获取下一张图片并保存上一张图片的标注结果****/
        nextImage(){
          //保存当前图片的标注结果
          this.dataset_label[this.image_id-1].label=this.mydata
          //显示下一张图片
          if(this.image_id!==this.images.length)
          {
            this.image_id+=1
            this.imageSrc=this.images[this.image_id-1].image_src
            this.mydata=this.dataset_label[this.image_id-1].label
            if(this.mydata.length===0) //若图片没有标签，则调用机器预识别
            {
              this.machineAssist()
            }
          }
          else
            this.$message('后面没有图了哦~');
        },
        /****获取上一张图片并保持下一张图片的标注结果*****/
        formerImage(){
          //保存当前图片的标注结果
          this.dataset_label[this.image_id-1].label=this.mydata
          //显示下一张图片
          if(this.image_id!==1)
          {
            this.image_id-=1
            this.imageSrc=this.images[this.image_id-1].image_src
            this.mydata=this.dataset_label[this.image_id-1].label
            if(this.mydata.length===0) //若图片没有标签，则调用机器预识别
            {
              this.machineAssist()
            }
          }
          else
            this.$message('已经是第一张图片啦~');
        },
        /****保存标注结果****/
        saveLabels(){
          let _this=this
          //保存当前图片的标注结果
          this.dataset_label[this.image_id-1].label=this.mydata
          // 上传标注信息
          this.$reqs.post('/personal/saveLabels',{
            uid:_this.uid,
            datasetid:_this.datasetid,
            dataset_label:_this.dataset_label
          }).then(res=>{
            if(res.data.data===1)
            {
              this.$message({
                message: '上传标注信息成功！',
                type: 'success'
              });
            }
          }).catch(error=>{
            console.log(error);
            this.$message.error('上传标注信息失败');
          })
        },
        /****在加载完图片后获取图片宽高****/
        handleLoad(){
          this.picWidth = document.getElementById("labelPic").naturalWidth;
          this.clientWidth = document.getElementById("labelPic").clientWidth;
          this.clientHeight=document.getElementById("labelPic").clientHeight;
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
          //this.currentItem = null
          let { x, y } = this.getXY(e)  //获得鼠标坐标
          this.newItem = { x, y, x2:x, y2:y,label:"" }
          this.startPos = { x, y }   //记录鼠标初始位置
          this.mydata.push(this.newItem)
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
          this.mydata = this.mydata.filter(_ => (_.x2-_.x) > 5 && (_.y2-_.y) > 5)  //过滤掉过小的标注框
          if(!this.isAdjust)
          {
            this.isAdjust=true;     //调整拉框标记置为true
            this.index=this.mydata.indexOf(this.newItem);
          }
          else{
            this.newItem = this.startPos = null;
          }
        },
        //在拉框上点击右键时出现标注框
        onContextmenu(item,e) {
          this.currentItem=item;  //当前框置为此拉框
          this.originItem=item;   //记录此拉框的初始状态
          if(item.label!=="")
          {
            this.value=item.label.split(',');  //将当前标签内容置为此拉框的标签内容
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
          this.mydata.splice(this.mydata.indexOf(this.originItem), 1); //indexOf找到该item的位置，1表示删除该元素
          this.currentItem=this.originItem=null;  //清空当前拉框与此拉框初始状态
          this.isAdjust=false;
          this.value=[];
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
            this.value=[];
            this.mydata.splice(this.mydata.indexOf(this.originItem),1,this.currentItem);
            this.currentItem=this.originItem=null;
            if(this.isAdjust) this.isAdjust=false
          }
        },
        //点击修改按钮后，标记调整开始
        chooseBlock()
        {
          this.isAdjust=true;     //调整拉框标记置为true
          this.index=this.mydata.indexOf(this.originItem);
          this.currentItem=this.originItem=null;
        },
        //在拉框内按下鼠标左键时即选中此拉框准备调整（拖拽或放缩）
        startAdjust(e){
          if(!this.isAdjust) return;  //若不是调整拉框操作，则返回
          let { x, y } = this.getXY(e);  //获取鼠标当前位置
          this.startPos={x,y};    //记录鼠标初始位置
          let index=this.index;
          console.log(index)
          this.startSize={w:this.mydata[index].x2-this.mydata[index].x,h:this.mydata[index].y2-this.mydata[index].y,
            x1:this.mydata[index].x,y1:this.mydata[index].y,x2:this.mydata[index].x2,y2:this.mydata[index].y2}; //记录框的初始长宽
          /*判断是否为放缩操作*/
          //this.isDrag = !(Math.abs(x - this.mydata[index].x2) <= this.threshold && Math.abs(y - this.mydata[index].y2) <= this.threshold);  //若鼠标位置距离右小角在threshold内，则为放缩操作，否则为拖拽操作
          this.isDrag=!(
            (x-this.startSize.x1<=this.threshold&&y-this.startSize.y1<=this.threshold)||
            (this.startSize.x2-x<=this.threshold&&y-this.startSize.y1<=this.threshold)||
            (x-this.startSize.x1<=this.threshold&&this.startSize.y2-y<=this.threshold)||
            (this.startSize.x2-x<=this.threshold&&this.startSize.y2-y<=this.threshold)
          );
          if(this.isDrag)  //若为拖拽操作
          {
            this.startPos={x:x-this.mydata[index].x,y:y-this.mydata[index].y}   //记录鼠标在拉框内的位置（即，鼠标相对拉框的坐标）
          }
        },
        //在拉框内移动鼠标时，表示对此拉框正在进行拖拽或放缩操作，针对不同操作函数做出不同处理
        adjustBlock(e){
          if(!this.isAdjust||!this.startPos) return;  //若没有开始标注，则返回
          let index=this.index;
          //if(this.mydata[index].x<=0||this.mydata[index].y<=0||this.mydata[index].x2>=this.clientWidth||this.mydata[index].y2>=this.clientHeight) return;
          let{x,y}=this.getXY(e);   //记录鼠标当前位置
          let t=this.threshold;
          if(this.isDrag)  //若为拖拽操作
          {
            this.mydata[index].x=x-this.startPos.x;   //鼠标移动时，鼠标在拉框内的位置不变（即，拉框与鼠标相对静止）
            this.mydata[index].y=y-this.startPos.y;
            this.mydata[index].x2=this.mydata[index].x+this.startSize.w;
            this.mydata[index].y2=this.mydata[index].y+this.startSize.h;
          }
          else if(this.newItem===null) {   //若为放缩操作
            if(x-this.mydata[index].x<=t&&y-this.mydata[index].y<=t){this.mydata[index].x=x-t/2; this.mydata[index].y=y-t/2;}
            if(this.mydata[index].x2-x<=t&&y-this.mydata[index].y<=t){this.mydata[index].x2=x+t/2; this.mydata[index].y=y-t/2;}
            if(x-this.mydata[index].x<=t&&this.mydata[index].y2-y<=t){this.mydata[index].x=x-t/2; this.mydata[index].y2=y+t/2;}
            if(this.mydata[index].x2-x<=t&&this.mydata[index].y2-y<=t){this.mydata[index].x2=x+t/2; this.mydata[index].y2=y+t/2;}
            // this.mydata[index].x2=x+this.threshold;  //拉框右下角位置置为鼠标当前位置
            // this.mydata[index].y2=y+this.threshold;
          }
          /*border constraint*/
          if(this.mydata[index].x<=0)
            this.mydata[index].x=0;
          if(this.mydata[index].y<=0)
            this.mydata[index].y=0
          if(this.mydata[index].x2>=this.clientWidth)
            this.mydata[index].x2=this.clientWidth
          if(this.mydata[index].y2>=this.clientHeight)
            this.mydata[index].y2=this.clientHeight
        },
        //在拉框内释放鼠标左键时结束调整
        finishAdjust(e){
          this.isAdjust=false;  //调整标记置为false
          this.currentItem=this.originItem=null;
          this.value=[]
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
