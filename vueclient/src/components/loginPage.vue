<template>
  <div style="text-align:center" >
    <div class="is-background">
      <br />  <br />    <br />  <br />
      <img src="../assets/lablogo.png">
	   <br />  <br />
	    <div style="background-color:rgba(0,0,0,0.2) ; height:55px;  width:100%; " ><h1 style="color:white; letter-spacing:10px; font-size:35px; font-family:'Microsoft JhengHei';">数据标注平台</h1></div>


      <br />  <br />    <br />  <br />
      <div class="login-wrap" v-show="showLogin">
        <!--        <h3  style="font-size:20px">登录</h3>-->
        <br /><br />
        <input type="text" placeholder="请输入用户名" v-model="username" @keyup.enter="login">
        <input type="password" placeholder="请输入密码" v-model="password" @keyup.enter="login">
        <button v-on:click="login" style="font-size:20px">登录</button>
        <span v-on:click="ToRegister">没有账号？马上注册</span>
      </div>

      <div class="login-wrap" v-show="showRegister">
		    <br /><br />
        <input type="text" placeholder="请输入用户名" v-model="newUsername" @keyup.enter="register">
        <input type="password" placeholder="请输入密码" v-model="newPassword" @keyup.enter="register">
        <button v-on:click="register"  style="font-size:20px">注册</button>
        <span v-on:click="ToLogin">已有账号？马上登录</span>
      </div>
      <br />  <br />    <br />  <br />    <br />  <br />    <br />  <br />    <br />  <br />    <br />  <br />    <br />  <br />    <br />  <br />    <br />  <br />
	   <br />  <br />    <br />  <br />    <br />  <br />    <br />  <br />    <br />  <br />    <br />  <br />    <br />  <br />    <br />  <br />    <br />  <br />
    </div>
  </div>
</template>

<script>
export default {
  name: 'App',
	data(){
		return{
			username: '',
			password: '',
			newUsername: '',
			newPassword: '',
			tishi: '',
			showTishi: false,
			showLogin: true,
			showRegister: false
		}
	},
  mounted()
  {
		// if(getCookie('username')){
		// 	this.$router.push('/home')
		// }
	},
	methods: {
		login()
    {
			if(this.username === "" || this.password === "")
			{
        this.$message.warning("请输入用户名和密码");
			}
			else
      {
        let obj={user_name:this.username,user_password:this.password}
        var jsontext = encodeURIComponent(JSON.stringify(obj));
        this.$reqs.get('/login/?jsontext='+jsontext).then(res=>{
          if(res.data.data === 'no_user')
          {
            this.$message.error("该用户不存在");
          }
          else if(res.data.data === 'wrong_password')
          {
            this.$message.error("密码输入错误");
          }
          else if(res.data.data === 'success')
          {
            let str="欢迎您，"+this.username
            this.$message.success(str);
            this.$router.push
            ({
              name:'personalPage',
              query:{uid:res.data.id}
            })
          }
        })
			}
		},
		ToRegister(){
			this.showRegister = true
			this.showLogin = false
		},
		ToLogin(){
			this.showRegister = false
			this.showLogin = true
		},
		register(){
			if(this.newUsername === "" || this.newPassword === ""){
        this.$message.warn("请输入用户名或密码");
      }
      else
      {
        let obj={user_name:this.newUsername,user_password:this.newPassword}
        var jsontext = encodeURIComponent(JSON.stringify(obj));
        this.$reqs.get('/register/?jsontext='+jsontext).then(res=>{
          if(res.data.data === "success"){
            let str="欢迎"+this.newUsername+"使用LINKE标注平台"
            this.$message.success(str);
            this.username = ''
            this.password = ''
            setTimeout(function(){
              this.showRegister = false
              this.showLogin = true
              this.showTishi = false
            }.bind(this),1000)
          }
        })
			}
		}
  }
}
</script>

<style scoped>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 0px;
}
.login-wrap{text-align:center;}
input{display:block; width:250px; height:40px; line-height:40px; margin:0 auto; margin-bottom: 10px; outline:none; border:1px solid #888; padding:10px; box-sizing:border-box;}
p{color:red;}
button{display:block; width:250px; height:40px; line-height: 40px; margin:0 auto; border:none; background-color:#41b883; color:#fff; font-size:16px; margin-bottom:5px;}
span{cursor:pointer;}
span:hover{color:#41b883;}
.is-background{
  background:url(../assets/background.jpg)  no-repeat center center;
  background-size:cover;
  background-attachment:fixed;
  background-color:#CCCCCC;
}
</style>
