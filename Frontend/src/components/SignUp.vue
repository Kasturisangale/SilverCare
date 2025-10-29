<template>
  <div class="signup-page">
    <Navbar />
    <div class="overlay">
      <div class="glass-container">
        <!-- Branding text like login page -->
        <div class="branding-text">
          <h1>SilverCare</h1>
          <p>Never Miss a Dose, Never Miss a Moment.</p>
        </div>

        <!-- Form -->
        <div class="form-container">
          <h2 class="form-title">Create Account</h2>
          <form @submit.prevent="handleSubmit">
            <!-- First & Last Name on same line -->
            <div class="form-row">
              <div class="input-group">
                <label for="first_name">First Name</label>
                <input type="text" id="first_name" v-model="first_name" placeholder="Enter your First Name" required />
              </div>
              <div class="input-group">
                <label for="last_name">Last Name</label>
                <input type="text" id="last_name" v-model="last_name" placeholder="Enter your Last Name" required />
              </div>
            </div>

            <div class="input-group">
              <label for="username">Username</label>
              <input type="text" id="username" v-model="username" placeholder="Enter a username" required />
            </div>

            <!-- Password & Confirm Password on same line -->
            <div class="form-row">
              <div class="input-group">
                <label for="password">Password</label>
                <input type="password" id="password" v-model="password" placeholder="Enter a password" required />
              </div>
              <div class="input-group">
                <label for="confirm_password">Confirm Password</label>
                <input type="password" id="confirm_password" v-model="confirm_password" placeholder="Confirm password" required />
              </div>
            </div>

            <div class="input-group">
              <label for="role">Role</label>
              <select id="role" v-model="role" required>
                <option disabled value="">Select Role</option>
                <option value="care_giver">Care Giver</option>
                <option value="senior_citizen">Dependent</option>
              </select>
            </div>

            <button type="submit" class="register-btn">Register</button>
          </form>

          <p v-if="message" class="message" :class="{ error: !success, success: success }">{{ message }}</p>

          <div class="login-link">
            <span>
              Already have an account?
              <a href="/login">Login here</a>
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Navbar from "@/components/Navbar.vue";
export default {
  name: "SignUpPage",
  components: { Navbar },
  data() {
    return {
      first_name: "",
      last_name: "",
      username: "",
      password: "",
      confirm_password: "",
      role: "",
      message: "",
      success: false,
    };
  },
  methods: {
    async handleSubmit() {
      if (this.password !== this.confirm_password) {
        this.message = "Confirmation password must be the same as your password.";
        this.success = false;
        return;
      }
      try {
        const response = await fetch("http://localhost:5000/auth/signup", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            first_name: this.first_name,
            last_name: this.last_name,
            username: this.username,
            password: this.password,
            confirm_password: this.confirm_password,
            role: this.role,
          }),
        });

        const data = await response.json();
        const result = response.ok
          ? { success: true }
          : { success: false, message: data.message };

        if (result.success) {
          this.message = "Registered successfully! Please login.";
          this.success = true;
          this.first_name = "";
          this.last_name = "";
          this.username = "";
          this.password = "";
          this.confirm_password = "";
          this.role = "";
          setTimeout(() => {
            this.$router.push("/login");
          }, 1500);
        } else {
          this.message = result.message || "Registration failed.";
          this.success = false;
        }
      } catch (error) {
        console.error("Registration error:", error);
        this.message = "An error occurred. Please try again.";
        this.success = false;
      }
    },
  },
};
</script>

<style scoped>
.signup-page {
  height: 100vh;
  width: 100%;
  margin: 0;
  padding: 0;
  background: url("https://media.swncdn.com/via/16464-happy-senior-mature-dad-hugging-prodigal-adul.jpg") no-repeat center center;
  background-size: cover;
  position: relative;
  display: flex;
  flex-direction: column;
  font-family: 'Inter', sans-serif;
}

.overlay {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  background: rgba(0, 0, 0, 0.4);
  padding-top: 60px; /* Offset for navbar */
}

.glass-container {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 2rem 2.5rem;
  width: 100%;
  max-width: 550px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
  text-align: center;
  color: white;
}

.branding-text h1 {
  font-family: 'Georgia', serif;
  font-size: calc(2.5rem * var(--font-scale));
  font-weight: bold;
  margin-bottom: 0.3rem;
  color: #ffffff;
}

.branding-text p {
  font-size: calc(1rem * var(--font-scale));
  font-style: italic;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 1.5rem;
}

.form-container .form-title {
  font-size: calc(1.5rem * var(--font-scale));
  font-weight: 600;
  margin-bottom: 1rem;
}

.input-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  font-size: calc(0.9rem * var(--font-scale));
  text-align: left;
}

input,
select {
  width: 100%;
  padding: 0.8rem 1rem;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.15);
  color: white;
  font-size: calc(1rem * var(--font-scale));
}

input:focus,
select:focus {
  outline: none;
  border-color: #80bdff;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

input::placeholder {
  color: rgba(255, 255, 255, 0.7);
}

select {
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  background-image: url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%27http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%27%20width%3D%27292.4%27%20height%3D%27292.4%27%3E%3Cpath%20fill%3D%27%23ffffff%27%20d%3D%27M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%27%2F%3E%3C%2Fsvg%3E");
  background-repeat: no-repeat;
  background-position: right 1rem center;
  background-size: 0.65em auto;
}

select option {
  background-color: #333;
  color: white;
}

.register-btn {
  width: 100%;
  padding: 0.9rem;
  background-color: #28a745;
  color: white;
  font-weight: 600;
  font-size: calc(1rem * var(--font-scale));
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s ease, transform 0.2s ease;
  margin-top: 1rem;
}

.register-btn:hover {
  background-color: #218838;
  transform: translateY(-2px);
}

.message {
  margin-top: 1rem;
  font-size: calc(0.9rem * var(--font-scale));
}
.message.success {
  color: #a7f3d0;
}
.message.error {
  color: #fca5a5;
}

.form-row {
  display: flex;
  gap: 1.25rem;
}

.form-row > div {
  flex: 1;
}

.login-link {
  margin-top: 1.5rem;
  font-size: calc(0.9rem * var(--font-scale));
}
.login-link a {
  color: #93c5fd;
  font-weight: 600;
  text-decoration: none;
}
.login-link a:hover {
  text-decoration: underline;
}
</style>
