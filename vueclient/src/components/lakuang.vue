<<template>
  <div class="mycanvas-container">
    <el-container  style=" border: 1px solid #eee">
      <el-header style="text-align: center; font-size: 35px">LINKE数据标注平台</el-header>
      <el-main>
        <el-row>
          <el-col :span="8">
    <div class="left">
      <p>展示视口</p>
      <div class="myshow">
        <img :src="mysrc" alt width="100%" />
      </div>
    </div>
          </el-col>
          <el-col :span="8">
    <div class="center">
      <p>操作视口</p>
      <div class="myedit" ref="myedit" @mousedown.prevent="onMousedown" @mousemove="onMousemove" @mouseup="onMouseup">
        <img :src="mysrc" @load="handleLoad"/>
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
          <el-col :span="8">
            <div class="right">
              <input v-show="0" ref="newFile" type="file" class="mybutton" @change="newFile" />
              <el-button class="asideButton" @click="selectNewFile">导入新图片</el-button>
              <input v-show="0" ref="labelFile" type="file" class="mybutton" @change="labelFile" />
              <el-button class="asideButton" @click="selectLabelFile">导入已标注图片</el-button>
              <el-button style="margin-top: 20px;margin-left:0px" @click="saveFile">保存图片</el-button>
            </div>
          </el-col>
        </el-row>
        <div class="myMenu" v-show="currentItem" :style="mymenu.style">
          <el-row><el-col :span="24">
            <el-input v-model="labelContent" placeholder="此处显示标签"></el-input>
          </el-col></el-row>
          <el-row><el-col :span="24">
            <el-cascader
              v-model="labelContent"
              :options="options"
              :props="{ expandTrigger: 'hover' }"
              @change="changeLabel">
            </el-cascader>
          </el-col>
          </el-row>
          <el-row :gutter="5">
            <el-col :span="12"><el-button type="primary" @click="chooseBlock">修改</el-button></el-col>
            <el-col :span="12"><el-button type="primary" @click="finishAdjust">确认修改</el-button></el-col>
          </el-row>
          <el-row :gutter="5">
            <el-col :span="12"><el-button type="primary" @click="addLabel">确认</el-button></el-col>
            <el-col :span="12"><el-button type="primary" @click="onRemoveItem">删除</el-button></el-col>
          </el-row>
        </div>
      </el-main>
      <el-footer style="text-align: right; font-size: 10px">@版权归LINKE实验室所有</el-footer>
    </el-container>
  </div>
</template>

<script>
  export default {
    data() {
      return {
        mysrc: "",
        mydata: [],  //存储了所有框的信息，每个框的信息由index与item构成，其中index为索引，item为拉框对象
        currentItem:null,  //表示目前选中的拉框
        originItem:null,  //更改前的拉框
        labelContent:"",  //初始化标签内容
        isAdjust:false,  //是否在调整画框
        isDrag:true,  //是否是拖拽操作
        threshold:15,  //鼠标在框右下角的判断范围
        mymenu: { style: { left: 0, top: 0 } },  //标注框左上角位置
        isNewFile:true, //保存的是否为新图片
        options: [{   //提供的可选标注
          value: 'human',
          label: '人类',
          children: [{
            value: 'man',
            label: 'man',
          },{
            value: 'woman',
            label: 'woman',
          }]
        },{
          value: 'animal',
          label: '动物',
          children: [{
            value: 'dog',
            label: 'dog',
          },{
            value: 'cat',
            label: 'cat',
          }]
        }]
      };
    },
    mounted() {
      console.log("lalala");
      this.$reqs.get('/label/getDatasetPath',{params:{id1:1}}).then(res=>{
        if(res.status===200&&res.data){
          console.log(res.data.data)
        }
      })
    },
    methods: {
      /****导入图片相关函数****/
      //在加载完新图片后进行机器预识别
       handleLoad(){
        if(!this.isNewFile) return;
         /*请求webAPI*/
         let _this=this;
         var fd = new FormData();
         fd.append('img', this.image);
         this.$reqs.post('http://114.214.161.227:5001/object-detection',fd).
         then(function (response){
           _this.mydata = response.data;
           var picWidth = document.getElementsByTagName("img")[1].naturalWidth;
           var clientWidth = document.getElementsByTagName("img")[1].clientWidth;
           let temp = clientWidth/picWidth;
           for(let i = 0;i<_this.mydata.length;i++){
             _this.mydata[i].x *= temp;
             _this.mydata[i].y *= temp;
             _this.mydata[i].x2 *= temp;
             _this.mydata[i].y2 *= temp;
           }
         }).catch(function(error){
           console.log(error);
         });
         /*请求webAPI*/
      },
      // 用户选择新图片
      newFile(event) {
        const files=event.target.files;
        let filename=files[0].name;
        if(filename.lastIndexOf('.')<=0){
          return alert("Please add a valid image!")
        }
        this.image=files[0];
        this.mysrc = window.URL.createObjectURL(event.target.files[0]);
      },
      //用户选择已标注的图片
      labelFile(event){
        const files=event.target.files
        let filename=files[0].name
        if(filename.lastIndexOf('.')<=0){
          return alert("Please add a valid image!")
        }
        else{
          this.mysrc = window.URL.createObjectURL(event.target.files[0]);
          //获取该文件的json，将该json赋值给mydata数组
          this.fid=filename.substring(0,filename.lastIndexOf("."));
          this.$reqs.get('/label/loadLabel',{params:{fid:this.fid}}).then(res=>{
            if(res.status===200&&res.data){
              console.log(res.data.data);
              this.mydata=res.data.data;
            }
          })
          console.log("before")
          console.log(this.mydata);
        }
      },
      // “导入新图片”按钮触发input组件
      selectNewFile() {
        this.mydata=[];
        this.$refs.newFile.click();
        this.isNewFile=true; //导入图片为新图片
      },
      //“导入已标记图片”按钮触发input组件
      selectLabelFile() {
        this.mydata=[];
        this.$refs.labelFile.click();
        this.isNewFile=false;
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
        if(this.isAdjust||e.button === 2 ) return;  //若是右键显示菜单，则不做处理
        //this.currentItem = null
        console.log("onMousedown");
        let { x, y } = this.getXY(e)  //获得鼠标坐标
        this.newItem = { x, y, x2:x, y2:y,label:"" }
        this.startPos = { x, y }   //记录鼠标初始位置
        this.mydata.push(this.newItem)
      },
      //当鼠标移动时，若此时正在拉框，则更新拉框右下角的位置，否则不做操作
      onMousemove(e) {
        if (!this.newItem) return;
        console.log("onMousemove");
        this.newItem.x2=this.startPos.x+Math.abs(this.getXY(e).x-this.startPos.x);
        this.newItem.y2=this.startPos.y+Math.abs(this.getXY(e).y-this.startPos.y);
      },
      //当鼠标左键释放，清空现有拉框与初始位置
      onMouseup(e) {
        console.log("onMouseup");
        this.newItem = this.startPos = null;
        this.mydata = this.mydata.filter(_ => (_.x2-_.x) > 5 && (_.y2-_.y) > 5)  //过滤掉过小的标注框
      },
      //在拉框上点击右键时出现标注框
      onContextmenu(item,e) {
        console.log("onContextmenu");
        this.currentItem=item;  //当前框置为此拉框
        this.originItem=item;   //记录此拉框的初始状态
        console.log("this.mydata:");
        console.log(this.mydata);
        console.log("contextMenu's currentaItem:");
        console.log(this.currentItem);
        console.log("contextMenu's originItem:");
        console.log(this.originItem);
        this.labelContent=item.label;  //将当前标签内容置为此拉框的标签内容
        this.mymenu = {  //拉框左上角位置为当前鼠标点击位置
          style: {
            top: e.clientY + 'px',
            left: e.clientX + 'px'
          }
        }
      },
      //删除拉框
      onRemoveItem() {
        console.log("onRemoveItem");
        this.mydata.splice(this.mydata.indexOf(this.originItem), 1); //indexOf找到该item的位置，1表示删除该元素
        this.currentItem=this.originItem=null;  //清空当前拉框与此拉框初始状态
      },

      /****修改拉框相关函数****/
      //将用户在标注框里选中的标签赋值给labelContent属性
      changeLabel(value) {
        this.labelContent=value.toString();
      },
      //点击确认键后，当前拉框的标注内容改为labelContent的内容，修改mydata中此拉框的标注信息
      addLabel() {
        this.currentItem.label=this.labelContent;
        this.mydata.splice(this.mydata.indexOf(this.originItem), 1,this.currentItem);
        this.currentItem=this.originItem=null;
      },
      //点击修改按钮后，标记调整开始
      chooseBlock()
      {
        console.log("chooseBlock");
        this.isAdjust=true;     //调整拉框标记置为true
        this.index=this.mydata.indexOf(this.originItem);
        this.currentItem=this.originItem=null;
      },
      //在拉框内按下鼠标左键时即选中此拉框准备调整（拖拽或放缩）
      startAdjust(e){
        console.log("startAdjust");
        if(!this.isAdjust) return;  //若不是调整拉框操作，则返回
        let { x, y } = this.getXY(e);  //获取鼠标当前位置
        this.startPos={x,y};    //记录鼠标初始位置
        let index=this.index;
        this.isDrag = !(Math.abs(x - this.mydata[index].x2) <= this.threshold && Math.abs(y - this.mydata[index].y2) <= this.threshold);  //若鼠标位置距离右小角在threshold内，则为放缩操作，否则为拖拽操作
        if(this.isDrag)  //若为拖拽操作
        {
          this.startPos={x:x-this.mydata[index].x,y:y-this.mydata[index].y}   //记录鼠标在拉框内的位置（即，鼠标相对拉框的坐标）
          this.startSize={w:this.mydata[index].x2-this.mydata[index].x,h:this.mydata[index].y2-this.mydata[index].y}; //记录框的初始w与h
        }
      },
      //在拉框内移动鼠标时，表示对此拉框正在进行拖拽或放缩操作，针对不同操作函数做出不同处理
      adjustBlock(e){
        console.log("adjustBlock");
        if(!this.isAdjust||!this.startPos) return;  //若没有开始标注，则返回
        let index=this.index;
        let{x,y}=this.getXY(e);   //记录鼠标当前位置
        if(this.isDrag)  //若为拖拽操作
        {
          this.mydata[index].x=x-this.startPos.x;   //鼠标移动时，鼠标在拉框内的位置不变（即，拉框与鼠标相对静止）
          this.mydata[index].y=y-this.startPos.y;
          this.mydata[index].x2=this.mydata[index].x+this.startSize.w;
          this.mydata[index].y2=this.mydata[index].y+this.startSize.h;
        }
        else {   //若为放缩操作
          this.mydata[index].x2=x+this.threshold;  //拉框右下角位置置为鼠标当前位置
          this.mydata[index].y2=y+this.threshold;
        }
      },
      //在拉框内释放鼠标左键时结束调整
      finishAdjust(e){
        console.log("finishAdjust");
        this.isAdjust=false;  //调整标记置为false
        this.currentItem=this.originItem=null;
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
      },

      /****保存标注图片相关函数****/
      saveFile(event){
        event.preventDefault();
        if(this.isNewFile)  //若保存的是新图片
        {
          //上传图片
          let fd=new FormData()
          fd.append('file',this.image)
          this.$reqs.post('/label/uploadNewPic',fd,{headers:{"Content-Type":"multipart/form-data"}}).then(res=>{

          }).catch(error=>{
            console.log(error)
          });
          //上传标注信息
          this.$reqs.post('/label/uploadNewLabel',{
            mydata:this.mydata
          }).then(res=>{

          }).catch(error=>{
            console.log(error);
          })
        }
        else{  //若需要更新已有图片的标注信息
          console.log("post/updateLabel");
          console.log(this.fid);
          console.log(this.mydata);
          this.$reqs.post('/label/updateLabel',{
            fid:this.fid,
            mydata:this.mydata
          }).then(res=>{

          }).catch(error=>{
            console.log(error);
          })
        }
      }
    }
  };
</script>
<style lang="less" scoped>
  .el-row{
    margin-bottom: 5%;
  }
  .el-header {
    background-color: #B3C0D1;
    color: #333;
    line-height: 60px;
  }
  .el-footer {
    background-color: #B3C0D1;
    color: #333;
    line-height: 60px;
  }
  // 设置绘图样式1
  body {
    user-select: none;
  }

  .myMenu
  {
    position: fixed;
    top: 400px;
    left: 400px;
    width: 200px;
    padding: 8px 0;
    background-color: #fff;
    > * {
      width:100%
    }
  }
  .asideButton{
    margin-top: 50%;
    display: block;
  }

  // 设置绘图样式2
  .mycanvas-container
  {
    display: flex;
    justify-content: center;
    align-items: center;
    .left,
    .center,
    .right
    {
      width: 300px;
      margin-left:40%;
      p
      {
        text-align: center;
        font-size: 20px;
        margin-left:50%;
      }
      .myshow,
      .myedit
      {
        width: 450px;
        //height: 500px;
        //border: 1px solid #000;
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
    .right
    {
      width: 150px;
      display: flex;
      justify-content: center;
      align-items:center;
      flex-direction: column;
    }
  }
</style>
