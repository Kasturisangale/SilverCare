import { createRouter, createWebHistory } from "vue-router";

// --- Import your components ---
import SignUp from "./components/SignUp.vue";
import HomePage from "./components/HomePage.vue";
import Login from "./components/Login.vue";
import ManageDependents from "./components/ManageDependents.vue";
import DependentProfile from "./components/DependentProfile.vue";
import AccessDenied from "./components/AccessDenied.vue";
import SeniorCitizenDashboard from "./components/SeniorCitizenDashboard.vue";
import AdminDashboard from "./components/AdminDashboard.vue";
import UserProfile from "./components/UserProfile.vue";
import StatsPage from "./components/StatsPage.vue";
import LandingPage from './components/LandingPage.vue';
import AdminMedicines from "./components/AdminMedicines.vue";
const routes = [
  // --- Public Routes ---
  {
        name: 'LandingPage',
        component: LandingPage,
        path: '/',
    },
  {
    name: "Login",
    component: Login,
    path: "/login",
  },
  {
    name: "SignUp",
    component: SignUp,
    path: "/signup",
  },
  {
    name: "AccessDenied",
    component: AccessDenied,
    path: "/access-denied",
  },

  // --- Protected Routes ---
  {
    name: "ManageDependents",
    component: ManageDependents,
    path: "/manage-dependents",
    meta: {
      requiresAuth: false,
      allowedRoles: ["care_giver"], //if 'all' is present, it means any user can access this route
    },
  },
  {
    name: "HomePage",
    component: HomePage,
    path: "/cg", // The dynamic path
  },
  {
    name: "SeniorCitizenDashboard",
    component: SeniorCitizenDashboard,
    path: "/sc",
    meta: {
      requiresAuth: false,
      requiresHasDep: false,
      // NO `allowedRoles` key means ANY logged-in user can access it.
    },
  },
  {
    name: "AdminDashboard",
    component: AdminDashboard,
    path: "/admin",
    meta: {
      requiresAuth: false,
      requiresHasDep: false,
      // NO `allowedRoles` key means ANY logged-in user can access it.
    },
  },
  {
    name: "DependentProfile",
    path: "/cg/:userId/dependantProfile",
    component: DependentProfile,
    meta: {
      requiresAuth: false,
      allowedRoles: ["caregiver", "senior_citizen", "all"],
    },
  },
  {
    path: "/profile",
    name: "UserProfile",
    component: UserProfile,
  },
  {
    path: "/stats",
    name: "StatsPage",
    component: StatsPage,
  },
  {
    path: "/admin-medicines",
    name: "AdminMedicines",
    component: AdminMedicines,
  },
  
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Global Navigation Guard
router.beforeEach((to, from, next) => {
  // Get meta properties from the route
  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth);
  const requiresHasDep = to.matched.some(
    (record) => record.meta.requiresHasDep
  );
  const allowedRoles = to.meta.allowedRoles;

  // Get status from sessionStorage
  const isLoggedIn = sessionStorage.getItem("isLoggedIn") === "true";
  const hasDep = sessionStorage.getItem("hasDep") === "true";
  const userRole = sessionStorage.getItem("role"); // This will be null if not set

  // CHECK 1: AUTHENTICATION
  if (requiresAuth && !isLoggedIn) {
    return next({ name: "Login" });
  }

  // ========================================================================
  // CHECK 2: AUTHORIZATION (ROLE CHECK) - THIS IS THE FIXED LOGIC
  // ========================================================================
  // This check only runs if the route has a defined `allowedRoles` array with at least one role.
  // If `meta.allowedRoles` is missing or is an empty array, this entire block is skipped.
  if (
    allowedRoles &&
    Array.isArray(allowedRoles) &&
    allowedRoles.length > 0 &&
    !allowedRoles.includes("all") // <-- The new bypass condition
  ) {
    // This is the strict check for specific roles.
    // It runs only if the route has roles like ['caregiver'] or ['admin'].
    if (!userRole || !allowedRoles.includes(userRole)) {
      return next({ name: "AccessDenied" });
    }
  }

  // CHECK 3: DEPENDENT CHECK ('hasDep')
  // Runs after auth and role checks have passed.
  if (requiresHasDep && !hasDep && to.name !== "ManageDependents") {
    return next({ name: "ManageDependents" });
  }

  // If all checks passed, allow navigation
  next();
});

export default router;
