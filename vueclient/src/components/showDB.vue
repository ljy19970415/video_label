<template>
  <div class="showDataset">
    <el-row style="margin-top: 3%">
      <el-col  v-if="is_Object">
        <router-link :to="{ name: 'object', query:{user_id:this.user_id,video_id:this.video_id,fps:this.fps}}"><img :src="mysrc"/></router-link>
      </el-col>
      <el-col  v-else>
        <router-link :to="{ name: 'event', query:{user_id:this.user_id,video_id:this.video_id,fps:this.fps}}"><img :src="mysrc"/></router-link>
      </el-col>
    </el-row>
    <el-row>
      <el-col :span="13">
        <el-select filterable v-model="fps" size="small">
          <el-option
            v-for="item in fps_options"
            :key="item.value"
            :label="item.label"
            :value="item.value">
          </el-option>
        </el-select>
      </el-col>
      <el-col :span="2">
        <el-button @click="startLabel" type="primary" size="small" style="margin-left:60%">开始标注</el-button>
      </el-col>
    </el-row>
    <el-row>
      <el-col>
        <el-button style="width:200px;margin-top:3%" @click="removeVideo" icon="el-icon-minus" type="primary" size="small">移除视频</el-button>
      </el-col>
    </el-row>
    <br/><br/>
  </div>
</template>

<script scoped>
    export default {
        name: "showDB",
      props:{
        video_id:Number,
        user_id:Number,
        mysrc:String,
        isObject:Boolean
      },
      data(){
          return{
            fps_options:[{value:0,label:"原视频帧率"},{value:1,label:"每秒1张"},{value:2,label:"每秒2张"},{value:5,label:"每秒5张"},{value:10,label:"每秒10张"}],
            fps:1,
            is_Object:this.isObject
          }
      },
      mounted:function(){
      },
      methods:{
        removeVideo(){
          let obj={
            video_id:this.video_id,
            user_id:this.user_id,
            mysrc:this.mysrc,
            isObject:this.isObject
          }
          this.$emit('removeVideo',obj);
        },
        startLabel()
        {
          let _this=this
          if(this.isObject){
            this.$router.push({name:'object', query:{user_id:_this.user_id,video_id:_this.video_id,fps:_this.fps}})
          }
          else{
            this.$router.push({name:'event', query:{user_id:_this.user_id,video_id:_this.video_id,fps:_this.fps}})
          }
        }
      }
    }
</script>

<style lang="less" scoped>
.showDataset
{
  width:200px;
  margin-left:20%;
  img{
    width:100%;
    height:150px;
    justify-content: center;
  }
}
</style>
