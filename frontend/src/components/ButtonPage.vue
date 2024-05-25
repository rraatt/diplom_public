<template>
  <div style="display: flex; justify-content: space-around; align-items: center;">
    <v-btn
      color="info"
      text="Оновити інформацію з сайту nfv.ukrintei.ua"
      variant="flat"
      style="float: right;"
      :disabled="reestrButtonDisabled"
      class="top-right-button request-button" @click="parseReestr"
    ></v-btn>
    <v-btn
      color="green"
      text="Почати сканування"
      variant="flat"
      style="float: right;"
      :disabled="scanButtonDisabled"
      class="top-right-button request-button" @click="makeRequest"
    ></v-btn>
    <v-btn
      color="info"
      text="Оновити інформацію з сайту Rada.kpi"
      variant="flat"
      style="float: right;"
      :disabled="radaButtonDisabled"
      class="top-right-button request-button" @click="parseRada"
    ></v-btn>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import axios from '@/axios'; // Import Axios for making HTTP requests
import Swal from 'sweetalert2'

export default defineComponent({

  setup() {
    const radaButtonDisabled = ref(true); // Initially disable the button
    const scanButtonDisabled = ref(false);
    const reestrButtonDisabled = ref(false);
    const makeRequest = async () => {
      if (radaButtonDisabled.value === true){
        fireModal('Сканування бази вчених рад у прогресі!!!')
      }
      else{
        const response = await axios.post('/api/start-scan')
        scanButtonDisabled.value = true;
        fireModal('Почалось сканування наявної бази');
        setTimeout(() => {
          scanButtonDisabled.value = false;
        }, 60 * 1000);}

    };

    const fireModal = (message: string) => {
      Swal.fire({
        icon: "info",
        title: message,
        showConfirmButton: false,
        timer: 1500
      });
    };

    const parseReestr = async () => {
      try {
        fireModal('Почалось сканування бази фахових видань');
        reestrButtonDisabled.value = true;
        const response = await axios.post('/api/parse-reestr');
        console.log(response)
        setTimeout(() => {
          reestrButtonDisabled.value = false;
        }, 60 * 1000);
      } catch (error) {
        console.error('Error making request:', error);
      }
    }

    const parseRada = async () => {
      try {
        const response = await axios.post('/api/parse-rada');
        console.log(response)
        radaButtonDisabled.value = true;
        fireModal('Почався парсинг бази вчених рад, кнопка буде доступна через 4 години');
      } catch (error) {
        console.error('Error making request:', error);
      }
    };

    const fetchButtonState = async () => {
      try {
        const response = await axios.get('/api/button-state');
        radaButtonDisabled.value = response.data.button_disabled;
      } catch (error) {
        console.error('Error getting button state:', error);
      }
    };



    // Fetch button state from the backend when the component is mounted
    onMounted(fetchButtonState);

    // Poll the backend every 30 seconds to update the button state
    setInterval(fetchButtonState, 30000);

    return {
      makeRequest,
      parseRada,
      parseReestr,
      radaButtonDisabled,
      scanButtonDisabled,
      reestrButtonDisabled
    };
  },
});
</script>

<style scoped>
.top-right {
  position: absolute;
  top: 10px;
  right: 10px;
}
</style>
<script setup lang="ts">
</script>