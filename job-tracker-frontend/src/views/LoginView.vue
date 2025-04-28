<template>
  <v-container class="fill-height bg-grey-lighten-4" fluid>
    <!-- Match main background -->
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="5" lg="4">
        <!-- Use flat card with border -->
        <v-card class="pa-4" flat border rounded="lg">
          <v-card-title class="text-center text-h5 font-weight-regular mb-4">
            Welcome Back
          </v-card-title>
          <v-card-text>
            <!-- Use lazy-validation -->
            <v-form
              @submit.prevent="handleLogin"
              ref="loginForm"
              lazy-validation
            >
              <v-text-field
                v-model="email"
                label="Email Address"
                name="email"
                prepend-inner-icon="mdi-email-outline"
                type="email"
                required
                :rules="emailRules"
                variant="outlined"
                density="compact"
                class="mb-4"
              ></v-text-field>

              <v-text-field
                v-model="password"
                label="Password"
                name="password"
                prepend-inner-icon="mdi-lock-outline"
                :append-inner-icon="
                  showPassword ? 'mdi-eye-off-outline' : 'mdi-eye-outline'
                "
                :type="showPassword ? 'text' : 'password'"
                required
                :rules="passwordRules"
                variant="outlined"
                density="compact"
                class="mb-4"
                @click:append-inner="showPassword = !showPassword"
              ></v-text-field>

              <v-alert
                v-if="error"
                type="error"
                density="compact"
                variant="tonal"
                class="mb-4"
              >
                {{ error }}
              </v-alert>

              <v-btn
                color="primary"
                @click="handleLogin"
                :loading="loading"
                :disabled="loading"
                block
                size="large"
                variant="flat"
                class="mb-2"
              >
                Login
              </v-btn>

              <div class="text-center mt-4">
                <span class="text-grey">Don't have an account?</span>
                <v-btn
                  to="/register"
                  variant="text"
                  color="primary"
                  size="small"
                  >Register Now</v-btn
                >
              </div>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mapState, mapActions } from "vuex";

export default {
  name: "LoginView",
  data() {
    return {
      email: "",
      password: "",
      showPassword: false,
      loginForm: null, // For validation ref
      emailRules: [
        (v) => !!v || "Email is required",
        (v) => /.+@.+\..+/.test(v) || "Email must be valid",
      ],
      passwordRules: [(v) => !!v || "Password is required"],
    };
  },
  computed: {
    ...mapState("auth", ["loading", "error"]),
  },
  methods: {
    ...mapActions("auth", ["login"]),
    async handleLogin() {
      const { valid } = await this.$refs.loginForm.validate();
      if (valid) {
        this.login({
          email: this.email,
          password: this.password,
        });
      }
    },
  },
  mounted() {
    this.loginForm = this.$refs.loginForm;
  },
};
</script>

<style scoped>
.v-card {
  /* Override potential default shadows if needed */
  box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.05) !important; /* Softer shadow */
}
</style>
