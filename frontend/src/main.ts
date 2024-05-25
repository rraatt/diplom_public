import './assets/main.css'
import 'material-design-icons-iconfont/dist/material-design-icons.css'
import { aliases, mdi } from 'vuetify/iconsets/mdi'
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

import VueSweetalert2 from 'vue-sweetalert2';
import 'sweetalert2/dist/sweetalert2.min.css';

import App from './App.vue'
import router from './router'

const vuetify = createVuetify({
  components,
  directives,
})

const app = createApp(App)

app.use(vuetify)
app.use(VueSweetalert2)
app.use(createPinia())
app.use(router)

app.mount('#app')
