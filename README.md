<template>
  <v-container>
    <v-btn @click="openAppStore" prepend-icon="mdi-alpha-a-box" color="primary">
      <template v-slot:prepend>
        <v-icon color="success"></v-icon>
      </template>
      Go to App Store
    </v-btn>
    
    <AppStore :dialogVisible.sync="appStoreDialogVisible" />
  </v-container>
</template>

<script>
import AppStore from './AppStore.vue';

export default {
  name: 'MainComponent',
  components: {
    AppStore
  },
  data() {
    return {
      appStoreDialogVisible: false
    };
  },
  methods: {
    openAppStore() {
      this.appStoreDialogVisible = true;
    }
  }
};
</script>
