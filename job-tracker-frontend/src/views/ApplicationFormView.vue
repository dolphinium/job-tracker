<template>
  <main-layout>
    <v-card>
      <v-card-title>
        {{ isEdit ? "Edit Application" : "New Application" }}
      </v-card-title>
      <v-card-text>
        <v-form ref="form" v-model="valid" @submit.prevent="saveApplication">
          <v-text-field
            v-model="form.linkedin_url"
            label="LinkedIn Job URL"
            required
            :rules="[(v) => !!v || 'URL is required']"
          ></v-text-field>

          <v-text-field v-model="form.title" label="Job Title"></v-text-field>

          <v-text-field v-model="form.company" label="Company"></v-text-field>

          <v-text-field v-model="form.location" label="Location"></v-text-field>

          <v-select
            v-model="form.status"
            :items="statusOptions"
            label="Status"
            required
          ></v-select>

          <v-menu
            v-model="dateMenu"
            :close-on-content-click="false"
            min-width="auto"
          >
            <template v-slot:activator="{ on, attrs }">
              <v-text-field
                v-model="formattedDate"
                label="Applied Date"
                readonly
                v-bind="attrs"
                v-on="on"
              ></v-text-field>
            </template>
            <v-date-picker
              v-model="form.applied_date"
              @input="dateMenu = false"
            ></v-date-picker>
          </v-menu>

          <v-textarea
            v-model="form.job_description"
            label="Job Description"
            rows="5"
          ></v-textarea>

          <v-textarea v-model="form.notes" label="Notes" rows="3"></v-textarea>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="error" text :to="'/applications'"> Cancel </v-btn>
        <v-btn color="primary" :loading="loading" @click="saveApplication">
          Save
        </v-btn>
      </v-card-actions>
    </v-card>
  </main-layout>
</template>

<script>
import { mapState, mapActions } from "vuex";
import MainLayout from "@/layouts/MainLayout.vue";

export default {
  name: "ApplicationFormView",
  components: {
    MainLayout,
  },
  data() {
    return {
      valid: false,
      form: {
        linkedin_url: "",
        title: "",
        company: "",
        location: "",
        job_description: "",
        applied_date: null,
        status: "Wishlist",
        notes: "",
      },
      dateMenu: false,
      statusOptions: [
        "Wishlist",
        "Applied",
        "Screening",
        "Interview",
        "Technical Test",
        "Final Interview",
        "Offer",
        "Accepted",
        "Rejected",
        "Withdrawn",
      ],
    };
  },
  computed: {
    ...mapState("applications", ["loading", "currentApplication"]),
    isEdit() {
      return !!this.$route.params.id;
    },
    formattedDate() {
      return this.form.applied_date
        ? new Date(this.form.applied_date).toLocaleDateString()
        : "";
    },
  },
  methods: {
    ...mapActions("applications", [
      "createApplication",
      "updateApplication",
      "fetchApplication",
    ]),
    async saveApplication() {
      if (this.$refs.form.validate()) {
        try {
          if (this.isEdit) {
            await this.updateApplication({
              id: this.$route.params.id,
              data: this.form,
            });
          } else {
            await this.createApplication(this.form);
          }
          this.$router.push("/applications");
        } catch (error) {
          console.error("Error saving application:", error);
        }
      }
    },
  },
  async created() {
    if (this.isEdit) {
      await this.fetchApplication(this.$route.params.id);
      if (this.currentApplication) {
        // Copy values to form
        Object.keys(this.form).forEach((key) => {
          if (this.currentApplication[key] !== undefined) {
            this.form[key] = this.currentApplication[key];
          }
        });
      }
    }
  },
};
</script>
