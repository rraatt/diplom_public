import { defineStore } from 'pinia';
import axios from '@/axios';

interface FileUploadState {
  file: File | null;
}

export const useFileUploadStore = defineStore({
  id: 'fileUpload',
  state: (): FileUploadState => ({
    file: null,
  }),
  actions: {
    setFile(file: File | null) {
      this.file = file;
    },
    clearFile() {
      this.file = null;
    },
    async uploadFile() {
      if (!this.file) {
        throw new Error('No file selected');
      }

      if (!this.isExcelFile(this.file)) {
        throw new Error('File must be in Excel format');
      }

      const formData = new FormData();
      formData.append('file', this.file);

      try {
        const response = await axios.post('/api/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        console.log(response.data); // Log the response from the server
        // Optionally, you can perform additional actions after the file is uploaded
      } catch (error) {
        console.error('Error uploading file:', error);
        throw new Error('Failed to upload file');
      }
    },
    isExcelFile(file: File) {
      return file.type === 'application/vnd.ms-excel' ||
             file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
    },
  },
});
