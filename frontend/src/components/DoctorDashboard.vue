<template>
  <div>
    <h4 class="mb-3">Doctor Dashboard</h4>

    <div v-if="doctor" class="mb-3 d-flex align-items-center">
      <div
        class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center me-3"
        style="width: 44px; height: 44px"
      >
        <i class="bi bi-person-badge"></i>
      </div>
      <div>
        <div class="fw-semibold">
          Dr. {{ doctor.full_name }}
        </div>
        <small class="text-muted">{{ doctor.specialization }}</small>
      </div>
    </div>

    <div class="row">
      <div class="col-lg-7 mb-4">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white">
            <i class="bi bi-calendar-event me-1"></i> Appointments
          </div>
          <div class="card-body p-0" style="max-height: 260px; overflow-y: auto">
            <table class="table table-hover table-sm mb-0">
              <thead class="table-light">
                <tr>
                  <th>ID</th>
                  <th>Patient</th>
                  <th>Date</th>
                  <th>Time</th>
                  <th>Status</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="a in appointments"
                  :key="a.id"
                  :class="{ 'table-active': a.id === selectedAppointmentId }"
                  @click="selectAppointment(a)"
                  style="cursor: pointer"
                >
                  <td>{{ a.id }}</td>
                  <td>{{ a.patient }}</td>
                  <td>{{ a.date }}</td>
                  <td>{{ a.time }}</td>
                  <td>{{ a.status }}</td>
                  <td>
                    <select
                      class="form-select form-select-sm"
                      v-model="a.status"
                      @change="updateStatus(a)"
                    >
                      <option>Booked</option>
                      <option>Completed</option>
                      <option>Cancelled</option>
                    </select>
                  </td>
                </tr>
                <tr v-if="!appointments.length">
                  <td colspan="6" class="text-muted text-center py-3">
                    No appointments yet.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Treatment form -->
      <div class="col-lg-5 mb-4">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white">
            <i class="bi bi-file-earmark-medical me-1"></i> Update Patient
            History
            <span v-if="currentAppointment" class="small ms-2 text-muted">
              (Appt #{{ currentAppointment.id }} –
              {{ currentAppointment.patient }})
            </span>
          </div>
          <div class="card-body">
            <div v-if="!currentAppointment" class="text-muted small">
              Select an appointment on the left to add diagnosis.
            </div>
            <form v-else @submit.prevent="saveTreatment">
              <div class="mb-2">
                <label class="form-label small">Diagnosis</label>
                <textarea
                  v-model="treatment.diagnosis"
                  class="form-control"
                  rows="2"
                />
              </div>
              <div class="mb-2">
                <label class="form-label small">Prescription</label>
                <textarea
                  v-model="treatment.prescription"
                  class="form-control"
                  rows="2"
                />
              </div>
              <div class="mb-2">
                <label class="form-label small">Notes</label>
                <textarea
                  v-model="treatment.notes"
                  class="form-control"
                  rows="2"
                />
              </div>
              <div class="mb-2">
                <label class="form-label small">Next Visit Date</label>
                <input
                  type="date"
                  v-model="treatment.next_visit_date"
                  class="form-control"
                />
              </div>
              <button class="btn btn-success w-100">
                <i class="bi bi-save me-1"></i> Save Treatment
              </button>
            </form>
            <div v-if="msg" class="alert alert-info mt-2 py-2 small">
              {{ msg }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Availability -->
    <div class="card border-0 shadow-sm">
      <div class="card-header bg-white">
        <i class="bi bi-clock-history me-1"></i> Availability (next 7 days)
      </div>
      <div class="card-body">
        <div class="row g-2 mb-2">
          <div class="col-md-3">
            <input
              type="date"
              v-model="availForm.date"
              class="form-control form-control-sm"
            />
          </div>
          <div class="col-md-3">
            <input
              type="time"
              v-model="availForm.start"
              class="form-control form-control-sm"
            />
          </div>
          <div class="col-md-3">
            <input
              type="time"
              v-model="availForm.end"
              class="form-control form-control-sm"
            />
          </div>
          <div class="col-md-3 d-grid">
            <button class="btn btn-outline-primary btn-sm" @click="addSlot">
              <i class="bi bi-plus-lg me-1"></i> Add Slot
            </button>
          </div>
        </div>

        <ul class="list-group mb-3 small">
          <li
            v-for="(s, idx) in slots"
            :key="idx"
            class="list-group-item d-flex justify-content-between align-items-center"
          >
            {{ s.date }} | {{ s.start }} – {{ s.end }}
            <button
              class="btn btn-sm btn-outline-danger"
              @click="slots.splice(idx, 1)"
            >
              <i class="bi bi-x"></i>
            </button>
          </li>
          <li v-if="!slots.length" class="list-group-item text-muted">
            No slots added yet.
          </li>
        </ul>

        <button class="btn btn-primary btn-sm" @click="saveAvailability">
          <i class="bi bi-save me-1"></i> Save Availability
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

const API_BASE = "http://127.0.0.1:5000/api";

export default {
  data() {
    return {
      doctor: null,
      appointments: [],
      selectedAppointmentId: null,
      treatment: {
        diagnosis: "",
        prescription: "",
        notes: "",
        next_visit_date: ""
      },
      msg: null,
      slots: [],
      availForm: {
        date: "",
        start: "",
        end: ""
      }
    };
  },
  computed: {
    currentAppointment() {
      return this.appointments.find(
        (a) => a.id === this.selectedAppointmentId
      );
    }
  },
  methods: {
    getAuthConfig() {
      const token =
        localStorage.getItem("hms_token") ||
        localStorage.getItem("access_token") ||
        localStorage.getItem("jwt");

      console.log("DoctorDashboard token:", token);
      if (!token) return {};

      return {
        headers: {
          Authorization: `Bearer ${token}`
        }
      };
    },

    async loadDashboard() {
      try {
        const res = await axios.get(
          `${API_BASE}/doctor/dashboard`,
          this.getAuthConfig()
        );
        this.doctor = res.data.doctor;
      } catch (err) {
        console.error("Error loading dashboard:", err.response?.data || err);
        const msg =
          err?.response?.data?.message ||
          err?.response?.data?.msg ||
          "Dashboard load failed";
        alert("Doctor dashboard couldn't load: " + msg);
      }
    },

    async loadAppointments() {
      try {
        const res = await axios.get(
          `${API_BASE}/doctor/appointments`,
          this.getAuthConfig()
        );
        this.appointments = res.data;
      } catch (err) {
        console.error("Error loading appointments:", err.response?.data || err);
      }
    },

    selectAppointment(a) {
      this.selectedAppointmentId = a.id;
      this.treatment = {
        diagnosis: "",
        prescription: "",
        notes: "",
        next_visit_date: ""
      };
      this.msg = null;
    },

    async updateStatus(a) {
      try {
        await axios.patch(
          `${API_BASE}/doctor/appointments/${a.id}/status`,
          { status: a.status },
          this.getAuthConfig()
        );
      } catch (err) {
        console.error("Error updating status:", err.response?.data || err);
        alert("Status update failed");
      }
    },

    async saveTreatment() {
      if (!this.currentAppointment) return;
      try {
        await axios.post(
          `${API_BASE}/doctor/appointments/${this.currentAppointment.id}/treatment`,
          this.treatment,
          this.getAuthConfig()
        );
        this.msg = "Treatment saved.";
        this.loadAppointments();
      } catch (err) {
        console.error("Error saving treatment:", err.response?.data || err);
        alert("Treatment save failed");
      }
    },

    addSlot() {
      if (!this.availForm.date || !this.availForm.start || !this.availForm.end) {
        alert("Date, start and end should be filled");
        return;
      }

      this.slots.push({
        date: this.availForm.date,
        start: this.availForm.start,
        end: this.availForm.end,
        start_time: this.availForm.start,
        end_time: this.availForm.end
      });

      this.availForm = { date: "", start: "", end: "" };
    },

    async loadAvailability() {
      try {
        const res = await axios.get(
          `${API_BASE}/doctor/availability`,
          this.getAuthConfig()
        );
        console.log("GET /doctor/availability:", res.data);

        this.slots = (res.data || []).map((s) => ({
          date: s.date,
          start: s.start_time || s.start,
          end: s.end_time || s.end,
          start_time: s.start_time || s.start,
          end_time: s.end_time || s.end
        }));
      } catch (err) {
        console.error("Error loading availability:", err.response?.data || err);
        const msg =
          err?.response?.data?.message ||
          err?.response?.data?.msg ||
          err.message;
        alert("Availability load fail: " + msg);
      }
    },

    async saveAvailability() {
      try {
        const payloadSlots = this.slots.map((s) => ({
          date: s.date,
          start_time: s.start_time || s.start,
          end_time: s.end_time || s.end
        }));

        console.log("POST /doctor/availability payload:", { slots: payloadSlots });

        const res = await axios.post(
          `${API_BASE}/doctor/availability`,
          { slots: payloadSlots },
          this.getAuthConfig()
        );
        console.log("POST /doctor/availability response:", res.data);

        alert("Availability saved ");
        await this.loadAvailability();
      } catch (err) {
        console.error("Error saving availability:", err.response?.data || err);
        const msg =
          err?.response?.data?.message ||
          err?.response?.data?.msg ||
          JSON.stringify(err?.response?.data || err.message);
        alert("Failed to save availability: " + msg);
      }
    }
  },
  mounted() {
    this.loadDashboard();
    this.loadAppointments();
    this.loadAvailability();
  }
};
</script>