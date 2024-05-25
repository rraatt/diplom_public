<template>
  <div style="display: flex; align-items: center;">
    <v-file-input
      label="File input"
      show-size
      @change="handleFileChange"
      append-icon="info"
    ></v-file-input>
    <v-btn
      color="info"
      text="Upload"
      variant="flat"
      class="top-right-button upload-file-button" @click="uploadFile"
    ></v-btn>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import { useFileUploadStore } from '@/stores/fileUploadStore';
import { useRouter } from 'vue-router';
import Swal from 'sweetalert2'

export default defineComponent({

  setup() {
    const fileUploadStore = useFileUploadStore();
    const router = useRouter();

// or via CommonJS
    const handleFileChange = (event: Event) => {
      const target = event.target as HTMLInputElement;
      const file = target.files?.[0];
      if (file) {
        fileUploadStore.setFile(file);
      }
    };

    const uploadFile = async () => {
      try {
        await fileUploadStore.uploadFile();
        // Show modal for successful upload
        Swal.fire({
          title: "",
          text: "Ексель файл успішно додано до БД",
          icon: "success"
        });
      } catch (error:any) {
        Swal.fire({
          title: "Error uploading file",
          text: error.toString(),
          icon: "error"
        });
      }
    };


    return {
      handleFileChange,
      uploadFile,
    };
  },
});
</script>

<style scoped>
/* Component styles */
</style>
