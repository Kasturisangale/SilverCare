<template>
  <div class="login-page">
    <Navbar />
    <div class="login-overlay">
      <div class="glass-container">
        <div class="branding-text">
          <h1>SilverCare</h1>
          <p>Never Miss a Dose, Never Miss a Moment.</p>
        </div>

        <div class="form-container">
          <h2 class="form-title">Login</h2>
          <form @submit.prevent="handleSubmit">
            <div class="input-group">
              <label for="username">Username</label>
              <input
                type="text"
                id="username"
                v-model="username"
                placeholder="Enter your username"
                required
              />
            </div>
            
            <div class="input-group">
              <label for="password">Password</label>
              <input
                type="password"
                id="password"
                v-model="password"
                placeholder="Enter your password"
                required
              />
            </div>

            <button type="submit" class="login-btn">Login</button>
          </form>

          <p v-if="message" class="message" :class="{ error: !success, success: success }">
            {{ message }}
          </p>

          <div class="signup-link">
            <span>
              Not yet registered? <a href="/signup">Click here</a>
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { jwtDecode } from "jwt-decode";
import Navbar from "@/components/Navbar.vue";

export default {
  name: "LibLogin",
  components: { Navbar },
  data() {
    return {
      username: "",
      password: "",
      message: "",
      success: false,
    };
  },
  methods: {
    async handleSubmit() {
      try {
        const response = await fetch("http://localhost:5000/auth/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            username: this.username,
            password: this.password,
          }),
        });
        const data = await response.json();

        const result = response.ok
          ? { success: true, data }
          : { success: false, message: data.message };

        if (result.success) {
          const decodedToken = jwtDecode(result.data.access_token);
          const role = decodedToken.role;
          const user_id = result.data.user_id;

          sessionStorage.setItem("accesstoken", result.data.access_token);
          sessionStorage.setItem("role", role);
          sessionStorage.setItem("user_id", user_id);
          sessionStorage.setItem("first_name", decodedToken.name);
          sessionStorage.setItem("user_name", decodedToken.username);
          sessionStorage.setItem("loggedIn", "true");

          this.message = "Logged in successfully! Redirecting...";
          this.success = true;

          setTimeout(() => {
            if (role === "senior_citizen") this.$router.push(`/sc`);
            else if (role === "care_giver") this.$router.push(`/cg`);
            else if (role === "admin") this.$router.push(`/admin`);
            else this.$router.push("/login");
          }, 1500);
        } else {
          this.message =
            result.message || "Invalid credentials. Please try again!";
          this.success = false;
        }
      } catch (error) {
        console.error("Login error:", error);
        this.message = "An error occurred. Please try again later.";
        this.success = false;
      }
    },
  },
};
</script>

<style scoped>
.login-page {
  height: 100vh;
  width: 100%;
  margin: 0;
  padding: 0;
  background: url('https://media.swncdn.com/via/16464-happy-senior-mature-dad-hugging-prodigal-adul.jpg') no-repeat center center;
  background-size: cover;
  position: relative;
  display: flex;
  flex-direction: column;
  font-family: 'Inter', sans-serif;
}

.login-overlay {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  background: rgba(0, 0, 0, 0.4); /* Darkening overlay */
  padding-top: 60px; /* Offset for navbar */
}

.glass-container {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 2.5rem 3rem;
  width: 100%;
  max-width: 450px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  text-align: center;
  color: white;
}

.branding-text h1 {
  font-family: 'Georgia', serif;
  font-size: calc(3rem * var(--font-scale));
  font-weight: bold;
  margin-bottom: 0.5rem;
  color: #ffffff;
}

.branding-text p {
  font-size: calc(1.1rem * var(--font-scale));
  font-style: italic;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 2rem;
}

.form-container .form-title {
  font-size: calc(1.8rem * var(--font-scale));
  font-weight: 600;
  margin-bottom: 1.5rem;
}

.input-group {
  margin-bottom: 1.25rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  font-size: calc(0.9rem * var(--font-scale));
  text-align: left;
}

input {
  width: 100%;
  padding: 0.8rem 1rem;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.15);
  color: white;
  font-size: calc(1rem * var(--font-scale));
}
input:focus {
  outline: none;
  border-color: #80bdff;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}
input::placeholder {
  color: rgba(255, 255, 255, 0.7);
}

.login-btn {
  width: 100%;
  padding: 0.9rem;
  background-color: #007bff;
  color: white;
  font-weight: 600;
  font-size: calc(1rem * var(--font-scale));
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s ease, transform 0.2s ease;
  margin-top: 1rem;
}

.login-btn:hover {
  background-color: #0056b3;
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

.signup-link {
  margin-top: 1.5rem;
  font-size: calc(0.9rem * var(--font-scale));
}
.signup-link a {
  color: #93c5fd;
  font-weight: 600;
  text-decoration: none;
}
.signup-link a:hover {
  text-decoration: underline;
}
</style>
