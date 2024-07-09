<template>
  <v-container>
    <v-row>
      <v-col>
        <v-text-field
          label="Please specify the workflow name"
          prepend-icon="mdi-account"
          solo
        >
          <template v-slot:append>
            <v-icon @click="openDialog">mdi-plus</v-icon>
          </template>
        </v-text-field>
      </v-col>
    </v-row>

    <v-dialog v-model="dialog" max-width="500">
      <v-card>
        <v-card-title>
          <span class="headline">Popup Form</span>
        </v-card-title>
        <v-card-text>
          <v-form>
            <v-text-field label="Field 1"></v-text-field>
            <v-text-field label="Field 2"></v-text-field>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" @click="dialog = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>



<script>
export default {
  data() {
    return {
      dialog: false
    };
  },
  methods: {
    openDialog() {
      this.dialog = true;
    }
  }
};
</script>