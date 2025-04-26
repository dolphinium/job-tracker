<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card class="elevation-12">
          <v-toolbar color="primary" dark flat>
            <v-toolbar-title>Register</v-toolbar-title>
          </v-toolbar>
          <v-card-text>
            <v-form @submit.prevent="handleRegister">
              <v-text-field
                v-model="username"
                label="Username"
                name="username"
                prepend-icon="mdi-account"
                type="text"
                required
              ></v-text-field>

              <v-text-field
                v-model="email"
                label="Email"
                name="email"
                prepend-icon="mdi-email"
                type="email"
                required
              ></v-text-field>

              <v-text-field
                v-model="password"
                label="Password"
                name="password"
                prepend-icon="mdi-lock"
                type="password"
                required
              ></v-text-field>
            </v-form>
            <v-alert v-if="error" type="error">{{ error }}</v-alert>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn to="/login" text>Already have an account?</v-btn>
            <v-btn color="primary" @click="handleRegister" :loading="loading">
              Register
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mapState, mapActions } from "vuex";

export default {
  name: "RegisterView",
  data() {
    return {
      username: "",
      email: "",
      password: "",
    };
  },
  computed: {
    ...mapState("auth", ["loading", "error"]),
  },
  methods: {
    ...mapActions("auth", ["register"]),
    handleRegister() {
      this.register({
        username: this.username,
        email: this.email,
        password: this.password,
      });
    },
  },
};
</script>
