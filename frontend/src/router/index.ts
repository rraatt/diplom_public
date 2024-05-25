import { createRouter, createWebHistory } from 'vue-router'
import FileUpload from "@/views/FileUpload.vue";
import ButtonPage from "@/views/ScanPage.vue";
import ReportList from "@/components/ReportShow.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/upload',
      name: 'upload',
      component: FileUpload
    },
    {
    path: '/scan',
    name: 'ButtonPage',
    component: ButtonPage,
    },
    {
      path: '/',
      name: 'reports',
      component: ReportList,
    }
  ]
})

export default router
