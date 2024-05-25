<!-- Modal.vue -->
<template>
  <div v-if="visible" class="modal">
    <div class="modal-content">
      <p>{{ message }}</p>
      <button @click="closeModal">OK</button>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    visible: Boolean,
    message: String,
    onClose: Function,
  },
  methods: {
    closeModal() {
      this.$emit('closeModal'); // Emit event to parent component to close the modal
    },
  },
};
</script>

<style scoped>
/* Modal styles */
</style>
