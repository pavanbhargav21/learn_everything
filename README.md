<template>
  <v-card>
    <v-toolbar color="black">
      <!-- ... (rest of your toolbar code) ... -->

      <template v-slot:extension>
        <!-- ... (rest of your extension slot code) ... -->
        <v-btn @click="openStore" append-icon="mdi-alpha-a-box" color="primary">
          <template v-slot:append>
            <v-icon color="success"></v-icon>
          </template>
          {{ storeButtonText }}
        </v-btn>
        <!-- ... (rest of your extension slot code) ... -->
      </template>
    </v-toolbar>

    <AppStore 
      v-if="activeTab === 0"
      :dialogVisible="storeDialogVisible[0]"
      @update:dialogVisible="updateStoreVisibility"
    />
    <KeyStore 
      v-if="activeTab === 1"
      :dialogVisible="storeDialogVisible[1]"
      @update:dialogVisible="updateStoreVisibility"
    />
    <VolumeStore 
      v-if="activeTab === 2"
      :dialogVisible="storeDialogVisible[2]"
      @update:dialogVisible="updateStoreVisibility"
    />

    <v-tabs-items v-model="activeTab">
      <!-- ... (rest of your tabs code) ... -->
    </v-tabs-items>
  </v-card>
</template>

<script>
import KeynameMapping from './KeynameMapping.vue';
import AppStore from './AppStore.vue';
import KeyStore from './KeyStore.vue';
import VolumeStore from './VolumeStore.vue';
import WorkflowConfigurator from './WorkflowConfigurator.vue';

export default {
  data() {
    return {
      tab: null,
      items: ['Workflow Master', 'Keyname Mapping', 'Volume Matrix'],
      activeTab: 0,
      storeDialogVisible: [false, false, false],
    };
  },
  components: {
    WorkflowConfigurator,
    AppStore,
    KeyStore,
    VolumeStore,
    KeynameMapping,
  },
  computed: {
    storeButtonText() {
      const texts = ['Go To AppStore', 'Go To KeyStore', 'Go To VolumeStore'];
      return texts[this.activeTab];
    },
  },
  methods: {
    openStore() {
      this.$set(this.storeDialogVisible, this.activeTab, true);
    },
    updateStoreVisibility(value) {
      this.$set(this.storeDialogVisible, this.activeTab, value);
    },
  },
};
</script>
