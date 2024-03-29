// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';
import 'vueui-widgets/dist/index.css'
import VueUI from 'vueui-widgets'

Vue.config.productionTip = false

//配置ElementUI
Vue.use(ElementUI);
//配置vueui-widgets
Vue.use(VueUI);
//配置跨域
import axios from 'axios';//引入axios组件
axios.defaults.withCredentials=false;  //跨域保存session有用；由于是跨域请求，我们需要配置withCredentials为true，这样避免每次都被识别为新的请求。
axios.defaults.baseURL = "http://localhost:5415"; //打包的时候直接删掉，默认的node服务器路径在这里配置
Vue.prototype.$reqs = axios;  //将 axios 赋值给 Vue，方便在子组件里面使用

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  components: { App },
  template: '<App/>'
})
