<template>
  <v-container class="fill-height bg-grey-lighten-4" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="5" lg="4">
        <v-card class="pa-4" flat border rounded="lg">
          <v-card-title class="text-center text-h5 font-weight-regular mb-4">
            Create Your Account
          </v-card-title>
          <v-card-text>
            <v-form
              @submit.prevent="handleRegister"
              ref="registerForm"
              lazy-validation
            >
              <!-- Username Field -->
              <v-text-field
                v-model="username"
                label="Username"
                name="username"
                prepend-inner-icon="mdi-account-outline"
                type="text"
                required
                :rules="usernameRules"
                variant="outlined"
                density="compact"
                class="mb-4"
              ></v-text-field>

              <!-- Email Field -->
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

              <!-- Password Field -->
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
                hint="Minimum 8 characters"
                persistent-hint
              ></v-text-field>

              <!-- Confirm Password Field -->
              <v-text-field
                v-model="passwordConfirmation"
                label="Confirm Password"
                name="password_confirmation"
                prepend-inner-icon="mdi-lock-check-outline"
                :append-inner-icon="
                  showConfirmPassword
                    ? 'mdi-eye-off-outline'
                    : 'mdi-eye-outline'
                "
                :type="showConfirmPassword ? 'text' : 'password'"
                required
                :rules="confirmPasswordRules"
                variant="outlined"
                density="compact"
                class="mb-4"
                @click:append-inner="showConfirmPassword = !showConfirmPassword"
              ></v-text-field>

              <!-- Error Alert -->
              <v-alert
                v-if="error"
                type="error"
                density="compact"
                variant="tonal"
                class="mb-4"
              >
                {{ error }}
              </v-alert>

              <!-- Register Button -->
              <v-btn
                color="primary"
                @click="handleRegister"
                :loading="loading"
                :disabled="loading"
                block
                size="large"
                variant="flat"
                class="mb-2"
              >
                Register
              </v-btn>

              <!-- Login Link -->
              <div class="text-center mt-4">
                <span class="text-grey">Already have an account?</span>
                <v-btn to="/login" variant="text" color="primary" size="small"
                  >Login Now</v-btn
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
  name: "RegisterView",
  data() {
    return {
      username: "",
      email: "",
      password: "",
      passwordConfirmation: "", // Added for confirmation
      showPassword: false,
      showConfirmPassword: false, // Added for confirmation field
      registerForm: null, // For validation ref

      // Validation Rules
      requiredRule: [(v) => !!v || "This field is required"],
      usernameRules: [
        (v) => !!v || "Username is required",
        (v) => (v && v.length >= 3) || "Username must be at least 3 characters",
        // Optional: Add regex for allowed characters if needed
        // v => /^[a-zA-Z0-9_]+$/.test(v) || 'Username can only contain letters, numbers, and underscores',
      ],
      emailRules: [
        (v) => !!v || "Email is required",
        (v) => /.+@.+\..+/.test(v) || "E-mail must be valid",
      ],
      passwordRules: [
        (v) => !!v || "Password is required",
        (v) => (v && v.length >= 8) || "Password must be at least 8 characters",
        // Optional: Add complexity rules (e.g., uppercase, number, symbol) if desired
      ],
      confirmPasswordRules: [
        (v) => !!v || "Please confirm your password",
        // Check if it matches the password field
        (v) => v === this.password || "Passwords do not match",
      ],
    };
  },
  computed: {
    // Map state from the 'auth' module
    ...mapState("auth", ["loading", "error"]),
  },
  methods: {
    // Map the 'register' action from the 'auth' module
    ...mapActions("auth", ["register"]),

    async handleRegister() {
      // Validate the form using the ref
      const { valid } = await this.$refs.registerForm.validate();

      if (valid) {
        // Call the mapped Vuex action 'register'
        this.register({
          username: this.username,
          email: this.email,
          password: this.password,
          // Note: We don't send passwordConfirmation to the backend
        });
      } else {
        console.log("Registration form is not valid");
      }
    },
  },
  mounted() {
    // Assign the ref after component is mounted
    this.registerForm = this.$refs.registerForm;
  },
};
</script>

<style scoped>
/* Consistent styling with LoginView */
.v-card {
  box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.05) !important; /* Softer shadow */
}
/* Ensure hints don't cause layout shifts if possible */
:deep(.v-input__details) {
  min-height: 14px;
  padding-top: 2px;
}
</style>
