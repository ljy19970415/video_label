import Vue from 'vue'
import Router from 'vue-router'
import personalPage from '@/components/personalPage'
import loginPage from '@/components/loginPage'
import labelPage from '@/components/labelPage'
import object from '@/components/videoLabel_object'
import event from '@/components/videoLabel_keyAction'


Vue.use(Router)

export default new Router({
  mode: 'history',  //去掉url中的#
  routes: [
    {
      path: '/personal',
      name: 'personalPage',
      component: personalPage
    },
    {
      path:'/label',
      name:'label',
      component:labelPage
    },
    {
      path:'/',
      name:'login',
      component:loginPage
    },
    {
      path:'/object',
      name:'object',
      component:object
    },
    {
      path:'/event',
      name:'event',
      component:event
    }
  ]
})
