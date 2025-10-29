<template>
  <div class="landing-wrapper">
    <!-- Navigation -->
    <Navbar :is-landing-page="true" />

    <!-- Hero Section -->
    <section class="hero-section d-flex align-items-center text-white">
      <div class="container text-center">
        <h1 class="hero-title">Compassionate Care for a Life of Dignity.</h1>
        <p class="hero-subtitle">
          Connecting you with skilled, compassionate providers for a better quality of life.
        </p>
        <router-link to="/signup" class="btn btn-primary btn-lg mt-4 hero-btn">
          Get Started
        </router-link>
      </div>
    </section>

    <!-- Features Section -->
    <section id="features" class="features-section">
      <div class="container">
        <div class="text-center mb-5">
          <h2 class="section-title">Peace of Mind for Your Family</h2>
          <p class="section-subtitle">Everything you need to ensure their well-being.</p>
        </div>
        <div class="row g-4">
          <div class="col-md-4">
            <div class="feature-card">
              <div class="feature-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a10 10 0 0 0-10 10 10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2Z"></path><path d="m14.3 14.3 4.25 4.25"></path><path d="M12 18a6 6 0 0 0 6-6 6 6 0 0 0-6-6 6 6 0 0 0-6 6 6 6 0 0 0 6 6Z"></path></svg>
              </div>
              <h3>Medication Reminders</h3>
              <p>Never miss a dose with timely alerts and a clear schedule for caregivers and seniors.</p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="feature-card">
              <div class="feature-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
              </div>
              <h3>Daily Schedule</h3>
              <p>Organize appointments, activities, and daily routines in one accessible calendar.</p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="feature-card">
              <div class="feature-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
              </div>
              <h3>Caregiver Coordination</h3>
              <p>Seamlessly share updates and coordinate tasks between family members and professional caregivers.</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- About Section -->
    <section id="about" class="about-section">
      <div class="container">
        <div class="row align-items-center g-5">
          <div class="col-lg-6">
            <!-- Image Changed -->
            <img src="https://imgs.search.brave.com/gdccOe-m0kv9VdqMmdxtlB8MZS25AwI3gDdafv-9Q-M/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9zdGF0/aWMudmVjdGVlenku/Y29tL3N5c3RlbS9y/ZXNvdXJjZXMvdGh1/bWJuYWlscy8wNDkv/NjQyLzcyOS9zbWFs/bC9hbi1vbGRlci1j/b3VwbGUtYW5kLXRo/ZWlyLWdyYW5kY2hp/bGRyZW4tYXJlLXNt/aWxpbmctZnJlZS12/aWRlby5qcGc" class="img-fluid rounded-3 shadow-lg" alt="Caregiver and senior woman smiling together">
          </div>
          <div class="col-lg-6">
            <h2 class="section-title">Dedicated to a Life of Comfort and Dignity</h2>
            <p class="about-text">We are dedicated to providing the highest level of care to the elderly, ensuring their comfort, and independence. Our team of professionals is trained to handle a wide range of needs with compassion and respect.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer id="contact" class="footer">
      <div class="container">
        <div class="row">
          <div class="col-lg-4 mb-4 mb-lg-0">
            <h4 class="footer-brand">SilverCare<span>.</span></h4>
            <p class="text-muted">Your trusted partner in senior care.</p>
          </div>
          <div class="col-lg-4 mb-4 mb-lg-0">
            <h5 class="footer-heading">Contact Us</h5>
            <ul class="list-unstyled">
              <li>Email: support@silvercare.com</li>
              <li>Phone: +91-8010676679</li>
            </ul>
          </div>
          <div class="col-lg-4">
            <h5 class="footer-heading">Follow Us</h5>
            <p class="text-muted">Stay connected for updates and tips.</p>
          </div>
        </div>
        <div class="text-center text-muted pt-4 mt-4 border-top">
          &copy; {{ new Date().getFullYear() }} SilverCare. All Rights Reserved.
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import Navbar from '@/components/Navbar.vue';
</script>

<style scoped>
/* --- Font Import --- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Georgia&display=swap');

/* --- CSS Variables for Theming --- */
:root {
  --font-primary: 'Inter', sans-serif;
  --font-secondary: 'Georgia', serif;
  --primary-color: #0d6efd; /* Bootstrap Blue for consistency */
  --primary-hover-color: #0b5ed7;
  --text-dark: #212529;
  --text-light: #ffffff;
  --text-muted: #6c757d;
  --shadow-sm: 0 4px 6px rgba(0,0,0,0.05);
  --border-radius: 12px;
}

/* --- Base Styles --- */
.landing-wrapper {
  font-family: var(--font-primary);
  color: var(--text-dark);
  scroll-behavior: smooth;
  background-color: #fff;
}

/* --- Hero Section --- */
.hero-section {
  background: linear-gradient(rgba(0, 30, 60, 0.6), rgba(0, 30, 60, 0.6)), url('https://images.unsplash.com/photo-1584515933487-779824d29309?q=80&w=1920&auto=format&fit=crop');
  background-size: cover;
  background-position: center;
  height: 100vh;
  min-height: 700px;
  padding-top: 80px;
}
.hero-title {
  font-family: var(--font-secondary);
  font-size: calc(4.8rem * var(--font-scale));
  font-weight: 700;
  line-height: 1.2;
  text-shadow: 0 2px 10px rgba(0,0,0,0.3);
}
.hero-subtitle {
  font-size: calc(1.4rem * var(--font-scale));
  max-width: 700px;
  margin: 1.5rem auto 0;
  opacity: 0.9;
  line-height: 1.7;
}

/* --- Buttons --- */
.btn {
  padding: 0.75rem 2rem;
  border-radius: 50px; /* Pill shape */
  font-weight: 600;
  font-size: calc(1rem * var(--font-scale));
  transition: all 0.3s ease;
  border: 2px solid transparent;
}
.hero-btn.btn-primary {
  background-color: 0 10px 20px rgba(31, 4, 237, 0.25);
  border-color: var(--primary-color);
  color: var(--text-light);
  padding: 1rem 2.5rem;
  font-size: calc(1.1rem * var(--font-scale));
}
.hero-btn.btn-primary:hover {
  background-color: var(--primary-hover-color);
  border-color: var(--primary-hover-color);
  transform: translateY(-3px);
  box-shadow: 0 10px 20px rgba(13, 110, 253, 0.25);
}

/* --- General Section Styling --- */
.features-section, .about-section {
  padding: 6rem 0;
}
.section-title {
  font-family: var(--font-secondary);
  font-size: calc(3rem * var(--font-scale));
  font-weight: 700;
  margin-bottom: 1rem;
}
.section-subtitle {
  font-size: calc(1.2rem * var(--font-scale));
  color: var(--text-muted);
  max-width: 600px;
  margin: 0 auto;
}

/* --- Features Section --- */
.features-section {
    background-color: #f8f9fa;
}
.feature-card {
  background-color: #fff;
  padding: 2.5rem 2rem;
  border-radius: var(--border-radius);
  text-align: center;
  box-shadow: var(--shadow-sm);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  height: 100%;
}
.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.08);
}
.feature-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: #e6f0ff;
  color: var(--primary-color);
  margin-bottom: 1.5rem;
}
.feature-icon svg {
    width: 28px;
    height: 28px;
}
.feature-card h3 {
  font-size: calc(1.3rem * var(--font-scale));
  font-weight: 600;
  margin-bottom: 0.75rem;
}
.feature-card p {
  color: var(--text-muted);
  font-size: calc(1rem * var(--font-scale));
  line-height: 1.6;
}

/* --- About Section --- */
.about-text {
  font-size: calc(1.15rem * var(--font-scale));
  line-height: 1.8;
  color: var(--text-muted);
}

/* --- Footer --- */
.footer {
  background-color: var(--text-dark);
  color: #adb5bd;
  padding: 4rem 0;
}
.footer-brand {
  font-family: var(--font-secondary);
  font-weight: 700;
  font-size: calc(1.75rem * var(--font-scale));
  color: var(--text-light);
}
.footer-brand span {
  color: var(--primary-color);
}
.footer-heading {
  color: var(--text-light);
  font-weight: 600;
  font-size: calc(1.1rem * var(--font-scale));
  margin-bottom: 1rem;
}
.footer .list-unstyled li {
  margin-bottom: 0.5rem;
  font-size: calc(1rem * var(--font-scale));
}

/* --- Responsive Adjustments --- */
@media (max-width: 991.98px) {
  .hero-title {
    font-size: calc(3.5rem * var(--font-scale));
  }
}

@media (max-width: 768px) {
    .hero-title {
        font-size: calc(2.8rem * var(--font-scale));
    }
    .hero-subtitle {
        font-size: calc(1.2rem * var(--font-scale));
    }
    .section-title {
        font-size: calc(2.2rem * var(--font-scale));
    }
}
</style>
