import apiService from "./apiService";

const medicationService = {
  // Generate calendar data for a specific month/year
  async generateCalendarData(month, year, dependentId) {
    try {
      console.log(
        `API Call: /sc/status-report with body: { month: ${month}, year: ${year}, user_id: ${dependentId} }`
      );

      const userId = dependentId || sessionStorage.getItem("user_id");
      if (!userId) {
        console.error("No user_id in sessionStorage or dependentId provided");
        return [];
      }

      const body = { month, year, user_id: parseInt(userId) };

      const response = await apiService.post("/sc/status-report", body);
      const result = response.data;

      console.log("API Response:", result);

      if (Object.keys(result).length === 0) {
        console.log("API returned no data for the requested month.");
      }

      const daysInMonth = new Date(year, month, 0).getDate();
      const firstDay = new Date(year, month - 1, 1);
      let startingDayOfWeek = firstDay.getDay();
      startingDayOfWeek = startingDayOfWeek === 0 ? 6 : startingDayOfWeek - 1;

      const today = new Date();
      today.setHours(0, 0, 0, 0);

      const medicationDays = [];

      for (let i = 0; i < startingDayOfWeek; i++) {
        medicationDays.push({
          label: "",
          date: null,
          medicationData: null,
        });
      }

      for (let day = 1; day <= daysInMonth; day++) {
        // FIX: Use Date.UTC to create a timezone-independent date
        const currentDate = new Date(Date.UTC(year, month - 1, day));
        const dateStr = currentDate.toISOString().split("T")[0];

        const isToday = currentDate.getTime() === today.getTime();
        const isFuture = currentDate > today;
        const isPast = currentDate < today;

        let medicationData = null;

        if (result[dateStr]) {
          const dayData = result[dateStr];
          const taken = dayData.taken || 0;
          const missed = dayData.missed || 0;
          const total = taken + missed;

          const takenPercentage = total > 0 ? (taken / total) * 100 : 0;
          const missedPercentage = total > 0 ? (missed / total) * 100 : 0;

          medicationData = {
            taken,
            missed,
            takenPercentage,
            missedPercentage,
            isToday,
            isFuture,
            isPast,
          };
        }

        medicationDays.push({
          label: day.toString(),
          date: dateStr,
          medicationData: medicationData,
        });
      }

      return medicationDays;
    } catch (err) {
      console.error("API call failed, generating fallback data:", err);
      return await this.generateFallbackData(month, year);
    }
  },

  async generateFallbackData(month, year) {
    const today = new Date();
    const daysInMonth = new Date(year, month, 0).getDate();
    const firstDay = new Date(year, month - 1, 1);
    let startingDayOfWeek = firstDay.getDay();
    startingDayOfWeek = startingDayOfWeek === 0 ? 6 : startingDayOfWeek - 1;
    const fallbackDays = [];

    for (let i = 0; i < startingDayOfWeek; i++) {
      fallbackDays.push({
        label: "",
        date: null,
        medicationData: null,
      });
    }

    for (let day = 1; day <= daysInMonth; day++) {
      const isToday =
        day === today.getDate() &&
        month === today.getMonth() + 1 &&
        year === today.getFullYear();
      const isFuture = new Date(year, month - 1, day) > today && !isToday;
      const isPast = new Date(year, month - 1, day) < today && !isToday;

      let medicationData = null;
      if (!isFuture) {
        const taken = Math.floor(Math.random() * 3);
        const missed = Math.floor(Math.random() * 2);
        const total = taken + missed;

        const takenPercentage = total > 0 ? (taken / total) * 100 : 0;
        const missedPercentage = total > 0 ? (missed / total) * 100 : 0;

        medicationData = {
          taken,
          missed,
          takenPercentage,
          missedPercentage,
          isToday,
          isFuture,
          isPast,
        };
      }

      fallbackDays.push({
        label: day.toString(),
        date: `${year}-${month.toString().padStart(2, "0")}-${day
          .toString()
          .padStart(2, "0")}`,
        medicationData,
      });
    }

    return fallbackDays;
  },

  async getDayMedications(date) {
    await new Promise((resolve) => setTimeout(resolve, 300));
    return {
      date,
      medications: [
        { name: "Vitamin D", time: "8:00 AM", status: "taken", person: "Mom" },
        {
          name: "Blood Pressure Med",
          time: "12:00 PM",
          status: "missed",
          person: "Dad",
        },
      ],
    };
  },

  async getMedicationReport(month, year, userId) {
    try {
      const response = await apiService.post("/sc/status-report", {
        month,
        year,
        user_id: userId,
      });
      return response.data;
    } catch (error) {
      console.error("Error fetching medication report:", error);
      throw error;
    }
  },

  async getAllMedicines() {
    try {
      const response = await apiService.get("/sc/medicines");
      return response.data;
    } catch (error) {
      console.error("Error fetching medicines:", error);
      throw error;
    }
  },

  async getUpcomingMedicines() {
    try {
      const response = await apiService.get("/sc/upcoming-medications");
      return response.data;
    } catch (error) {
      console.error("Error fetching upcoming medicines:", error);
      throw error;
    }
  },

  async sendReminder(userId, medicineId) {
    try {
      const response = await apiService.post("/sc/send-reminder", {
        user_id: userId,
        medicine_id: medicineId,
      });
      return response.data;
    } catch (error) {
      console.error("Error sending reminder:", error);
      throw error;
    }
  },
};

export default medicationService;
