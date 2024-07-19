<template>
  <v-container class="pb-16">
    <v-form ref="form" @submit.prevent="submitForm" v-model="valid">
      <v-row>
        <v-col cols="8">
          <v-autocomplete
            v-model="autocompleteValuee"
            :items="workflowNames.map(workflow => workflow.workflow_name)"
            label="Please specify the workflow name"
            placeholder="Type"
            prepend-icon="mdi-database-arrow-up"
            solo
            :rules="[v => !!v || 'Workflowname is required']"
          >
            <template v-slot:prepend>
              <span
                style="
                  margin-right: 10px;
                  font-family: 'Gill Sans';
                  font-weight: bold;
                "
                >Workflow Name</span
              >
            </template>
          </v-autocomplete>
        </v-col>
      </v-row>

      <!-- Patterns -->
      <v-row>
        <v-col
          v-for="(pattern, patternIndex) in patterns"
          :key="patternIndex"
          cols="12"
          sm="6"
          class="d-flex flex-column"
        >
          <v-card class="flex-grow-1 mb-2" elevation="2">
            <v-card-title class="d-flex align-center py-2">
              <v-icon left color="seashell" small>mdi-google-analytics</v-icon>
              <span class="text-subtitle-2">{{ pattern.name }}</span>
              <v-spacer></v-spacer>
              <v-btn
                icon
                x-small
                @click="removePattern(patternIndex)"
                color="black"
              >
                <v-icon x-small>mdi-delete-alert</v-icon>
              </v-btn>
            </v-card-title>
            <v-divider></v-divider>
            <v-card-text class="pa-2">
              <!-- Field headers -->
              <v-row dense class="mb-1">
                <v-col cols="4">
                  <span class="text-caption font-weight-bold">Volume Key</span>
                </v-col>
                <v-col cols="4">
                  <span class="text-caption font-weight-bold">Type</span>
                </v-col>
                <v-col cols="4">
                  <span class="text-caption font-weight-bold">Layout</span>
                </v-col>
              </v-row>

              <!-- Fields -->
              <v-row
                v-for="(field, fieldIndex) in pattern.fields"
                :key="fieldIndex"
                dense
                class="mb-1"
              >
                <v-col cols="4">
                  <v-text-field
                    v-model="field.keyName"
                    label="Key value"
                    dense
                    outlined
                    hide-details
                  ></v-text-field>
                </v-col>
                <v-col cols="4">
                  <v-select
                    v-model="field.type"
                    :items="types"
                    label="Label"
                    dense
                    outlined
                    hide-details
                  ></v-select>
                </v-col>
                <v-col cols="4">
                  <v-select
                    v-model="field.layout"
                    :items="layouts"
                    label="Layout"
                    dense
                    outlined
                    hide-details
                  ></v-select>
                </v-col>
              </v-row>

              <v-row dense class="mt-1">
                <v-col cols="6">
                  <v-btn
                    @click="addFieldSet(patternIndex)"
                    x-small
                    color="primary"
                    outlined
                  >
                    <v-icon left x-small>mdi-plus</v-icon> Add Field
                  </v-btn>
                </v-col>
                <v-col cols="6">
                  <v-btn
                    @click="removeFieldSet(patternIndex, pattern.fields.length - 1)"
                    x-small
                    color="error"
                    outlined
                  >
                    <v-icon left x-small>mdi-minus</v-icon> Remove Field
                  </v-btn>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-form>

    <!--<v-footer app fixed class="pa-0"> -->
    <v-card flat tile width="100%" class="text-center">
      <v-card-text>
        <v-btn @click="addPattern" color="primary" class="mr-2">
          <v-icon left>mdi-plus</v-icon> Add Pattern
        </v-btn>
        <v-btn
          type="submit"
          color="success"
          :disabled="!valid"
          @click="submitForm"
          >Save</v-btn
        >
      </v-card-text>
    </v-card>
    <!-- </v-footer> -->
  </v-container>
</template>

<script>
  export default {
    data() {
      return {
        patterns: [
          {
            id: 1,
            name: 'Pattern1',
            fields: [{ keyName: '', type: '', layout: '' }],
          },
        ],
        nextPatternId: 2,
        types: ['Field', 'Button'],
        layouts: ['Horizontal', 'Vertical'],
        autocompleteValuee: '',
        valid: false,
        workflowNames: [],
        payload: null,
      }
    },
    created() {
      this.fetchWorkflowNames()
    },
    methods: {
      addPattern() {
        this.patterns.push({
          id: this.nextPatternId,
          name: `Pattern${this.nextPatternId}`,
          fields: [{ keyName: '', type: '', layout: '' }],
        })
        this.nextPatternId++
      },
      removePattern(patternIndex) {
        this.patterns.splice(patternIndex, 1)
        this.updatePatternNames()
      },
      updatePatternNames() {
        this.patterns.forEach((pattern, index) => {
          pattern.name = `Pattern${index + 1}`
        })
        this.nextPatternId = this.patterns.length + 1
      },
      addFieldSet(patternIndex) {
        this.patterns[patternIndex].fields.push({
          keyName: '',
          type: '',
          layout: '',
        })
      },
      removeFieldSet(patternIndex, fieldIndex) {
        if (this.patterns[patternIndex].fields.length > 1) {
          this.patterns[patternIndex].fields.splice(fieldIndex, 1)
        }
      },
      async fetchWorkflowNames() {
        try {
          const response = await axios.get('/api/workflows')
          this.workflowNames = response.data.map(workflow => ({
            workflow_name: workflow.workflow_name,
            id: workflow.id,
          }))
          console.log('Workflow Names:', this.workflowNames)
        } catch (error) {
          console.error(error)
        }
      },
      async submitForm() {
        if (this.$refs.form.validate()) {
          const selectedWorkflow = this.workflowNames.find(
            option => option.workflow_name === this.autocompleteValuee
          )

          if (selectedWorkflow) {
            console.log('Getting payload data...')
            this.payload = this.patterns.flatMap(pattern =>
              pattern.fields.map(field => ({
                workflowId: selectedWorkflow.id,
                patternName: pattern.name,
                keyname: field.keyName,
                layout: field.layout,
                types: field.type,
              }))
            )
            try {
              console.log('payload is', this.payload)
              await axios.post('/api/volumematrix', this.payload)
              alert('Data submitted successfully!')
              EventBus.$emit('volume-added')
              this.fetchWorkflowNames()
            } catch (error) {
              console.error('Error submitting data:', error)
            }
          }
        }
      },
    },
  }
</script>

<style scoped>
  .v-card-title {
    background-color: royalblue;
  }

  .pattern-container {
    margin-bottom: 10px;
  }

  .field-set {
    margin-bottom: 5px;
  }

  .field-set .field {
    margin-bottom: 5px;
  }

  button {
    margin-top: 1px;
    margin-bottom: 1px;
  }
</style>































<template>
  <v-container>
    <v-form ref="form" @submit.prevent="submitForm" v-model="valid">
      <v-row>
        <v-col cols="8">
          <v-autocomplete
            v-model="autocompleteValuee"
            :items="workflowNames.map(workflow => workflow.workflow_name)"
            label="Please specify the workflow name"
            placeholder="Type"
            prepend-icon="mdi-database-arrow-up"
            solo
            :rules="[v => !!v || 'Workflow name is required']"
          >
            <template v-slot:prepend>
              <span style="margin-right: 10px; font-family: 'Gill Sans'; font-weight: bold;">Workflow Name</span>
            </template>
          </v-autocomplete>
        </v-col>
      </v-row>

      <!-- Patterns -->
      <v-row>
        <v-col v-for="(pattern, patternIndex) in patterns" :key="patternIndex" cols="12" md="6">
          <v-card class="mb-4" elevation="2">
            <v-card-title class="d-flex align-center">
              <v-icon left color="primary">mdi-google-analytics</v-icon>
              {{ pattern.name }}
              <v-btn icon small class="ml-2" @click="removePattern(patternIndex)" color="black">
                <v-icon small>mdi-delete-alert</v-icon>
              </v-btn>
            </v-card-title>
            <v-divider></v-divider>
            <v-card-text>
              <!-- Field headers -->
              <v-row class="mb-2">
                <v-col cols="4">
                  <strong class="text-subtitle-2">Volume Key</strong>
                </v-col>
                <v-col cols="4">
                  <strong class="text-subtitle-2">Type</strong>
                </v-col>
                <v-col cols="4">
                  <strong class="text-subtitle-2">Layout</strong>
                </v-col>
              </v-row>

              <!-- Fields -->
              <v-row v-for="(field, fieldIndex) in pattern.fields" :key="fieldIndex" class="mb-2">
                <v-col cols="4">
                  <v-text-field v-model="field.keyName" label="Key value" dense outlined></v-text-field>
                </v-col>
                <v-col cols="4">
                  <v-select v-model="field.type" :items="types" label="Label" dense outlined></v-select>
                </v-col>
                <v-col cols="4">
                  <v-select v-model="field.layout" :items="layouts" label="Layout" dense outlined></v-select>
                </v-col>
              </v-row>

              <v-row class="mt-2">
                <v-col cols="6">
                  <v-btn @click="addFieldSet(patternIndex)" small color="primary" outlined>
                    <v-icon left small>mdi-plus</v-icon> Add Field
                  </v-btn>
                </v-col>
                <v-col cols="6">
                  <v-btn @click="removeFieldSet(patternIndex, pattern.fields.length - 1)" small color="error" outlined>
                    <v-icon left small>mdi-minus</v-icon> Remove Field
                  </v-btn>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <v-row>
        <v-col>
          <v-btn @click="addPattern" color="primary">
            <v-icon left>mdi-plus</v-icon> Add Pattern
          </v-btn>
        </v-col>
      </v-row>

      <v-btn type="submit" color="success" :disabled="!valid" class="mt-4">Save</v-btn>
    </v-form>
  </v-container>
</template>

<script>
import axios from '../axios';

export default {
  data() {
    return {
      patterns: [
        {
          id: 1,
          name: 'Pattern1',
          fields: [{ keyName: '', type: '', layout: '' }]
        }
      ],
      nextPatternId: 2,
      types: ['Field', 'Button'],
      layouts: ['Horizontal', 'Vertical'],
      autocompleteValuee: "",
      valid: false,
      workflowNames: [],
      payload: null
    };
  },
  created() {
    this.fetchWorkflowNames();
  },
  methods: {
    addPattern() {
      this.patterns.push({
        id: this.nextPatternId,
        name: `Pattern${this.nextPatternId}`,
        fields: [{ keyName: '', type: '', layout: '' }]
      });
      this.nextPatternId++;
    },
    removePattern(patternIndex) {
      this.patterns.splice(patternIndex, 1);
      this.updatePatternNames();
    },
    updatePatternNames() {
      this.patterns.forEach((pattern, index) => {
        pattern.name = `Pattern${index + 1}`;
      });
      this.nextPatternId = this.patterns.length + 1;
    },
    addFieldSet(patternIndex) {
      this.patterns[patternIndex].fields.push({ keyName: '', type: '', layout: '' });
    },
    removeFieldSet(patternIndex, fieldIndex) {
      if (this.patterns[patternIndex].fields.length > 1) {
        this.patterns[patternIndex].fields.splice(fieldIndex, 1);
      }
    },
    async fetchWorkflowNames() {
      try {
        const response = await axios.get('/api/workflows');
        this.workflowNames = response.data.map(workflow => ({
          workflow_name: workflow.workflow_name,
          id: workflow.id
        }));
        console.log("Workflow Names:", this.workflowNames);
      } catch (error) {
        console.error(error);
      }
    },
    async submitForm() {
      if (this.$refs.form.validate()) {
        const selectedWorkflow = this.workflowNames.find(
          option => option.workflow_name === this.autocompleteValuee
        );

        if (selectedWorkflow) {
          console.log("Getting payload data...")
          this.payload = this.patterns.flatMap(pattern => 
            pattern.fields.map(field => ({
              workflowId: selectedWorkflow.id,
              patternName: pattern.name,
              keyname: field.keyName,
              layout: field.layout,
              types: field.type,
            }))
          );
          try {
            console.log("payload is", this.payload)
            await axios.post('/api/volumematrix', this.payload);
            alert('Data submitted successfully!');
            this.fetchWorkflowNames();
          } catch (error) {
            console.error('Error submitting data:', error);
          }
        }
      }
    }
  },
};
</script>

<style scoped>
.v-card-title {
  background-color: #f5f5f5;
}

/* Adjusted styles to reduce spacing */
.mb-2 {
  margin-bottom: 0.5rem;
}

.mt-2 {
  margin-top: 0.5rem;
}

.ml-2 {
  margin-left: 0.5rem;
}

.button-row {
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
}
</style>

















.pattern-container {
  margin-bottom: 10px;
}

.field-set {
  margin-bottom: 5px;
}

.field-set .field {
  margin-bottom: 5px;
}

button {
  margin-top: 5px;
  margin-bottom: 5px;
}






<template>
  <!-- Keep the template as it was in the previous version -->
</template>

<script>
import axios from '../axios';

export default {
  data() {
    return {
      patterns: [
        {
          id: 1,
          name: 'Pattern1',
          fields: [{ keyName: '', type: '', layout: '' }]
        }
      ],
      nextPatternId: 2,
      types: ['Field', 'Button'],
      layouts: ['Horizontal', 'Vertical'],
      autocompleteValuee: "",
      valid: false,
      workflowNames: [],
      payload: null
    };
  },
  created() {
    this.fetchWorkflowNames();
  },
  methods: {
    addPattern() {
      this.patterns.push({
        id: this.nextPatternId,
        name: `Pattern${this.nextPatternId}`,
        fields: [{ keyName: '', type: '', layout: '' }]
      });
      this.nextPatternId++;
    },
    removePattern(patternIndex) {
      this.patterns.splice(patternIndex, 1);
      this.updatePatternNames();
    },
    updatePatternNames() {
      this.patterns.forEach((pattern, index) => {
        pattern.name = `Pattern${index + 1}`;
      });
      this.nextPatternId = this.patterns.length + 1;
    },
    addFieldSet(patternIndex) {
      this.patterns[patternIndex].fields.push({ keyName: '', type: '', layout: '' });
    },
    removeFieldSet(patternIndex, fieldIndex) {
      if (this.patterns[patternIndex].fields.length > 1) {
        this.patterns[patternIndex].fields.splice(fieldIndex, 1);
      }
    },
    async fetchWorkflowNames() {
      try {
        const response = await axios.get('/api/workflows');
        this.workflowNames = response.data.map(workflow => ({
          workflow_name: workflow.workflow_name,
          id: workflow.id
        }));
        console.log("Workflow Names:", this.workflowNames);
      } catch (error) {
        console.error(error);
      }
    },
    async submitForm() {
      if (this.$refs.form.validate()) {
        const selectedWorkflow = this.workflowNames.find(
          option => option.workflow_name === this.autocompleteValuee
        );

        if (selectedWorkflow) {
          console.log("Getting payload data...")
          this.payload = this.patterns.flatMap(pattern => 
            pattern.fields.map(field => ({
              workflowId: selectedWorkflow.id,
              patternName: pattern.name,
              keyname: field.keyName,
              layout: field.layout,
              types: field.type,
            }))
          );
          try {
            console.log("payload is", this.payload)
            await axios.post('/api/volumematrix', this.payload);
            alert('Data submitted successfully!');
            this.fetchWorkflowNames();
          } catch (error) {
            console.error('Error submitting data:', error);
          }
        }
      }
    }
  },
};
</script>

<style scoped>
.v-card-title {
  background-color: #f5f5f5;
}
</style>









<template>
  <v-container>
    <v-form ref="form" @submit.prevent="submitForm" v-model="valid">
      <v-row>
        <v-col cols="8">
          <v-autocomplete
            v-model="autocompleteValuee"
            :items="workflowNames.map(workflow => workflow.workflow_name)"
            label="Please specify the workflow name"
            placeholder="Type"
            prepend-icon="mdi-database-arrow-up"
            solo
            :rules="[v => !!v || 'Workflowname is required']"
          >
            <template v-slot:prepend>
              <span style="margin-right:10px; font-family: 'Gill Sans'; font-weight: bold;">Workflow Name</span>
            </template>
          </v-autocomplete>
        </v-col>
      </v-row>

      <!-- Patterns -->
      <v-row>
        <v-col v-for="(pattern, patternIndex) in patterns" :key="patternIndex" cols="12" md="6">
          <v-card class="mb-4" elevation="2">
            <v-card-title class="d-flex align-center">
              <v-icon left color="primary">mdi-shape-outline</v-icon>
              {{ pattern.name }}
              <v-btn icon small class="ml-2" @click="removePattern(patternIndex)" color="error">
                <v-icon small>mdi-close</v-icon>
              </v-btn>
            </v-card-title>
            <v-divider></v-divider>
            <v-card-text>
              <!-- Field headers -->
              <v-row class="mb-2">
                <v-col cols="4">
                  <strong class="text-subtitle-2">Volume Key</strong>
                </v-col>
                <v-col cols="4">
                  <strong class="text-subtitle-2">Type</strong>
                </v-col>
                <v-col cols="4">
                  <strong class="text-subtitle-2">Layout</strong>
                </v-col>
              </v-row>

              <!-- Fields -->
              <v-row v-for="(field, fieldIndex) in pattern.fields" :key="fieldIndex" class="mb-2">
                <v-col cols="4">
                  <v-text-field v-model="field.keyName" label="Key value" dense outlined></v-text-field>
                </v-col>
                <v-col cols="4">
                  <v-select v-model="field.type" :items="types" label="Label" dense outlined></v-select>
                </v-col>
                <v-col cols="4">
                  <v-select v-model="field.layout" :items="layouts" label="Layout" dense outlined></v-select>
                </v-col>
              </v-row>

              <v-row class="mt-2">
                <v-col cols="6">
                  <v-btn @click="addFieldSet(patternIndex)" small color="primary" outlined>
                    <v-icon left small>mdi-plus</v-icon> Add Field
                  </v-btn>
                </v-col>
                <v-col cols="6">
                  <v-btn @click="removeFieldSet(patternIndex, pattern.fields.length - 1)" small color="error" outlined>
                    <v-icon left small>mdi-minus</v-icon> Remove Field
                  </v-btn>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <v-row>
        <v-col>
          <v-btn @click="addPattern" color="primary">
            <v-icon left>mdi-plus</v-icon> Add Pattern
          </v-btn>
        </v-col>
      </v-row>

      <v-btn type="submit" color="success" :disabled="!valid" class="mt-4">Save</v-btn>
    </v-form>
  </v-container>
</template>

<script>
// ... (keep the script section as it was in the previous version)
</script>

<style scoped>
.v-card-title {
  background-color: #f5f5f5;
}
</style>














<template>
  <v-container>
    <v-form ref="form" @submit.prevent="submitForm" v-model="valid">
      <v-row>
        <v-col cols="8">
          <v-autocomplete
            v-model="autocompleteValuee"
            :items="workflowNames.map(workflow => workflow.workflow_name)"
            label="Please specify the workflow name"
            placeholder="Type"
            prepend-icon="mdi-database-arrow-up"
            solo
            :rules="[v => !!v || 'Workflowname is required']"
          >
            <template v-slot:prepend>
              <span style="margin-right:10px; font-family: 'Gill Sans'; font-weight: bold;">Workflow Name</span>
            </template>
          </v-autocomplete>
        </v-col>
      </v-row>

      <!-- Patterns -->
      <v-row>
        <v-col v-for="(pattern, patternIndex) in patterns" :key="patternIndex" cols="12" md="6" lg="4">
          <v-card class="mb-4">
            <v-card-title>
              {{ pattern.name }}
              <v-spacer></v-spacer>
              <v-btn icon @click="removePattern(patternIndex)" color="error">
                <v-icon>mdi-minus</v-icon>
              </v-btn>
            </v-card-title>
            <v-card-text>
              <!-- Field headers -->
              <v-row>
                <v-col cols="4">
                  <strong style="font-family: 'Gill Sans'; font-weight: bold;">Volume Key</strong>
                </v-col>
                <v-col cols="4">
                  <strong style="font-family: 'Gill Sans'; font-weight: bold;">Type</strong>
                </v-col>
                <v-col cols="4">
                  <strong style="font-family: 'Gill Sans'; font-weight: bold;">Layout</strong>
                </v-col>
              </v-row>

              <!-- Fields -->
              <v-row v-for="(field, fieldIndex) in pattern.fields" :key="fieldIndex" class="align-center">
                <v-col cols="4">
                  <v-text-field v-model="field.keyName" label="Key value"></v-text-field>
                </v-col>
                <v-col cols="4">
                  <v-select v-model="field.type" :items="types" label="Label"></v-select>
                </v-col>
                <v-col cols="4">
                  <v-select v-model="field.layout" :items="layouts" label="Layout"></v-select>
                </v-col>
              </v-row>

              <v-row>
                <v-col cols="6">
                  <v-btn @click="addFieldSet(patternIndex)" small>
                    <v-icon left>mdi-plus</v-icon> Add Field
                  </v-btn>
                </v-col>
                <v-col cols="6">
                  <v-btn @click="removeFieldSet(patternIndex, pattern.fields.length - 1)" small>
                    <v-icon left>mdi-minus</v-icon> Remove Field
                  </v-btn>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <v-row>
        <v-col>
          <v-btn @click="addPattern" color="primary">
            <v-icon left>mdi-plus</v-icon> Add Pattern
          </v-btn>
        </v-col>
      </v-row>

      <v-btn type="submit" color="success" :disabled="!valid" class="mt-4">Save</v-btn>
    </v-form>
  </v-container>
</template>

<script>
import axios from '../axios';

export default {
  data() {
    return {
      patterns: [
        {
          name: 'Pattern1',
          fields: [{ keyName: '', type: '', layout: '' }]
        }
      ],
      types: ['Field', 'Button'],
      layouts: ['Horizontal', 'Vertical'],
      autocompleteValuee: "",
      valid: false,
      workflowNames: [],
      payload: null
    };
  },
  created() {
    this.fetchWorkflowNames();
  },
  methods: {
    addPattern() {
      const newPatternNumber = this.patterns.length + 1;
      this.patterns.push({
        name: `Pattern${newPatternNumber}`,
        fields: [{ keyName: '', type: '', layout: '' }]
      });
    },
    removePattern(patternIndex) {
      this.patterns.splice(patternIndex, 1);
    },
    addFieldSet(patternIndex) {
      this.patterns[patternIndex].fields.push({ keyName: '', type: '', layout: '' });
    },
    removeFieldSet(patternIndex, fieldIndex) {
      if (this.patterns[patternIndex].fields.length > 1) {
        this.patterns[patternIndex].fields.splice(fieldIndex, 1);
      }
    },
    async fetchWorkflowNames() {
      try {
        const response = await axios.get('/api/workflows');
        this.workflowNames = response.data.map(workflow => ({
          workflow_name: workflow.workflow_name,
          id: workflow.id
        }));
        console.log("Workflow Names:", this.workflowNames);
      } catch (error) {
        console.error(error);
      }
    },
    async submitForm() {
      if (this.$refs.form.validate()) {
        const selectedWorkflow = this.workflowNames.find(
          option => option.workflow_name === this.autocompleteValuee
        );

        if (selectedWorkflow) {
          console.log("Getting payload data...")
          this.payload = this.patterns.flatMap(pattern => 
            pattern.fields.map(field => ({
              workflowId: selectedWorkflow.id,
              patternName: pattern.name,
              keyname: field.keyName,
              layout: field.layout,
              types: field.type,
            }))
          );
          try {
            console.log("payload is", this.payload)
            await axios.post('/api/volumematrix', this.payload);
            alert('Data submitted successfully!');
            this.fetchWorkflowNames();
          } catch (error) {
            console.error('Error submitting data:', error);
          }
        }
      }
    }
  },
};
</script>

<style scoped>
.align-center {
  display: flex;
  align-items: center;
}
</style>





-----------------------------------
<template>
  <v-container>
    <v-form ref="form" @submit.prevent="submitForm" v-model="valid">
      <v-row>
        <v-col cols="8">
          <v-autocomplete
            v-model="selectedWorkflow"
            :items="workflowNames"
            label="Please specify the workflow name"
            placeholder="Type"
            prepend-icon="mdi-database-arrow-up"
            solo
            :rules="[v => !!v || 'Workflow name is required']"
          >
            <template #prepend>
              <span class="mr-2 font-weight-bold">Workflow Name</span>
            </template>
          </v-autocomplete>
        </v-col>
      </v-row>

      <v-row>
        <v-col v-for="(pattern, patternIndex) in patterns" :key="patternIndex" cols="12" md="6" lg="4">
          <v-card>
            <v-card-title>
              {{ pattern.name }}
              <v-spacer></v-spacer>
              <v-btn icon @click="removePattern(patternIndex)">
                <v-icon>mdi-minus</v-icon>
              </v-btn>
            </v-card-title>
            <v-card-text>
              <v-row>
                <v-col cols="4">
                  <strong>Volume Key</strong>
                </v-col>
                <v-col cols="4">
                  <strong>Type</strong>
                </v-col>
                <v-col cols="4">
                  <strong>Layout</strong>
                </v-col>
              </v-row>

              <v-row v-for="(field, fieldIndex) in pattern.fields" :key="fieldIndex" class="align-center">
                <v-col cols="4">
                  <v-text-field v-model="field.keyName" label="Key value" dense></v-text-field>
                </v-col>
                <v-col cols="4">
                  <v-select v-model="field.type" :items="types" label="Label" dense></v-select>
                </v-col>
                <v-col cols="4">
                  <v-select v-model="field.layout" :items="layouts" label="Layout" dense></v-select>
                </v-col>
              </v-row>

              <v-row>
                <v-col cols="6">
                  <v-btn @click="addFieldSet(patternIndex)" small>
                    <v-icon left>mdi-plus</v-icon> Add Field
                  </v-btn>
                </v-col>
                <v-col cols="6">
                  <v-btn @click="removeFieldSet(patternIndex)" small>
                    <v-icon left>mdi-minus</v-icon> Remove Field
                  </v-btn>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <v-row class="mt-4">
        <v-col>
          <v-btn @click="addPattern" color="secondary">
            <v-icon left>mdi-plus</v-icon> Add Pattern
          </v-btn>
        </v-col>
      </v-row>
    </v-form>

    <v-footer app fixed class="d-flex justify-center">
      <v-btn type="submit" color="primary" :disabled="!valid" @click="submitForm" large>Save</v-btn>
    </v-footer>
  </v-container>
</template>

<script>
import axios from '../axios';

export default {
  data() {
    return {
      patterns: [
        {
          name: 'Pattern1',
          fields: [{ keyName: '', type: '', layout: '' }]
        }
      ],
      types: ['Field', 'Button'],
      layouts: ['Horizontal', 'Vertical'],
      selectedWorkflow: "",
      valid: false,
      workflowNames: [],
      payload: null
    };
  },
  created() {
    this.fetchWorkflowNames();
  },
  methods: {
    addPattern() {
      const newPatternNumber = this.patterns.length + 1;
      this.patterns.push({
        name: `Pattern${newPatternNumber}`,
        fields: [{ keyName: '', type: '', layout: '' }]
      });
    },
    removePattern(patternIndex) {
      this.patterns.splice(patternIndex, 1);
    },
    addFieldSet(patternIndex) {
      this.patterns[patternIndex].fields.push({ keyName: '', type: '', layout: '' });
    },
    removeFieldSet(patternIndex) {
      if (this.patterns[patternIndex].fields.length > 1) {
        this.patterns[patternIndex].fields.pop();
      }
    },
    async fetchWorkflowNames() {
      try {
        const response = await axios.get('/api/workflows');
        this.workflowNames = response.data.map(workflow => ({
          text: workflow.workflow_name,
          value: workflow.id
        }));
      } catch (error) {
        console.error('Error fetching workflow names:', error);
      }
    },
    async submitForm() {
      if (this.$refs.form.validate()) {
        this.payload = this.patterns.flatMap(pattern => 
          pattern.fields.map(field => ({
            workflowId: this.selectedWorkflow,
            patternName: pattern.name,
            keyname: field.keyName,
            layout: field.layout,
            types: field.type,
          }))
        );
        try {
          await axios.post('/api/volumematrix', this.payload);
          alert('Data submitted successfully!');
          this.fetchWorkflowNames();
        } catch (error) {
          console.error('Error submitting data:', error);
        }
      }
    }
  },
};
</script>

<style scoped>
.align-center {
  display: flex;
  align-items: center;
}
</style>











<template>
  <v-card>
    <v-toolbar color="black">
      <v-toolbar-title class="title-bold-stylish">Pulse Configurator</v-toolbar-title>
      <template #prepend>
        <img src="../assets/logo.png" alt="Logo" />
      </template>
    </v-toolbar>

    <v-tabs v-model="activeTab" align-tabs="title" class="tab-bold-stylish">
      <v-tab v-for="(item, index) in items" :key="item" :value="index">
        {{ item }}
      </v-tab>
    </v-tabs>

    <v-container>
      <v-row>
        <v-col>
          <v-btn @click="openStore" class="store-bold-stylish">
            {{ storeButtonText }}
            <v-icon end color="success">mdi-arch</v-icon>
          </v-btn>
        </v-col>
        <v-col>
          <v-btn class="excel-bold-stylish">
            Excel Upload
            <v-icon end color="red">mdi-file-upload</v-icon>
          </v-btn>
        </v-col>
      </v-row>
    </v-container>

    <v-tabs-items v-model="activeTab">
      <v-tab-item :value="0">
        <WorkflowConfigurator v-if="activeTab === 0"/>
      </v-tab-item>
      <v-tab-item :value="1">
        <KeynameMapping v-if="activeTab === 1"/>
      </v-tab-item>
      <v-tab-item :value="2">
        <VolumeMatrix v-if="activeTab === 2"/>
      </v-tab-item>
    </v-tabs-items>

    <component :is="storeComponent" v-model:dialogVisible="storeDialogVisible"/>
  </v-card>
</template>

<script>
import KeynameMapping from './KeynameMapping.vue';
import AppStore from './AppStore.vue';
import WorkflowConfigurator from './WorkflowConfigurator.vue';
import KeyStore from './KeyStore.vue';
import VolumeMatrix from './VolumeMatrix.vue';
import VolumeStore from './VolumeStore.vue';

export default {
  components: {
    WorkflowConfigurator,
    AppStore,
    KeynameMapping,
    KeyStore,
    VolumeStore,
    VolumeMatrix,
  },
  data() {
    return {
      items: ['Workflow Master', 'Keyname Mapping', 'Volume Matrix'],
      activeTab: 0,
      storeDialogVisible: false,
    };
  },
  computed: {
    storeButtonText() {
      const texts = ['Go To AppStore', 'Go To KeyStore', 'Go To VolumeStore'];
      return texts[this.activeTab];
    },
    storeComponent() {
      const components = ['AppStore', 'KeyStore', 'VolumeStore'];
      return components[this.activeTab];
    },
  },
  methods: {
    openStore() {
      this.storeDialogVisible = true;
    },
  },
};
</script>

<style scoped>
.title-bold-stylish {
  font-weight: bold;
  font-family: 'Garamond', sans-serif;
  font-size: 28px;
  color: lavenderblush;
}
.tab-bold-stylish {
  font-weight: bold;
  font-family: 'Garamond', sans-serif;
  font-size: 28px;
  color: lavenderblush;
}
.store-bold-stylish, .excel-bold-stylish {
  font-weight: bold;
  font-family: 'Garamond', sans-serif;
  font-size: 14px;
  color: snow;
}
</style>












<template>
  <v-container>
    <v-form ref="form" @submit.prevent="submitForm" v-model="valid">
      <v-row>
        <v-col cols="8">
          <v-autocomplete
            v-model="autocompleteValuee"
            :items="workflowNames.map(workflow => workflow.workflow_name)"
            label="Please specify the workflow name"
            placeholder="Type"
            prepend-icon="mdi-database-arrow-up"
            solo
            :rules="[v => !!v || 'Workflowname is required']"
          >
            <template v-slot:prepend>
              <span style="margin-right:10px; font-family: 'Gill Sans'; font-weight: bold;">Workflow Name</span>
            </template>
          </v-autocomplete>
        </v-col>
      </v-row>

      <!-- Patterns -->
      <v-row>
        <v-col v-for="(pattern, patternIndex) in patterns" :key="patternIndex" cols="12" md="6" lg="4">
          <v-card>
            <v-card-title>
              {{ pattern.name }}
              <v-spacer></v-spacer>
              <v-btn icon @click="removePattern(patternIndex)">
                <v-icon>mdi-minus</v-icon>
              </v-btn>
            </v-card-title>
            <v-card-text>
              <!-- Field headers -->
              <v-row>
                <v-col cols="4">
                  <strong style="font-family: 'Gill Sans'; font-weight: bold;">Volume Key</strong>
                </v-col>
                <v-col cols="4">
                  <strong style="font-family: 'Gill Sans'; font-weight: bold;">Type</strong>
                </v-col>
                <v-col cols="4">
                  <strong style="font-family: 'Gill Sans'; font-weight: bold;">Layout</strong>
                </v-col>
              </v-row>

              <!-- Fields -->
              <v-row v-for="(field, fieldIndex) in pattern.fields" :key="fieldIndex" class="align-center">
                <v-col cols="4">
                  <v-text-field v-model="field.keyName" label="Key value" dense></v-text-field>
                </v-col>
                <v-col cols="4">
                  <v-select v-model="field.type" :items="types" label="Label" dense></v-select>
                </v-col>
                <v-col cols="4">
                  <v-select v-model="field.layout" :items="layouts" label="Layout" dense></v-select>
                </v-col>
              </v-row>

              <v-row>
                <v-col cols="6">
                  <v-btn @click="addFieldSet(patternIndex)" small>
                    <v-icon left>mdi-plus</v-icon> Add Field
                  </v-btn>
                </v-col>
                <v-col cols="6">
                  <v-btn @click="removeFieldSet(patternIndex)" small>
                    <v-icon left>mdi-minus</v-icon> Remove Field
                  </v-btn>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <v-row class="mt-4">
        <v-col>
          <v-btn @click="addPattern" color="secondary">
            <v-icon left>mdi-plus</v-icon> Add Pattern
          </v-btn>
        </v-col>
      </v-row>
    </v-form>

    <!-- Fixed bottom save button -->
    <v-footer app fixed class="d-flex justify-center">
      <v-btn type="submit" color="primary" :disabled="!valid" @click="submitForm" large>Save</v-btn>
    </v-footer>
  </v-container>
</template>

<script>
import axios from '../axios';

export default {
  data() {
    return {
      patterns: [
        {
          name: 'Pattern1',
          fields: [{ keyName: '', type: '', layout: '' }]
        }
      ],
      types: ['Field', 'Button'],
      layouts: ['Horizontal', 'Vertical'],
      autocompleteValuee: "",
      valid: false,
      workflowNames: [],
      payload: null
    };
  },
  created() {
    this.fetchWorkflowNames();
  },
  methods: {
    addPattern() {
      const newPatternNumber = this.patterns.length + 1;
      this.patterns.push({
        name: `Pattern${newPatternNumber}`,
        fields: [{ keyName: '', type: '', layout: '' }]
      });
    },
    removePattern(patternIndex) {
      this.patterns.splice(patternIndex, 1);
    },
    addFieldSet(patternIndex) {
      this.patterns[patternIndex].fields.push({ keyName: '', type: '', layout: '' });
    },
    removeFieldSet(patternIndex) {
      if (this.patterns[patternIndex].fields.length > 1) {
        this.patterns[patternIndex].fields.pop();
      }
    },
    async fetchWorkflowNames() {
      try {
        const response = await axios.get('/api/workflows');
        this.workflowNames = response.data.map(workflow => ({
          workflow_name: workflow.workflow_name,
          id: workflow.id
        }));
        console.log("Workflow Names:", this.workflowNames);
      } catch (error) {
        console.error(error);
      }
    },
    async submitForm() {
      if (this.$refs.form.validate()) {
        const selectedWorkflow = this.workflowNames.find(
          option => option.workflow_name === this.autocompleteValuee
        );

        if (selectedWorkflow) {
          console.log("Getting payload data...")
          this.payload = this.patterns.flatMap(pattern => 
            pattern.fields.map(field => ({
              workflowId: selectedWorkflow.id,
              patternName: pattern.name,
              keyname: field.keyName,
              layout: field.layout,
              types: field.type,
            }))
          );
          try {
            console.log("payload is", this.payload)
            await axios.post('/api/volumematrix', this.payload);
            alert('Data submitted successfully!');
            this.fetchWorkflowNames();
          } catch (error) {
            console.error('Error submitting data:', error);
          }
        }
      }
    }
  },
};
</script>

<style scoped>
.align-center {
  display: flex;
  align-items: center;
}
</style>













-------------------------------------------------------------------------------------------------------------

<template>
  <v-container>
    <v-card flat>
      <v-card-text>
        <v-form ref="form" @submit.prevent="submitForm" v-model="valid">
          <v-row>
            <v-col cols="8">
              <v-autocomplete
                v-model="autocompleteValuee"
                :items="workflowNames.map(workflow => workflow.workflow_name)"
                label="Please specify the workflow name"
                placeholder="Type"
                prepend-icon="mdi-database-arrow-up"
                solo
                :rules="[v => !!v || 'Workflowname is required']"
              >
                <template v-slot:prepend>
                  <span style="margin-right:10px; font-family: 'Gill Sans'; font-weight: bold;">Workflow Name</span>
                </template>
              </v-autocomplete>
            </v-col>
          </v-row>

          <!-- Patterns -->
          <div v-for="(pattern, patternIndex) in patterns" :key="patternIndex">
            <v-row align="center">
              <v-col cols="11">
                <h3>{{ pattern.name }}</h3>
              </v-col>
              <v-col cols="1">
                <v-btn icon @click="addPattern" v-if="patternIndex === patterns.length - 1">
                  <v-icon>mdi-plus</v-icon>
                </v-btn>
              </v-col>
            </v-row>

            <!-- Field headers -->
            <v-row>
              <v-col cols="3">
                <strong style="margin-right:10px; font-family: 'Gill Sans'; font-weight: bold;">Volume Key</strong>
              </v-col>
              <v-col cols="3">
                <strong style="margin-right:10px; font-family: 'Gill Sans'; font-weight: bold;">Type</strong>
              </v-col>
              <v-col cols="3">
                <strong style="margin-right:10px; font-family: 'Gill Sans'; font-weight: bold;">Layout</strong>
              </v-col>
            </v-row>

            <!-- Fields -->
            <v-row v-for="(field, fieldIndex) in pattern.fields" :key="fieldIndex" class="align-center">
              <v-col cols="3">
                <v-text-field v-model="field.keyName" label="Key value"></v-text-field>
              </v-col>
              <v-col cols="3">
                <v-select v-model="field.type" :items="types" label="Label"></v-select>
              </v-col>
              <v-col cols="3">
                <v-select v-model="field.layout" :items="layouts" label="Layout"></v-select>
              </v-col>  
              <v-col cols="1.5">
                <v-btn @click="addFieldSet(patternIndex)" icon>
                  <v-icon>mdi-plus</v-icon>
                </v-btn>
              </v-col>
              <v-col cols="1.5">
                <v-btn @click="removeFieldSet(patternIndex, fieldIndex)" icon>
                  <v-icon>mdi-minus</v-icon>
                </v-btn>
              </v-col>
            </v-row>
          </div>

          <v-btn type="submit" color="primary" :disabled="!valid" class="mt-4">Save</v-btn>
        </v-form>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script>
import axios from '../axios';

export default {
  data() {
    return {
      patterns: [
        {
          name: 'Pattern1',
          fields: [{ keyName: '', type: '', layout: '' }]
        }
      ],
      types: ['Field', 'Button'],
      layouts: ['Horizontal', 'Vertical'],
      autocompleteValuee: "",
      valid: false,
      workflowNames: [],
      payload: null
    };
  },
  created() {
    this.fetchWorkflowNames();
  },
  methods: {
    addPattern() {
      const newPatternNumber = this.patterns.length + 1;
      this.patterns.push({
        name: `Pattern${newPatternNumber}`,
        fields: [{ keyName: '', type: '', layout: '' }]
      });
    },
    addFieldSet(patternIndex) {
      this.patterns[patternIndex].fields.push({ keyName: '', type: '', layout: '' });
    },
    removeFieldSet(patternIndex, fieldIndex) {
      if (this.patterns[patternIndex].fields.length > 1) {
        this.patterns[patternIndex].fields.splice(fieldIndex, 1);
      }
    },
    async fetchWorkflowNames() {
      try {
        const response = await axios.get('/api/workflows');
        this.workflowNames = response.data.map(workflow => ({
          workflow_name: workflow.workflow_name,
          id: workflow.id
        }));
        console.log("Workflow Names:", this.workflowNames);
      } catch (error) {
        console.error(error);
      }
    },
    async submitForm() {
      if (this.$refs.form.validate()) {
        const selectedWorkflow = this.workflowNames.find(
          option => option.workflow_name === this.autocompleteValuee
        );

        if (selectedWorkflow) {
          console.log("Getting payload data...")
          this.payload = this.patterns.flatMap(pattern => 
            pattern.fields.map(field => ({
              workflowId: selectedWorkflow.id,
              patternName: pattern.name,
              keyname: field.keyName,
              layout: field.layout,
              types: field.type,
            }))
          );
          try {
            console.log("payload is", this.payload)
            await axios.post('/api/volumematrix', this.payload);
            alert('Data submitted successfully!');
            this.fetchWorkflowNames();
          } catch (error) {
            console.error('Error submitting data:', error);
          }
        }
      }
    }
  },
};
</script>

<style scoped>
.align-center {
  display: flex;
  align-items: center;
}

.headline {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 20px;
}

.subtitle-1 {
  font-size: 18px;
  font-weight: bold;
}

.body-2 {
  font-size: 14px;
  font-weight: bold;
}
</style>































---------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------------


pip install SQLAlchemy
pip install python-dotenv
pip install Flask-JWT-Extended
pip install Flask-Cors
pip install Flask
pip install Flask-RESTful



// src/eventBus.js

class EventBus {
  constructor() {
    this.events = {};
  }

  $on(eventName, fn) {
    this.events[eventName] = this.events[eventName] || [];
    this.events[eventName].push(fn);
  }

  $off(eventName, fn) {
    if (this.events[eventName]) {
      for (let i = 0; i < this.events[eventName].length; i++) {
        if (this.events[eventName][i] === fn) {
          this.events[eventName].splice(i, 1);
          break;
        }
      }
    }
  }

  $emit(eventName, data) {
    if (this.events[eventName]) {
      this.events[eventName].forEach(function(fn) {
        fn(data);
      });
    }
  }
}

export default new EventBus();
import EventBus from '../eventBus';

// ... other code ...

methods: {
  async submitForm(){
    const isFormValid = this.$refs.form.validate();
    if (isFormValid){
      try {
        console.log("New Workflow Data",this.form)
        await axios.post('/api/whitelists/',this.form);
        alert('Form submitted successfully');
        this.resetForm();
        // Emit an event to notify that a new workflow has been added
        EventBus.$emit('workflow-added');
      } catch (error) {
        console.error(error);
      }
    }
  },
  // ... other methods ...
}



To define your database table using SQLAlchemy (without Flask-SQLAlchemy), you need to create a model that represents your table structure. Below is an example of how to define the table with the specified columns and constraints:

```python
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class KeyNameMapping(Base):
    __tablename__ = 'key_name_mapping'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    workflow_id = Column(Integer, nullable=False)
    pattern = Column(String(50), nullable=True)
    activity_key_name = Column(String(1000), nullable=True)
    activity_key_type = Column(String(1000), nullable=True)
    activity_key_layout = Column(String(500), nullable=True)
    interactive_bit = Column(Integer, nullable=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=True)
    created_by = Column(String(50), nullable=True)
    modified_date = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=True)
    modified_by = Column(String(50), nullable=True)

    def __init__(self, workflow_id, pattern=None, activity_key_name=None, activity_key_type=None, activity_key_layout=None, interactive_bit=None, created_by=None, modified_by=None):
        self.workflow_id = workflow_id
        self.pattern = pattern
        self.activity_key_name = activity_key_name
        self.activity_key_type = activity_key_type
        self.activity_key_layout = activity_key_layout
        self.interactive_bit = interactive_bit
        self.created_by = created_by
        self.modified_by = modified_by

# Example of creating the engine and creating the tables in the database
engine = create_engine('sqlite:///your_database.db')  # Update with your database URL
Base.metadata.create_all(engine)
```

### Explanation:

1. **Class Definition**: The class `KeyNameMapping` represents the table `key_name_mapping`.
2. **Columns**: Each class attribute corresponds to a column in the table. For example, `id`, `workflow_id`, `pattern`, etc.
   - `Column(Integer, primary_key=True, autoincrement=True)` indicates that `id` is the primary key and it auto-increments.
   - `Column(String(50), nullable=True)` indicates a column with a `String` type of length 50 and it allows null values.
   - `Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=True)` indicates a `DateTime` column with a default value of the current UTC time and it updates to the current UTC time whenever the record is updated.
3. **Constructor**: The `__init__` method is defined to initialize the object with the specified parameters.
4. **Engine and Table Creation**: The `create_engine` function creates a new engine instance connected to your database, and `Base.metadata.create_all(engine)` creates the table in the database based on the defined models.

Replace `'sqlite:///your_database.db'` with the appropriate database URL for your setup.

You can extend this base model to include relationships, additional constraints, or methods as needed for your application's requirements.




[17/07, 09:54] Pavan Bhargav Reddy: To achieve this, you can structure your Flask backend with SQLAlchemy (without Flask-SQLAlchemy) and use Flask-RESTful for handling RESTful routes. Here’s how you can set up your project:

### Project Structure
```
my_flask_app/
│
├── app.py
├── models.py
├── resources/
│   ├── __init__.py
│   ├── keyname_mapping.py
├── db.py
└── config.py
```

### `config.py`
```python
class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///keyname_mapping.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

### `db.py`
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import Config

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

### `models.py`
```python
from sqlalchemy import Column, Integer, String
from db import Base, engine

class KeyNameMapping(Base):
    __tablename__ = 'key_name_mapping'
    id = Column(Integer, primary_key=True, index=True)
    workflow_name = Column(String, nullable=False)
    key_name = Column(String, nullable=False)
    layout = Column(String, nullable=False)
    remarks = Column(String, nullable=False)

# Create tables
Base.metadata.create_all(bind=engine)
```

### `resources/keyname_mapping.py`
```python
from flask_restful import Resource, reqparse
from models import KeyNameMapping
from db import SessionLocal

parser = reqparse.RequestParser()
parser.add_argument('workflowName', type=str, required=True, help="Workflow Name is required")
parser.add_argument('keyName', type=str, required=True, help="Key Name is required")
parser.add_argument('layout', type=str, required=True, help="Layout is required")
parser.add_argument('remarks', type=str, required=True, help="Remarks is required")

class KeyNameMappingResource(Resource):
    def get(self):
        session = SessionLocal()
        mappings = session.query(KeyNameMapping).all()
        session.close()
        return [{'id': mapping.id, 'workflow_name': mapping.workflow_name, 'key_name': mapping.key_name, 'layout': mapping.layout, 'remarks': mapping.remarks} for mapping in mappings], 200

    def post(self):
        args = parser.parse_args()
        session = SessionLocal()
        new_mapping = KeyNameMapping(
            workflow_name=args['workflowName'],
            key_name=args['keyName'],
            layout=args['layout'],
            remarks=args['remarks']
        )
        session.add(new_mapping)
        session.commit()
        session.refresh(new_mapping)
        session.close()
        return {'id': new_mapping.id, 'workflow_name': new_mapping.workflow_name, 'key_name': new_mapping.key_name, 'layout': new_mapping.layout, 'remarks': new_mapping.remarks}, 201

    def put(self, id):
        args = parser.parse_args()
        session = SessionLocal()
        mapping = session.query(KeyNameMapping).filter(KeyNameMapping.id == id).first()
        if mapping:
            mapping.workflow_name = args['workflowName']
            mapping.key_name = args['keyName']
            mapping.layout = args['layout']
            mapping.remarks = args['remarks']
            session.commit()
            session.refresh(mapping)
            session.close()
            return {'id': mapping.id, 'workflow_name': mapping.workflow_name, 'key_name': mapping.key_name, 'layout': mapping.layout, 'remarks': mapping.remarks}, 200
        else:
            session.close()
            return {'message': 'Mapping not found'}, 404

    def delete(self, id):
        session = SessionLocal()
        mapping = session.query(KeyNameMapping).filter(KeyNameMapping.id == id).first()
        if mapping:
            session.delete(mapping)
            session.commit()
            session.close()
            return {'message': 'Mapping deleted'}, 200
        else:
            session.close()
            return {'message': 'Mapping not found'}, 404
```

### `app.py`
```python
from flask import Flask
from flask_restful import Api
from resources.keyname_mapping import KeyNameMappingResource

app = Flask(__name__)
api = Api(app)

api.add_resource(KeyNameMappingResource, '/keyname_mapping', '/keyname_mapping/<int:id>')

if __name__ == '__main__':
    app.run(debug=True)
```

### Explanation

1. **`config.py`**: Contains the configuration for the database URI.
2. **`db.py`**: Sets up the SQLAlchemy engine, session, and base declarative class.
3. **`models.py`**: Defines the `KeyNameMapping` model and creates the database table.
4. **`resources/keyname_mapping.py`**: Contains the RESTful resource class for handling GET, POST, PUT, and DELETE requests for key name mappings.
5. **`app.py`**: Sets up the Flask application, initializes the RESTful API, and adds the resource routes.

### Testing

You can now start the Flask application and test the endpoints using tools like Postman or curl:

- **GET** `/keyname_mapping`: Retrieve all key name mappings.
- **POST** `/keyname_mapping`: Create a new key name mapping.
- **PUT** `/keyname_mapping/<id>`: Update an existing key name mapping.
- **DELETE** `/keyname_mapping/<id>`: Delete a key name mapping.

This setup provides a clean separation of concerns, with the database models, configuration, and resource handling in separate files.
[17/07, 09:55] Pavan Bhargav Reddy: <template>
  <v-container>
    <v-form ref="form" v-model="valid">
      <v-text-field v-model="workflowName" label="Workflow Name" required></v-text-field>
      
      <div v-for="(field, index) in fields" :key="index">
        <v-text-field v-model="field.keyName" label="Key Name" required></v-text-field>
        <v-text-field v-model="field.layout" label="Layout" required></v-text-field>
        <v-text-field v-model="field.remarks" label="Remarks" required></v-text-field>
        <v-btn @click="removeField(index)">Remove</v-btn>
      </div>

      <v-btn @click="addField">Add Field</v-btn>
      <v-btn @click="submit" :disabled="!valid">Submit</v-btn>
    </v-form>
  </v-container>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      valid: false,
      workflowName: '',
      fields: [
        { keyName: '', layout: '', remarks: '' }
      ]
    };
  },
  methods: {
    addField() {
      this.fields.push({ keyName: '', layout: '', remarks: '' });
    },
    removeField(index) {
      this.fields.splice(index, 1);
    },
    async submit() {
      if (this.$refs.form.validate()) {
        const payload = this.fields.map(field => ({
          workflowName: this.workflowName,
          keyName: field.keyName,
          layout: field.layout,
          remarks: field.remarks
        }));
        
        try {
          await axios.post('/api/submit', payload);
          alert('Data submitted successfully!');
        } catch (error) {
          console.error('Error submitting data:', error);
        }
      }
    }
  }
};
</script>
[17/07, 10:00] Pavan Bhargav Reddy: To address your requirement, the process involves fetching workflow names from the backend to populate the autocomplete field in the frontend. Once a workflow name is selected, the corresponding workflow ID is determined and sent to the backend with the key name, layout, and remark pairs. Here is how you can achieve this:

### Frontend

1. **Fetching Workflow Names**: Fetch workflow names to populate the autocomplete field.

```javascript
methods: {
  fetchWorkflowNames() {
    axios.get('/api/workflows')
      .then(response => {
        this.workflowOptions = response.data;
      })
      .catch(error => {
        console.error("There was an error fetching the workflow names!", error);
      });
  }
}
```

2. **Replacing Workflow Name with Workflow ID**: After selecting a workflow name, replace it with the corresponding workflow ID before sending the data to the backend.

```javascript
methods: {
  submitForm() {
    const selectedWorkflow = this.workflowOptions.find(
      option => option.name === this.form.workflowName
    );

    if (selectedWorkflow) {
      const formData = this.form.keyNameLayouts.map(entry => ({
        workflowId: selectedWorkflow.id,
        keyName: entry.keyName,
        layout: entry.layout,
        remarks: entry.remarks
      }));

      axios.post('/api/keyname-mapping', formData)
        .then(response => {
          console.log("Data submitted successfully", response);
        })
        .catch(error => {
          console.error("There was an error submitting the data!", error);
        });
    } else {
      console.error("Invalid workflow name selected");
    }
  }
}
```

### Backend

1. **SQLAlchemy Models**: Define the models for workflows and key name mapping.

```python
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from your_database_setup import Base, engine

class Workflow(Base):
    __tablename__ = 'workflows'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

class KeyNameMapping(Base):
    __tablename__ = 'key_name_mappings'
    id = Column(Integer, primary_key=True)
    workflow_id = Column(Integer, ForeignKey('workflows.id'), nullable=False)
    key_name = Column(String, nullable=False)
    layout = Column(String, nullable=False)
    remarks = Column(String, nullable=False)
    workflow = relationship('Workflow')
```

2. **REST API with Flask**: Handle GET and POST requests.

```python
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from your_database_setup import Session, Workflow, KeyNameMapping

app = Flask(__name__)
api = Api(app)
session = Session()

class WorkflowListResource(Resource):
    def get(self):
        workflows = session.query(Workflow).all()
        return jsonify([{"id": w.id, "name": w.name} for w in workflows])

class KeyNameMappingResource(Resource):
    def post(self):
        data = request.get_json()
        for item in data:
            new_entry = KeyNameMapping(
                workflow_id=item['workflowId'],
                key_name=item['keyName'],
                layout=item['layout'],
                remarks=item['remarks']
            )
            session.add(new_entry)
        session.commit()
        return {"message": "Key name mappings added successfully"}, 201

api.add_resource(WorkflowListResource, '/api/workflows')
api.add_resource(KeyNameMappingResource, '/api/keyname-mapping')

if __name__ == '__main__':
    app.run(debug=True)
```

This setup ensures that the workflow name is replaced with the workflow ID before the data is sent to the backend, where it is then stored correctly in the database.
[17/07, 10:03] Pavan Bhargav Reddy: To extend your current setup to include editing and deleting entries from the `KeyNameMapping` table, we need to implement additional frontend and backend functionality.

### Frontend

1. **Key Store Component**: Display key name mappings with edit and delete actions.

```vue
<template>
  <div>
    <v-data-table :headers="headers" :items="keyMappings" class="elevation-1">
      <template v-slot:item.actions="{ item }">
        <v-icon small @click="editItem(item)">mdi-pencil</v-icon>
        <v-icon small @click="deleteItem(item)">mdi-delete</v-icon>
      </template>
    </v-data-table>

    <!-- Edit Dialog -->
    <v-dialog v-model="editDialog" max-width="600px">
      <v-card>
        <v-card-title>
          <span class="headline">Edit Key Mapping</span>
        </v-card-title>
        <v-card-text>
          <v-container>
            <v-row>
              <v-col cols="12" sm="6" md="4">
                <v-text-field v-model="editedItem.keyName" label="Key Name"></v-text-field>
              </v-col>
              <v-col cols="12" sm="6" md="4">
                <v-text-field v-model="editedItem.layout" label="Layout"></v-text-field>
              </v-col>
              <v-col cols="12" sm="6" md="4">
                <v-text-field v-model="editedItem.remarks" label="Remarks"></v-text-field>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text @click="closeEdit">Cancel</v-btn>
          <v-btn color="blue darken-1" text @click="saveEdit">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
export default {
  data() {
    return {
      keyMappings: [],
      headers: [
        { text: 'Key Name', value: 'keyName' },
        { text: 'Layout', value: 'layout' },
        { text: 'Remarks', value: 'remarks' },
        { text: 'Actions', value: 'actions', sortable: false }
      ],
      editDialog: false,
      editedItem: {},
    };
  },
  methods: {
    fetchKeyMappings() {
      axios.get('/api/keyname-mapping')
        .then(response => {
          this.keyMappings = response.data;
        })
        .catch(error => {
          console.error("There was an error fetching the key mappings!", error);
        });
    },
    editItem(item) {
      this.editedItem = { ...item };
      this.editDialog = true;
    },
    saveEdit() {
      axios.put(`/api/keyname-mapping/${this.editedItem.id}`, this.editedItem)
        .then(response => {
          this.fetchKeyMappings();
          this.editDialog = false;
        })
        .catch(error => {
          console.error("There was an error saving the edit!", error);
        });
    },
    deleteItem(item) {
      axios.delete(`/api/keyname-mapping/${item.id}`)
        .then(response => {
          this.fetchKeyMappings();
        })
        .catch(error => {
          console.error("There was an error deleting the item!", error);
        });
    },
    closeEdit() {
      this.editDialog = false;
    }
  },
  mounted() {
    this.fetchKeyMappings();
  }
};
</script>
```

### Backend

1. **Add GET, PUT, DELETE methods**: Enhance your existing REST API to support fetching, updating, and deleting key name mappings.

```python
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Workflow, KeyNameMapping, Base

app = Flask(__name__)
api = Api(app)

# Database setup
engine = create_engine('sqlite:///your_database.db')  # Update with your database URL
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

class WorkflowListResource(Resource):
    def get(self):
        workflows = session.query(Workflow).all()
        return jsonify([{"id": w.id, "name": w.name} for w in workflows])

class KeyNameMappingResource(Resource):
    def get(self):
        key_name_mappings = session.query(KeyNameMapping).all()
        return jsonify([{
            "id": k.id,
            "workflowId": k.workflow_id,
            "keyName": k.key_name,
            "layout": k.layout,
            "remarks": k.remarks
        } for k in key_name_mappings])

    def post(self):
        data = request.get_json()
        for item in data:
            new_entry = KeyNameMapping(
                workflow_id=item['workflowId'],
                key_name=item['keyName'],
                layout=item['layout'],
                remarks=item['remarks']
            )
            session.add(new_entry)
        session.commit()
        return {"message": "Key name mappings added successfully"}, 201

class KeyNameMappingDetailResource(Resource):
    def put(self, id):
        data = request.get_json()
        key_name_mapping = session.query(KeyNameMapping).filter_by(id=id).first()
        if key_name_mapping:
            key_name_mapping.key_name = data['keyName']
            key_name_mapping.layout = data['layout']
            key_name_mapping.remarks = data['remarks']
            session.commit()
            return {"message": "Key name mapping updated successfully"}, 200
        return {"message": "Key name mapping not found"}, 404

    def delete(self, id):
        key_name_mapping = session.query(KeyNameMapping).filter_by(id=id).first()
        if key_name_mapping:
            session.delete(key_name_mapping)
            session.commit()
            return {"message": "Key name mapping deleted successfully"}, 200
        return {"message": "Key name mapping not found"}, 404

api.add_resource(WorkflowListResource, '/api/workflows')
api.add_resource(KeyNameMappingResource, '/api/keyname-mapping')
api.add_resource(KeyNameMappingDetailResource, '/api/keyname-mapping/<int:id>')

if __name__ == '__main__':
    app.run(debug=True)
```

This setup allows you to fetch key name mappings, update an entry via PUT requests, and delete an entry via DELETE requests. Each action (edit and delete) in the frontend triggers the respective backend endpoint, ensuring that your `KeyNameMapping` table is updated accordingly.













-----------------------------------------------

curl -X OPTIONS http://localhost:5000/api/whitelists \
-H "Access-Control-Request-Method: POST" \
-H "Origin: http://frontend.example.com" \
-H "Access-Control-Request-Headers: Content-Type, Authorization"


curl -X POST http://localhost:5000/api/whitelists \
-H "Content-Type: application/json" \
-d '{"workflow_name": "Example Workflow", "workflow_url": "http://example.com", "environment": "Production", "is_active": true, "created_by": "user@example.com", "modified_by": "user@example.com"}'


from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

# Replace with your SQLALCHEMY_DATABASE_URI
SQLALCHEMY_DATABASE_URI = 'mssql+pyodbc://linga:Iknw@2@pulseaz.database.windows.net:1433/pulserbb?driver=ODBC+Driver+17+for+SQL+Server'

def check_database_connection():
    try:
        engine = create_engine(SQLALCHEMY_DATABASE_URI)
        connection = engine.connect()
        connection.close()
        print("Database connection successful!")
    except OperationalError as e:
        print(f"Error connecting to database: {str(e)}")

if __name__ == "__main__":
    check_database_connection()












------------------------------------------------------------------
# backend/routes.py
from flask import Blueprint, jsonify
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

# Assuming db is your SQLAlchemy object
from . import db

# Define a Blueprint for routes
check_bp = Blueprint('check', __name__)

# Route to test database connection
@check_bp.route('/check_database')
def check_database():
    try:
        # Replace 'mssql+pyodbc://...' with your SQLALCHEMY_DATABASE_URI
        engine = create_engine('mssql+pyodbc://linga:Iknw@2@pulseaz.database.windows.net:1433/pulserbb?driver=ODBC+Driver+17+for+SQL+Server')
        connection = engine.connect()
        connection.close()
        return jsonify({'message': 'Database connection successful'})
    except OperationalError as e:
        return jsonify({'error': str(e)}), 500

# Register the Blueprint
db.init_app(app)
app.register_blueprint(check_bp)

return app







Certainly! Based on your updated table structures, here are the models defined for both SQLAlchemy and Flask-SQLAlchemy.

### SQLAlchemy Models

```python
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Whitelist(Base):
    __tablename__ = 'whitelist'
    id = Column(Integer, primary_key=True)
    workflow_name = Column(String(100), nullable=False)
    workflow_url = Column(String(200), nullable=False)
    environment = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_date = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100), nullable=False)
    modified_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    modified_by = Column(String(100), nullable=False)
    window_titles = Column(String(200), nullable=True)

class Workflow(Base):
    __tablename__ = 'workflows'
    id = Column(Integer, primary_key=True)
    workflow_name = Column(String(100), nullable=False, unique=True)
    system_name = Column(String(100), nullable=False)
    system_version = Column(String(100), nullable=False)
    is_feed = Column(Boolean, default=False)
    is_extension_enabled = Column(Boolean, default=False)
    layout_type = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_date = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100), nullable=False)
    modified_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    modified_by = Column(String(100), nullable=False)

# Database setup
DATABASE_URL = "sqlite:///mydatabase.db"  # Replace with your actual database URL
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)
```

### Flask-SQLAlchemy Models

```python
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Whitelist(db.Model):
    __tablename__ = 'whitelist'
    id = db.Column(db.Integer, primary_key=True)
    workflow_name = db.Column(db.String(100), nullable=False)
    workflow_url = db.Column(db.String(200), nullable=False)
    environment = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(100), nullable=False)
    modified_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    modified_by = db.Column(db.String(100), nullable=False)
    window_titles = db.Column(db.String(200), nullable=True)

class Workflow(db.Model):
    __tablename__ = 'workflows'
    id = db.Column(db.Integer, primary_key=True)
    workflow_name = db.Column(db.String(100), nullable=False, unique=True)
    system_name = db.Column(db.String(100), nullable=False)
    system_version = db.Column(db.String(100), nullable=False)
    is_feed = db.Column(db.Boolean, default=False)
    is_extension_enabled = db.Column(db.Boolean, default=False)
    layout_type = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(100), nullable=False)
    modified_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    modified_by = db.Column(db.String(100), nullable=False)
```

### Explanation

- **Whitelist Table:**
  - `id`: Primary key.
  - `workflow_name`: Name of the workflow.
  - `workflow_url`: URL of the workflow.
  - `environment`: Environment of the workflow.
  - `is_active`: Boolean flag indicating if the workflow is active.
  - `created_date`: Date the entry was created.
  - `created_by`: User who created the entry.
  - `modified_date`: Date the entry was last modified.
  - `modified_by`: User who last modified the entry.
  - `window_titles`: Titles of windows related to the workflow.

- **Workflow Table:**
  - `id`: Primary key.
  - `workflow_name`: Name of the workflow (unique).
  - `system_name`: Name of the system.
  - `system_version`: Version of the system.
  - `is_feed`: Boolean flag indicating if it's a feed.
  - `is_extension_enabled`: Boolean flag indicating if the extension is enabled.
  - `layout_type`: Type of layout.
  - `is_active`: Boolean flag indicating if the workflow is active.
  - `created_date`: Date the entry was created.
  - `created_by`: User who created the entry.
  - `modified_date`: Date the entry was last modified.
  - `modified_by`: User who last modified the entry.

Next, I'll provide the complete backend structure using Flask-SQLAlchemy and best practices.










from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import jwt_required
from ..models import db, Whitelist, Workflow

bp = Blueprint('whitelists', __name__, url_prefix='/api/whitelists')
api = Api(bp)

class WhitelistResource(Resource):
    @jwt_required()
    def get(self):
        whitelists = Whitelist.query.all()
        data = [{
            'id': w.id,
            'workflowid': w.workflowid,
            'workflowname': Workflow.query.get(w.workflowid).workflowname,
            'url': w.url,
            'system': w.system,
            'layout': w.layout,
            'created_date': w.created_date,
            'updated_date': w.updated_date
        } for w in whitelists]
        return jsonify(data)

    @jwt_required()
    def post(self):
        data = request.get_json()
        new_whitelist = Whitelist(
            workflowid=data['workflowid'],
            url=data['url'],
            system=data['system'],
            layout=data['layout']
        )
        db.session.add(new_whitelist)
        db.session.commit()
        return jsonify({'message': 'Whitelist entry created successfully'}), 201

class WhitelistDetailResource(Resource):
    @jwt_required()
    def put(self, id):
        data = request.get_json()
        whitelist = Whitelist.query.get(id)
        if not whitelist:
            return {'message': 'Whitelist entry not found'}, 404

        whitelist.workflowid = data['workflowid']
        whitelist.url = data['url']
        whitelist.system = data['system']
        whitelist.layout = data['layout']
        whitelist.updated_date = datetime.utcnow()

        db.session.commit()
        return {'message': 'Whitelist entry updated successfully'}, 200

    @jwt_required()
    def delete(self, id):
        whitelist = Whitelist.query.get(id)
        if not whitelist:
            return {'message': 'Whitelist entry not found'}, 404

        db.session.delete(whitelist)
        db.session.commit()
        return {'message': 'Whitelist entry deleted successfully'}, 200

api.add_resource(WhitelistResource, '/')
api.add_resource(WhitelistDetailResource, '/<int:id>')


++++++++++-------------------

from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required
from ..models import db, Workflow

bp = Blueprint('workflows', __name__, url_prefix='/api/workflows')
api = Api(bp)

class WorkflowResource(Resource):
    @jwt_required()
    def get(self):
        workflows = Workflow.query.all()
        data = [{'id': w.id, 'workflowname': w.workflowname, 'system': w.system} for w in workflows]
        return jsonify(data)

    @jwt_required()
    def post(self):
        data = request.get_json()
        new_workflow = Workflow(
            workflowname=data['workflowname'],
            system=data['system']
        )
        db.session.add(new_workflow)
        db.session.commit()
        return jsonify({'message': 'Workflow created successfully'}), 201

api.add_resource(WorkflowResource, '/')


+++++++++


from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required
from werkzeug.security import check_password_hash, generate_password_hash
from ..models import db, User

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity={'username': user.username})
        return jsonify(access_token=access_token), 200
    return jsonify({'message': 'Invalid credentials'}), 401

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(username=data['username'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201



+++++++++----------(++++++

import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'mysecretkey')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///mydatabase.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwtsecretkey')



-------

from app import create_app, db
from app.models import User, Workflow, Whitelist

app = create_app()

@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)


---------------------------------------+++------++

Certainly! Here's how you can structure your backend with best practices in mind, including proper project structure, authentication, separation of concerns, and maintaining code quality. We'll use Flask, SQLAlchemy, and Flask-JWT-Extended for authentication.

### Project Structure

Here is a suggested project structure:

```
my_flask_app/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth_routes.py
│   │   ├── workflow_routes.py
│   │   ├── whitelist_routes.py
│   ├── config.py
│   ├── utils.py
├── migrations/
├── tests/
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_workflows.py
│   ├── test_whitelists.py
├── .env
├── requirements.txt
├── run.py
```

### Backend Code

#### `run.py`

```python
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
```

#### `app/__init__.py`

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from .config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)
    
    from .routes import auth_routes, workflow_routes, whitelist_routes
    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(workflow_routes.bp)
    app.register_blueprint(whitelist_routes.bp)
    
    return app
```

#### `app/config.py`

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
```

#### `app/models.py`

```python
from . import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)

class Workflow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workflowname = db.Column(db.String(50), nullable=False)
    system = db.Column(db.String(50), nullable=False)

class Whitelist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workflowid = db.Column(db.Integer, db.ForeignKey('workflow.id'), nullable=False)
    url = db.Column(db.String(200), nullable=False)
    system = db.Column(db.String(50), nullable=False)
    layout = db.Column(db.String(50), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

#### `app/routes/__init__.py`

```python
# Initialize Blueprints
```

#### `app/routes/auth_routes.py`

```python
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from ..models import db, User

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "User already exists"}), 400
    
    new_user = User(username=username, password_hash=generate_password_hash(password))
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User registered successfully"}), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"message": "Invalid credentials"}), 401
    
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200
```

#### `app/routes/workflow_routes.py`

```python
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..models import db, Workflow

bp = Blueprint('workflows', __name__, url_prefix='/api/workflows')

@bp.route('', methods=['GET', 'POST'])
@jwt_required()
def handle_workflows():
    if request.method == 'GET':
        workflows = Workflow.query.all()
        return jsonify([{'id': w.id, 'workflowname': w.workflowname, 'system': w.system} for w in workflows])
    elif request.method == 'POST':
        data = request.get_json()
        new_workflow = Workflow(workflowname=data['workflowname'], system=data['system'])
        db.session.add(new_workflow)
        db.session.commit()
        return jsonify({'message': 'Workflow added successfully'}), 201
```

#### `app/routes/whitelist_routes.py`

```python
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..models import db, Whitelist, Workflow

bp = Blueprint('whitelists', __name__, url_prefix='/api/whitelists')

@bp.route('', methods=['GET', 'POST'])
@jwt_required()
def handle_whitelists():
    if request.method == 'GET':
        whitelists = Whitelist.query.all()
        return jsonify([{
            'id': w.id,
            'workflowid': w.workflowid,
            'workflowname': Workflow.query.get(w.workflowid).workflowname,
            'url': w.url,
            'system': w.system,
            'layout': w.layout,
            'created_date': w.created_date,
            'updated_date': w.updated_date
        } for w in whitelists])
    elif request.method == 'POST':
        data = request.get_json()
        new_whitelist = Whitelist(
            workflowid=data['workflowid'],
            url=data['url'],
            system=data['system'],
            layout=data['layout'],
            created_date=data.get('created_date', datetime.utcnow()),
            updated_date=data.get('updated_date', datetime.utcnow())
        )
        db.session.add(new_whitelist)
        db.session.commit()
        return jsonify({'message': 'Whitelist entry added successfully'}), 201

@bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_whitelist(id):
    data = request.get_json()
    whitelist = Whitelist.query.get(id)
    if whitelist is None:
        return jsonify({'message': 'Whitelist entry not found'}), 404

    whitelist.workflowid = data.get('workflowid', whitelist.workflowid)
    whitelist.url = data.get('url', whitelist.url)
    whitelist.system = data.get('system', whitelist.system)
    whitelist.layout = data.get('layout', whitelist.layout)
    whitelist.updated_date = data.get('updated_date', datetime.utcnow())

    db.session.commit()
    return jsonify({'message': 'Whitelist entry updated successfully'}), 200

@bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_whitelist(id):
    whitelist = Whitelist.query.get(id)
    if whitelist is None:
        return jsonify({'message': 'Whitelist entry not found'}), 404

    db.session.delete(whitelist)
    db.session.commit()
    return jsonify({'message': 'Whitelist entry deleted successfully'}), 200
```

### Explanation

1. **Project Structure:**
   - Organized into folders for routes, models, and configuration, allowing for scalable and maintainable code.

2. **Authentication:**
   - Handled using `Flask-JWT-Extended`.
   - Routes for user registration and login, generating JWT tokens upon successful authentication.

3. **Database Models:**
   - Separate `models.py` file for defining database models.
   - `User` model for authentication, `Workflow` model for workflows, and `Whitelist` model for whitelists.

4. **Routes:**
   - Split into separate modules for different functionalities (auth, workflows, whitelists).
   - `jwt_required` decorator to protect routes and ensure only authenticated users can access them.

5. **Configuration:**
   - Configuration settings in `config.py` for database URI and JWT secret key.
   - Environment variables stored in a `.env` file for sensitive information.

6. **Initialization:**
   - `create_app` function to initialize the Flask app, setup extensions, and register blueprints.

By following this structure, you ensure your backend is well-organized, secure, and scalable. You can further enhance this by adding unit tests in the `tests` directory to cover various functionalities and edge cases.












<template>
  <v-container>
    <v-data-table :headers="headers" :items="whitelists" item-key="id">
      <template v-slot:item.actions="{ item }">
        <v-icon small @click="editItem(item)">mdi-pencil</v-icon>
        <v-icon small @click="deleteItem(item.id)">mdi-delete</v-icon>
      </template>
    </v-data-table>

    <v-dialog v-model="dialog" max-width="600px">
      <v-card>
        <v-card-title>Edit Whitelist</v-card-title>
        <v-card-text>
          <v-autocomplete
            v-model="editedItem.workflow"
            :items="workflows"
            item-text="workflowname"
            item-value="id"
            label="Workflow Name"
            return-object
          ></v-autocomplete>
          <v-text-field v-model="editedItem.url" label="URL"></v-text-field>
          <v-text-field v-model="editedItem.system" label="System"></v-text-field>
          <v-text-field v-model="editedItem.layout" label="Layout"></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-btn color="blue darken-1" @click="saveChanges">Save</v-btn>
          <v-btn color="red darken-1" @click="closeDialog">Cancel</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      whitelists: [],
      headers: [
        { text: 'Workflow Name', align: 'start', value: 'workflowname' },
        { text: 'URL', value: 'url' },
        { text: 'System', value: 'system' },
        { text: 'Layout', value: 'layout' },
        { text: 'Actions', value: 'actions', sortable: false }
      ],
      dialog: false,
      editedItem: {
        id: null,
        workflow: null,
        url: '',
        system: '',
        layout: ''
      },
      workflows: []
    };
  },
  created() {
    this.fetchData();
  },
  methods: {
    fetchData() {
      axios.get('/api/whitelists')
        .then(response => {
          this.whitelists = response.data;
        });
      axios.get('/api/workflows')
        .then(response => {
          this.workflows = response.data;
        });
    },
    editItem(item) {
      this.editedItem = {
        ...item,
        workflow: this.workflows.find(w => w.id === item.workflowid)
      };
      this.dialog = true;
    },
    saveChanges() {
      axios.put(`/api/whitelists/${this.editedItem.id}`, {
        workflowid: this.editedItem.workflow.id,
        url: this.editedItem.url,
        system: this.editedItem.system,
        layout: this.editedItem.layout,
        updated_date: new Date()
      }).then(() => {
        this.fetchData();
        this.closeDialog();
      });
    },
    deleteItem(id) {
      axios.delete(`/api/whitelists/${id}`).then(() => {
        this.fetchData();
      });
    },
    closeDialog() {
      this.dialog = false;
      this.editedItem = {
        id: null,
        workflow: null,
        url: '',
        system: '',
        layout: ''
      };
    }
  }
}
</script>




















----------------------------------------


To ensure the whitelist table in the database is updated correctly when an item is edited in the app store, we'll make some adjustments to the logic both on the frontend and backend. Here's a detailed explanation:

### Frontend Adjustments

We need to ensure that the `workflowid` is sent to the backend whenever a whitelist item is edited. This is already done in the example provided, but let's clarify it further.

#### `AppStore.vue`

```vue
<template>
  <v-container>
    <v-data-table :headers="headers" :items="whitelists" item-key="id">
      <template v-slot:item.actions="{ item }">
        <v-icon small @click="editItem(item)">mdi-pencil</v-icon>
      </template>
    </v-data-table>

    <v-dialog v-model="dialog" max-width="600px">
      <v-card>
        <v-card-title>Edit Whitelist</v-card-title>
        <v-card-text>
          <v-autocomplete
            v-model="editedItem.workflow"
            :items="workflows"
            item-text="workflowname"
            item-value="id"
            label="Workflow Name"
            return-object
          ></v-autocomplete>
          <v-text-field v-model="editedItem.url" label="URL"></v-text-field>
          <v-text-field v-model="editedItem.system" label="System"></v-text-field>
          <v-text-field v-model="editedItem.layout" label="Layout"></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-btn color="blue darken-1" @click="saveChanges">Save</v-btn>
          <v-btn color="red darken-1" @click="closeDialog">Cancel</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      whitelists: [],
      headers: [
        { text: 'Workflow Name', align: 'start', value: 'workflowname' },
        { text: 'URL', value: 'url' },
        { text: 'System', value: 'system' },
        { text: 'Layout', value: 'layout' },
        { text: 'Actions', value: 'actions', sortable: false }
      ],
      dialog: false,
      editedItem: {
        id: null,
        workflow: null,
        url: '',
        system: '',
        layout: ''
      },
      workflows: []
    };
  },
  created() {
    this.fetchData();
  },
  methods: {
    fetchData() {
      axios.get('/api/whitelists')
        .then(response => {
          this.whitelists = response.data;
        });
      axios.get('/api/workflows')
        .then(response => {
          this.workflows = response.data;
        });
    },
    editItem(item) {
      this.editedItem = {
        ...item,
        workflow: this.workflows.find(w => w.id === item.workflowid)
      };
      this.dialog = true;
    },
    saveChanges() {
      axios.put(`/api/whitelists/${this.editedItem.id}`, {
        workflowid: this.editedItem.workflow.id,
        url: this.editedItem.url,
        system: this.editedItem.system,
        layout: this.editedItem.layout,
        updated_date: new Date()
      }).then(() => {
        this.fetchData();
        this.closeDialog();
      });
    },
    closeDialog() {
      this.dialog = false;
      this.editedItem = {
        id: null,
        workflow: null,
        url: '',
        system: '',
        layout: ''
      };
    }
  }
}
</script>
```

### Backend Adjustments

Ensure that the backend properly updates the whitelist table based on the `workflowid`. The whitelist table should contain the `workflowid` as a foreign key that references the `workflows` table.

#### `app.py`

```python
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://username:password@servername/databasename?driver=ODBC+Driver+17+for+SQL+Server'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Workflow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workflowname = db.Column(db.String(50), nullable=False)
    system = db.Column(db.String(50), nullable=False)

class Whitelist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workflowid = db.Column(db.Integer, db.ForeignKey('workflow.id'), nullable=False)
    url = db.Column(db.String(200), nullable=False)
    system = db.Column(db.String(50), nullable=False)
    layout = db.Column(db.String(50), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

@app.route('/api/workflows', methods=['GET', 'POST'])
def handle_workflows():
    if request.method == 'GET':
        workflows = Workflow.query.all()
        return jsonify([{'id': w.id, 'workflowname': w.workflowname, 'system': w.system} for w in workflows])
    elif request.method == 'POST':
        data = request.json
        new_workflow = Workflow(workflowname=data['workflowname'], system=data['system'])
        db.session.add(new_workflow)
        db.session.commit()
        return jsonify({'message': 'Workflow added successfully'}), 201

@app.route('/api/whitelists', methods=['GET', 'POST'])
def handle_whitelists():
    if request.method == 'GET':
        whitelists = Whitelist.query.all()
        return jsonify([{
            'id': w.id,
            'workflowid': w.workflowid,
            'workflowname': Workflow.query.get(w.workflowid).workflowname,
            'url': w.url,
            'system': w.system,
            'layout': w.layout,
            'created_date': w.created_date,
            'updated_date': w.updated_date
        } for w in whitelists])
    elif request.method == 'POST':
        data = request.json
        new_whitelist = Whitelist(
            workflowid=data['workflowid'],
            url=data['url'],
            system=data['system'],
            layout=data['layout'],
            created_date=data.get('created_date', datetime.utcnow()),
            updated_date=data.get('updated_date', datetime.utcnow())
        )
        db.session.add(new_whitelist)
        db.session.commit()
        return jsonify({'message': 'Whitelist entry added successfully'}), 201

@app.route('/api/whitelists/<int:id>', methods=['PUT'])
def update_whitelist(id):
    data = request.json
    whitelist = Whitelist.query.get(id)
    if whitelist is None:
        return jsonify({'message': 'Whitelist entry not found'}), 404

    whitelist.workflowid = data.get('workflowid', whitelist.workflowid)
    whitelist.url = data.get('url', whitelist.url)
    whitelist.system = data.get('system', whitelist.system)
    whitelist.layout = data.get('layout', whitelist.layout)
    whitelist.updated_date = data.get('updated_date', datetime.utcnow())

    db.session.commit()
    return jsonify({'message': 'Whitelist entry updated successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)
```

### Explanation

1. **Frontend (`FormComponent.vue` and `AppStore.vue`):**
   - The `v-autocomplete` component uses the `workflowname` to display the options to the user.
   - When a new whitelist entry is created or edited, the selected workflow's ID (`workflow.id`) is sent to the backend.
   - The `saveChanges` method in `AppStore.vue` sends the `workflowid` along with other form data to the backend for updating the whitelist entry.

2. **Backend (`app.py`):**
   - The `Whitelist` model includes `workflowid` as a foreign key referencing the `Workflow` model.
   - The `/api/whitelists` route handles `GET` and `POST` requests for retrieving and adding whitelist entries, respectively.
   - The `/api/whitelists/<int:id>` route handles `PUT` requests for updating existing whitelist entries.
   - When updating a whitelist entry, the `workflowid` is updated based on the `workflow.id` received from the frontend.

By following this structure, the whitelist table is correctly updated in the database whenever an item is edited in the app store. The frontend uses `workflowname` for display purposes and `workflowid` for backend operations, ensuring the relationship between `workflows` and `whitelist` tables is maintained correctly.









**************************PBR****************************************

Updated Backend Code
app/whitelist.py
python
Copy code
from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import jwt_required
from datetime import datetime
from app.models import db, Whitelist, Workflow

bp = Blueprint('whitelists', __name__, url_prefix='/api/whitelists')
api = Api(bp)

class WhitelistResource(Resource):
    @jwt_required()
    def get(self):
        whitelists = Whitelist.query.all()
        data = [{
            'id': w.id,
            'workflow_name': w.workflow_name,
            'workflow_url': w.workflow_url,
            'environment': w.environment,
            'is_active': w.is_active,
            'created_date': w.created_date,
            'created_by': w.created_by,
            'modified_date': w.modified_date,
            'modified_by': w.modified_by,
            'window_titles': w.window_titles
        } for w in whitelists]
        return jsonify(data)

    @jwt_required()
    def post(self):
        data = request.get_json()
        new_whitelist = Whitelist(
            workflow_name=data['workflow_name'],
            workflow_url=data['workflow_url'],
            environment=data['environment'],
            is_active=data['is_active'],
            created_by=data['created_by'],
            window_titles=data['window_titles'],
            created_date=datetime.utcnow()
        )
        db.session.add(new_whitelist)
        db.session.commit()
        return jsonify({'message': 'Whitelist entry created successfully'}), 201

class WhitelistDetailResource(Resource):
    @jwt_required()
    def put(self, id):
        data = request.get_json()
        whitelist = Whitelist.query.get(id)
        if not whitelist:
            return {'message': 'Whitelist entry not found'}, 404

        whitelist.workflow_name = data['workflow_name']
        whitelist.workflow_url = data['workflow_url']
        whitelist.environment = data['environment']
        whitelist.is_active = data['is_active']
        whitelist.modified_by = data['modified_by']
        whitelist.window_titles = data['window_titles']
        whitelist.modified_date = datetime.utcnow()

        db.session.commit()
        return {'message': 'Whitelist entry updated successfully'}, 200

    @jwt_required()
    def delete(self, id):
        whitelist = Whitelist.query.get(id)
        if not whitelist:
            return {'message': 'Whitelist entry not found'}, 404

        db.session.delete(whitelist)
        db.session.commit()
        return {'message': 'Whitelist entry deleted successfully'}, 200

api.add_resource(WhitelistResource, '/')
api.add_resource(WhitelistDetailResource, '/<int:id>')
app/workflows.py
python
Copy code
from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required
from datetime import datetime
from app.models import db, Workflow

bp = Blueprint('workflows', __name__, url_prefix='/api/workflows')
api = Api(bp)

class WorkflowResource(Resource):
    @jwt_required()
    def get(self):
        workflows = Workflow.query.all()
        data = [{
            'id': w.id,
            'workflow_name': w.workflow_name,
            'system_name': w.system_name,
            'system_version': w.system_version,
            'is_feed': w.is_feed,
            'is_extension_enabled': w.is_extension_enabled,
            'layout_type': w.layout_type,
            'is_active': w.is_active,
            'created_date': w.created_date,
            'created_by': w.created_by,
            'modified_date': w.modified_date,
            'modified_by': w.modified_by
        } for w in workflows]
        return jsonify(data)

    @jwt_required()
    def post(self):
        data = request.get_json()
        new_workflow = Workflow(
            workflow_name=data['workflow_name'],
            system_name=data['system_name'],
            system_version=data['system_version'],
            is_feed=data['is_feed'],
            is_extension_enabled=data['is_extension_enabled'],
            layout_type=data['layout_type'],
            is_active=data['is_active'],
            created_by=data['created_by'],
            created_date=datetime.utcnow()
        )
        db.session.add(new_workflow)
        db.session.commit()
        return jsonify({'message': 'Workflow created successfully'}), 201

class WorkflowDetailResource(Resource):
    @jwt_required()
    def put(self, id):
        data = request.get_json()
        workflow = Workflow.query.get(id)
        if not workflow:
            return {'message': 'Workflow entry not found'}, 404

        workflow.workflow_name = data['workflow_name']
        workflow.system_name = data['system_name']
        workflow.system_version = data['system_version']
        workflow.is_feed = data['is_feed']
        workflow.is_extension_enabled = data['is_extension_enabled']
        workflow.layout_type = data['layout_type']
        workflow.is_active = data['is_active']
        workflow.modified_by = data['modified_by']
        workflow.modified_date = datetime.utcnow()

        db.session.commit()
        return {'message': 'Workflow entry updated successfully'}, 200

    @jwt_required()
    def delete(self, id):
        workflow = Workflow.query.get(id)
        if not workflow:
            return {'message': 'Workflow entry not found'}, 404

        db.session.delete(workflow)
        db.session.commit()
        return {'message': 'Workflow entry deleted successfully'}, 200

api.add_resource(WorkflowResource, '/')
api.add_resource(WorkflowDetailResource, '/<int:id>')
Frontend Updates
html
Copy code
<template>
  <v-container>
    <v-form @submit.prevent="submitForm">
      <v-autocomplete
        v-model="form.workflow_name"
        :items="workflowNames"
        item-text="workflow_name"
        label="Workflow Name"
        required
      ></v-autocomplete>
      <v-icon @click="openWorkflowDialog">mdi-plus</v-icon>

      <v-text-field v-model="form.url" label="URL" required></v-text-field>
      <v-text-field v-model="form.system" label="System" required></v-text-field>
      <v-text-field v-model="form.layout" label="Layout" required></v-text-field>
      <v-btn type="submit" color="primary">Submit</v-btn>
    </v-form>

    <v-dialog v-model="workflowDialog" max-width="500px">
      <v-card>
        <v-card-title>
          <span class="headline">Add Workflow</span>
        </v-card-title>
        <v-card-text>
          <v-form @submit.prevent="submitWorkflow">
            <v-text-field v-model="newWorkflow.workflow_name" label="Workflow Name" required></v-text-field>
            <v-text-field v-model="newWorkflow.system" label="System" required></v-text-field>
            <v-btn type="submit" color="primary">Add</v-btn>
          </v-form>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      form: {
        workflow_name: '',
        url: '',
        system: '',
        layout: ''
      },
      workflowNames: [],
      workflowDialog: false,
      newWorkflow: {
        workflow_name: '',
        system: ''
      }
    };
  },
  created() {
    this.fetchWorkflowNames();
  },
  methods: {
    async fetchWorkflowNames() {
      try {
        const response = await axios.get('/api/workflows/');
        this.workflowNames = response.data;
      } catch (error) {
        console.error(error);
      }
    },
    async submitForm() {
      try {
        await axios.post('/api/whitelists/', this.form);
        alert('Form submitted successfully');
      } catch (error) {
        console.error(error);
      }
    },
    async submitWorkflow() {
      try {
        await axios.post('/api/workflows/', this.newWorkflow);
        this.workflowDialog = false;
        this.fetchWorkflowNames();
        alert('Workflow added successfully');
      } catch (error) {
        console.error(error);
      }
    },
    openWorkflowDialog() {
      this.workflowDialog = true;
    }
  }
};
</script>
models.py
python
Copy code
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Whitelist(db.Model):
    __tablename__ = 'whitelist'
    id = db.Column(db.Integer, primary_key=True)
    workflow_name = db.Column(db.String(100), nullable=False)
    workflow_url = db.Column(db.String(255), nullable=False)
    environment = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(100), nullable=False)
    modified_date = db.Column(db.DateTime)
    modified_by = db.Column(db.String(100))
    window_titles = db.Column(db.String(255))

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Workflow(db.Model):
    __tablename__ = 'workflow'
    id = db.Column(db.Integer, primary_key=True)
    workflow_name = db.Column(db.String(100), nullable=False)
    system_name = db.Column(db.String(100), nullable=False)
    system_version = db.Column(db.String(100), nullable=False)
```python
    is_feed = db.Column(db.Boolean, default=False)
    is_extension_enabled = db.Column(db.Boolean, default=False)
    layout_type = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(100), nullable=False)
    modified_date = db.Column(db.DateTime)
    modified_by = db.Column(db.String(100))

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
__init__.py
python
Copy code
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt = JWTManager(app)

    from app.whitelist import bp as whitelist_bp
    app.register_blueprint(whitelist_bp)

    from app.workflows import bp as workflows_bp
    app.register_blueprint(workflows_bp)

    from auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    return app
config.py
python
Copy code
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your_jwt_secret_key'
auth/routes.py
python
Copy code
from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token, jwt_required, unset_jwt_cookies

class LoginResource(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        # Implement your user authentication logic here
        if username == 'test' and password == 'test':  # Example check
            access_token = create_access_token(identity=username)
            return {'access_token': access_token}, 200

        return {'message': 'Invalid credentials'}, 401

class LogoutResource(Resource):
    @jwt_required()
    def delete(self):
        response = jsonify({'message': 'Logout successful'})
        unset_jwt_cookies(response)
        return response
run.py
python
Copy code
from app import create_app, db

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
Project Structure
arduino
Copy code
your_project/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── whitelist.py
│   └── workflows.py
├── auth/
│   ├── __init__.py
│   └── routes.py
├── config.py
├── run.py
└── requirements.txt
requirements.txt
makefile
Copy code
Flask==2.0.1









Updated Vue Component for App Store
html
Copy code
<template>
  <v-container>
    <v-card>
      <v-card-title>
        App Store
        <v-spacer></v-spacer>
        <v-btn @click="openFormDialog">Add New Entry</v-btn>
      </v-card-title>
      <v-card-text>
        <v-data-table :headers="headers" :items="whitelists" class="elevation-1">
          <template v-slot:item.actions="{ item }">
            <v-icon small class="mr-2" @click="editItem(item)">mdi-pencil</v-icon>
            <v-icon small @click="deleteItem(item)">mdi-delete</v-icon>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <v-dialog v-model="formDialog" max-width="500px">
      <v-card>
        <v-card-title>
          <span class="headline">{{ isEdit ? 'Edit Entry' : 'Add New Entry' }}</span>
        </v-card-title>
        <v-card-text>
          <v-form @submit.prevent="submitForm">
            <v-text-field v-model="form.workflow_name" label="Workflow Name" disabled></v-text-field>
            <v-text-field v-model="form.url" label="URL" required></v-text-field>
            <v-text-field v-model="form.system" label="System" disabled></v-text-field>
            <v-text-field v-model="form.layout" label="Layout" required></v-text-field>
            <v-btn type="submit" color="primary">{{ isEdit ? 'Update' : 'Add' }}</v-btn>
          </v-form>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      whitelists: [],
      headers: [
        { text: 'Workflow Name', value: 'workflow_name' },
        { text: 'System', value: 'system' },
        { text: 'URL', value: 'url' },
        { text: 'Title', value: 'title' },
        { text: 'Environment', value: 'environment' },
        { text: 'Is Active', value: 'is_active' },
        { text: 'Actions', value: 'actions', sortable: false }
      ],
      form: {
        workflow_name: '',
        url: '',
        system: '',
        layout: ''
      },
      workflowNames: [],
      formDialog: false,
      isEdit: false,
      editId: null
    };
  },
  created() {
    this.fetchWhitelists();
  },
  methods: {
    async fetchWhitelists() {
      try {
        const response = await axios.get('/api/whitelists/');
        this.whitelists = response.data.map(item => ({
          id: item.id,
          workflow_name: item.workflow_name,
          system: item.system,
          url: item.url,
          title: item.title,
          environment: item.environment,
          is_active: item.is_active
        }));
      } catch (error) {
        console.error(error);
      }
    },
    async submitForm() {
      try {
        if (this.isEdit) {
          await axios.put(`/api/whitelists/${this.editId}`, this.form);
          alert('Entry updated successfully');
        } else {
          await axios.post('/api/whitelists/', this.form);
          alert('Entry added successfully');
        }
        this.fetchWhitelists();
        this.closeFormDialog();
      } catch (error) {
        console.error(error);
      }
    },
    async deleteItem(item) {
      try {
        await axios.delete(`/api/whitelists/${item.id}`);
        alert('Entry deleted successfully');
        this.fetchWhitelists();
      } catch (error) {
        console.error(error);
      }
    },
    editItem(item) {
      this.form = { ...item };
      this.editId = item.id;
      this.isEdit = true;
      this.formDialog = true;
    },
    openFormDialog() {
      this.resetForm();
      this.formDialog = true;
      this.isEdit = false;
      this.editId = null;
    },
    closeFormDialog() {
      this.formDialog = false;
      this.resetForm();
    },
    resetForm() {
      this.form = {
        workflow_name: '',
        url: '',
        system: '',
        layout: ''
      };
    }
  }
};
</script>
Updated Backend in Flask
models.py
Ensure the models are correctly defined with SQLAlchemy:

python
Copy code
from datetime import datetime
from . import db  # Assuming 'db' is your SQLAlchemy object

class Whitelist(db.Model):
    __tablename__ = 'whitelist'

    id = db.Column(db.Integer, primary_key=True)
    workflow_name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    system = db.Column(db.String(100), nullable=False)
    layout = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    modified_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Workflow(db.Model):
    __tablename__ = 'workflow'

    id = db.Column(db.Integer, primary_key=True)
    workflow_name = db.Column(db.String(100), nullable=False)
    system_name = db.Column(db.String(100), nullable=False)
    system_version = db.Column(db.String(50), nullable=False)
    is_feed = db.Column(db.Boolean, default=False)
    is_extension_enabled = db.Column(db.Boolean, default=False)
    layout_type = db.Column(db.String(50), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    modified_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
routes.py
python
Copy code
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..models import db, Whitelist, Workflow

bp = Blueprint('whitelists', __name__, url_prefix='/api/whitelists')

@bp.route('/', methods=['GET'])
@jwt_required()
def get_whitelists():
    whitelists = Whitelist.query.all()
    data = [{
        'id': w.id,
        'workflow_name': w.workflow_name,
        'system': w.system,
        'url': w.url,
        'title': w.title,  # Adjust according to actual column names in Whitelist table
        'environment': w.environment,  # Adjust according to actual column names in Whitelist table
        'is_active': w.is_active
    } for w in whitelists]
    return jsonify(data)

@bp.route('/', methods=['POST'])
@jwt_required()
def create_whitelist():
    data = request.get_json()
    new_whitelist = Whitelist(
        workflow_name=data['workflow_name'],
        system=Workflow.query.filter_by(workflow_name=data['workflow_name']).first().system_name,
        url=data['url'],
        layout=data['layout'],
        is_active=True  # Adjust default value as needed
    )
    db.session.add(new_whitelist)
    db.session.commit()
    return jsonify({'message': 'Whitelist entry created successfully'}), 201

@bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_whitelist(id):
    data = request.get_json()
    whitelist = Whitelist.query.get(id)
    if not whitelist:
        return jsonify({'message': 'Whitelist entry not found'}), 404

    whitelist.url = data['url']
    whitelist.layout = data['layout']
    whitelist.modified_date = datetime.utcnow()

    db.session.commit()
    return jsonify({'message': 'Whitelist entry updated successfully'}), 200

@bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_whitelist(id):
    whitelist = Whitelist.query.get(id)
    if not whitelist:
        return jsonify({'message': 'Whitelist entry not found'}), 404

    db.session.delete(whitelist)
    db.session.commit()
    return jsonify({'message': 'Whitelist entry deleted successfully'}), 200

Explanation
Frontend: The Vue co
Flask-SQLAlchemy==2.5.1
Flask-RESTful==0.3.9
Flask-JWT-Extended==4.3.1
This setup ensures that your backend is organized using Flask Blueprints, and RESTful API practices are followed with the use of flask_restful. Additionally, the JWTManager is used for authentication, and the database models are defined with SQLAlchemy, leveraging Flask-SQLAlchemy for better integration with Flask.
