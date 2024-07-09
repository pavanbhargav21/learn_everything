<template>
  <v-dialog v-model="dialog" max-width="500px">
    <v-card>
      <v-card-title>
        <span class="headline">Additional Form</span>
      </v-card-title>
      <v-card-text>
        <v-form>
          <v-text-field label="Additional Input 1" v-model="form.input1"></v-text-field>
          <v-text-field label="Additional Input 2" v-model="form.input2"></v-text-field>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="blue darken-1" text @click="closeDialog">Cancel</v-btn>
        <v-btn color="blue darken-1" text @click="saveForm">Save</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import axios from 'axios';

export default {
  props: {
    dialog: Boolean
  },
  data() {
    return {
      form: { input1: '', input2: '' }
    }
  },
  methods: {
    closeDialog() {
      this.$emit('update:dialog', false);
    },
    async saveForm() {
      try {
        const response = await axios.post('http://your-backend-url.com/api/save-additional', this.form);
        console.log('Additional form data saved successfully:', response.data);
        this.$emit('update:dialog', false);
      } catch (error) {
        console.error('Error saving additional form data:', error);
      }
    }
  }
}
</script>



<template>
  <v-app>
    <v-container>
      <v-toolbar>
        <v-toolbar-title>My App</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-btn icon>
          <v-icon>mdi-apps</v-icon>
        </v-btn>
        <v-btn icon>
          <v-icon>mdi-upload</v-icon>
        </v-btn>
      </v-toolbar>
      
      <v-tabs v-model="activeTab" background-color="primary" dark>
        <v-tab v-for="tab in tabs" :key="tab">{{ tab }}</v-tab>
        <v-tab @click="addTab">More</v-tab>
      </v-tabs>
      
      <v-tabs-items v-model="activeTab">
        <v-tab-item v-for="tab in tabs" :key="tab">
          <v-card flat>
            <v-card-title>{{ tab }} Form</v-card-title>
            <v-card-text>
              <v-form>
                <v-text-field
                  label="Input 1"
                  v-model="formData[tab].input1"
                  append-outer-icon="mdi-plus"
                  @click:append-outer="openDialog"
                ></v-text-field>
                <v-text-field label="Input 2" v-model="formData[tab].input2"></v-text-field>
                <v-text-field label="Input 3" v-model="formData[tab].input3"></v-text-field>
                <v-btn color="primary" @click="saveForm(tab)">Save</v-btn>
              </v-form>
            </v-card-text>
          </v-card>
        </v-tab-item>
      </v-tabs-items>
      
      <PopupForm :dialog.sync="dialog" />
    </v-container>
  </v-app>
</template>

<script>
import axios from 'axios';
import PopupForm from './PopupForm.vue';

export default {
  components: {
    PopupForm
  },
  data() {
    return {
      activeTab: 0,
      tabs: ['Tab 1', 'Tab 2', 'Tab 3'],
      formData: {
        'Tab 1': { input1: '', input2: '', input3: '' },
        'Tab 2': { input1: '', input2: '', input3: '' },
        'Tab 3': { input1: '', input2: '', input3: '' },
      },
      dialog: false
    }
  },
  methods: {
    addTab() {
      const newTabIndex = this.tabs.length + 1;
      const newTabName = `Tab ${newTabIndex}`;
      this.tabs.push(newTabName);
      this.$set(this.formData, newTabName, { input1: '', input2: '', input3: '' });
    },
    async saveForm(tab) {
      try {
        const response = await axios.post('http://your-backend-url.com/api/save', this.formData[tab]);
        console.log(`Form data for ${tab} saved successfully:`, response.data);
      } catch (error) {
        console.error(`Error saving form data for ${tab}:`, error);
      }
    },
    openDialog() {
      this.dialog = true;
    }
  }
}
</script>