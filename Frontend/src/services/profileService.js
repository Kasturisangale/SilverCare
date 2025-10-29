import apiService from "./apiService";

export async function fetchMyMedicines() {
  try {
    const res = await apiService.get("/sc/my-medicines");
    return res.data.medicines || [];
  } catch (err) {
    console.error("Error fetching medicines:", err);
    return [];
  }
}

export async function fetchMyCaregiver() {
  try {
    const res = await apiService.get("/sc/my-caregiver");
    return res.data.caregiver || null;
  } catch (err) {
    console.error("Error fetching caregiver:", err);
    return null;
  }
}

export async function fetchMyDependents() {
  try {
    const res = await apiService.get("/sc/my-dependents");
    return res.data.dependents || [];
  } catch (err) {
    console.error("Error fetching dependents:", err);
    return [];
  }
}
