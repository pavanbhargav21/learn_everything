<template>
  <v-dialog v-model="internalDialogVisible" max-width="1200px">
    <v-card>
      <v-card-title class="headline bg-primary white--text d-flex justify-space-between">
        App Store
        <v-btn icon @click="closeDialog" color="white">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      <v-card-text class="pa-4">
        <v-text-field
          v-model="search"
          append-icon="mdi-magnify"
          label="Search Workflow"
          single-line
          hide-details
          class="mb-4"
        ></v-text-field>
        <v-data-table
          :headers="headers"
          :items="filteredItems"
          :search="search"
          class="elevation-1 custom-table"
          :items-per-page="10"
          :footer-props="{
            'items-per-page-options': [10, 20, 50, 100, -1],
            'items-per-page-text': 'Rows per page:',
          }"
        >
          <template v-slot:item.actions="{ item }">
            <v-icon small class="mr-2" @click="editItem(item)">mdi-pencil</v-icon>
            <v-icon small @click="deleteItem(item)">mdi-delete</v-icon>
          </template>
          <template v-slot:item.isActive="{ item }">
            <v-chip :color="item.isActive ? 'green' : 'red'" small>
              {{ item.isActive ? 'Yes' : 'No' }}
            </v-chip>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <v-dialog v-model="editDialog" max-width="600px">
      <v-card>
        <v-card-title class="headline bg-primary white--text d-flex justify-space-between">
          {{ editedIndex === -1 ? 'New Item' : 'Edit Item' }}
          <v-btn icon @click="closeEditDialog" color="white">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text class="pt-4">
          <v-form ref="form" v-model="valid">
            <v-text-field
              v-model="editedItem.workflow"
              label="Workflow Name"
              :rules="[v => !!v || 'Workflow Name is required']"
              required
            ></v-text-field>
            <v-text-field
              v-model="editedItem.system"
              label="System"
              :rules="[v => !!v || 'System is required']"
              required
            ></v-text-field>
            <v-text-field
              v-model="editedItem.url"
              label="URL"
              :rules="[v => !!v || 'URL is required']"
              required
            ></v-text-field>
            <v-text-field
              v-model="editedItem.title"
              label="Title"
              :rules="[v => !!v || 'Title is required']"
              required
            ></v-text-field>
            <v-select
              v-model="editedItem.environment"
              :items="['UAT', 'Testing', 'Production']"
              label="Environment"
              :rules="[v => !!v || 'Environment is required']"
              required
            ></v-select>
            <v-switch v-model="editedItem.isActive" label="Is Active"></v-switch>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text @click="closeEditDialog">Cancel</v-btn>
          <v-btn color="blue darken-1" text @click="saveItem" :disabled="!valid">
            Save
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-dialog>
</template>

<script>
export default {
  name: 'AppStore',
  props: {
    dialogVisible: {
      type: Boolean,
      default: false
    }
  },
  data: () => ({
    internalDialogVisible: false,
    editDialog: false,
    valid: true,
    editedIndex: -1,
    search: '',
    editedItem: {
      slNo: null,
      workflow: '',
      system: '',
      url: '',
      title: '',
      environment: '',
      isActive: false
    },
    defaultItem: {
      slNo: null,
      workflow: '',
      system: '',
      url: '',
      title: '',
      environment: '',
      isActive: false
    },
    items: [],
    headers: [
      { text: 'Sl.no', align: 'start', value: 'slNo', width: '5%' },
      { text: 'Workflow Name', value: 'workflow', width: '20%' },
      { text: 'System', value: 'system', width: '15%' },
      { text: 'URL', value: 'url', width: '20%' },
      { text: 'Title', value: 'title', width: '15%' },
      { text: 'Environment', value: 'environment', width: '10%' },
      { text: 'Is Active', value: 'isActive', width: '5%' },
      { text: 'Actions', value: 'actions', sortable: false, width: '10%' }
    ]
  }),

  watch: {
    dialogVisible(val) {
      this.internalDialogVisible = val;
    },
    internalDialogVisible(val) {
      this.$emit('update:dialogVisible', val);
    }
  },
  computed: {
    filteredItems() {
      return this.items.filter(item =>
        item.workflow.toLowerCase().includes(this.search.toLowerCase())
      );
    }
  },

  created() {
    this.generateDummyData();
  },

  methods: {
    generateDummyData() {
      for (let i = 1; i <= 1000; i++) {
        this.items.push({
          slNo: i,
          workflow: `Workflow ${i}`,
          system: `System ${i}`,
          url: `http://example${i}.com`,
          title: `Title ${i}`,
          environment: i % 3 === 0 ? 'Production' : i % 3 === 1 ? 'UAT' : 'Testing',
          isActive: i % 2 === 0
        });
      }
    },

    editItem(item) {
      this.editedIndex = this.items.indexOf(item);
      this.editedItem = Object.assign({}, item);
      this.editDialog = true;
    },

    deleteItem(item) {
      const index = this.items.indexOf(item);
      if (confirm('Are you sure you want to delete this item?')) {
        this.items.splice(index, 1);
      }
    },

    closeEditDialog() {
      this.editDialog = false;
      this.$nextTick(() => {
        this.editedItem = Object.assign({}, this.defaultItem);
        this.editedIndex = -1;
      });
    },

    saveItem() {
      if (this.$refs.form.validate()) {
        if (this.editedIndex > -1) {
          Object.assign(this.items[this.editedIndex], this.editedItem);
        } else {
          this.editedItem.slNo = this.items.length + 1;
          this.items.push(this.editedItem);
        }
        this.closeEditDialog();
      }
    },

    closeDialog() {
      this.$emit('update:dialogVisible', false);
    }
  }
};
</script>
