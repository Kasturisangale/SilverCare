import axios from "axios";
import { emitter } from "@/eventBus";

const apiService = axios.create({
  baseURL: "http://127.0.0.1:5000",
  headers: {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
  },
});

export async function verifyToken() {
  try {
    const token = sessionStorage.getItem("accesstoken");
    if (!token) return false;

    const response = await axios.get(
      "http://127.0.0.1:5000/set/api/verify-token",
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    const isValid = response.data.valid;
    if (!isValid) {
      handleLogout();
    }
    return isValid;
  } catch (error) {
    handleLogout();
    return false;
  }
}

function handleLogout() {
  sessionStorage.clear();
  emitter.emit("loginStateChanged", false);
}

// Request interceptor
apiService.interceptors.request.use(
  async (config) => {
    // Skip token verification for login endpoint
    if (config.url.includes("/login")) {
      return config;
    }

    const token = sessionStorage.getItem("accesstoken");
    if (!token) {
      handleLogout();
      return Promise.reject(new Error("No token found"));
    }

    // Add token to headers
    config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiService.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      switch (error.response.status) {
        case 401:
        case 403:
          handleLogout();
          break;
      }
    }
    return Promise.reject(error);
  }
);

export default apiService;
