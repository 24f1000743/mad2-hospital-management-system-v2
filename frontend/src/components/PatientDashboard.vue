<template>
  <div>
    <h4 class="mb-3">Patient Dashboard</h4>

    <div class="row">
      <!-- LEFT COLUMN: Departments + Doctors -->
      <div class="col-lg-6">
        <!-- Departments -->
        <div class="card mb-3">
          <div class="card-header">Departments</div>
          <div class="card-body">
            <div v-if="departments.length === 0" class="text-muted">
              No departments yet.
            </div>
            <ul v-else class="list-group">
              <li
                v-for="d in departments"
                :key="d.id"
                class="list-group-item"
              >
                {{ d.name }}
              </li>
            </ul>
          </div>
        </div>

        <!-- Doctors -->
        <div class="card mb-3">
          <div class="card-header">Doctors</div>
          <div class="card-body">
            <input
              class="form-control mb-2"
              v-model="search"
              placeholder="Search doctor"
              @input="loadDoctors"
            />

            <div v-if="doctors.length === 0" class="text-muted">
              No doctors found.
            </div>

            <table v-else class="table table-sm">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Specialization</th>
                  <th>Department</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="d in doctors" :key="d.id">
                  <td>{{ d.full_name }}</td>
                  <td>{{ d.specialization }}</td>
                  <td>{{ d.department || "-" }}</td>
                  <td>
                    <button
                      class="btn btn-sm btn-outline-primary"
                      @click="selectDoctor(d)"
                    >
                      Select
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>

            <div v-if="selectedDoctor" class="mt-2 small text-muted">
              Selected doctor: <strong>{{ selectedDoctor.full_name }}</strong>
            </div>
          </div>
        </div>
      </div>

      <!-- RIGHT COLUMN: Booking + Appointments + History -->
      <div class="col-lg-6">
        <!-- Book Appointment -->
        <div class="card mb-3">
          <div class="card-header">Book Appointment</div>
          <div class="card-body">
            <div v-if="!selectedDoctor" class="text-muted">
              Select a doctor on the left to view available slots and book.
            </div>

            <div v-else>
              <div class="mb-2">
                <strong>{{ selectedDoctor.full_name }}</strong>
                <div class="small text-muted">
                  {{ selectedDoctor.specialization }}
                </div>
              </div>

              <div class="mb-2 small text-muted" v-if="loadingSlots">
                Loading availability...
              </div>

              <div v-if="slots.length === 0 && !loadingSlots" class="text-muted mb-2">
                No availability slots defined for this doctor.
              </div>

              <div v-else-if="slots.length > 0">
                <label class="form-label small">Available Slots</label>
                <select
                  class="form-select form-select-sm mb-2"
                  v-model="selectedSlotId"
                >
                  <option
                    v-for="s in slots"
                    :key="s.id"
                    :value="s.id"
                  >
                    {{ s.date }} | {{ s.start_time }} - {{ s.end_time }}
                  </option>
                </select>
              </div>

              <button
                class="btn btn-primary btn-sm"
                :disabled="!selectedSlotId || bookingLoading"
                @click="bookSelectedSlot"
              >
                <span v-if="bookingLoading">Booking...</span>
                <span v-else>Book Appointment</span>
              </button>

              <div v-if="bookingMessage" class="alert alert-success mt-2 py-2 small">
                {{ bookingMessage }}
              </div>
              <div v-if="bookingError" class="alert alert-danger mt-2 py-2 small">
                {{ bookingError }}
              </div>
            </div>
          </div>
        </div>

        <!-- Upcoming Appointments -->
        <div class="card mb-3">
          <div class="card-header">Upcoming Appointments</div>
          <div class="card-body">
            <div v-if="upcoming.length === 0" class="text-muted">
              No upcoming appointments.
            </div>
            <table v-else class="table table-sm">
              <thead>
                <tr>
                  <th>Doctor</th>
                  <th>Date</th>
                  <th>Time</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="a in upcoming" :key="a.id">
                  <td>{{ a.doctor }}</td>
                  <td>{{ a.date }}</td>
                  <td>{{ a.time }}</td>
                  <td>{{ a.status }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Treatment History -->
        <div class="card">
          <div class="card-header">Treatment History</div>
          <div class="card-body">
            <div v-if="history.length === 0" class="text-muted">
              No history yet.
            </div>
            <table v-else class="table table-sm">
              <thead>
                <tr>
                  <th>Doctor</th>
                  <th>Date</th>
                  <th>Diagnosis</th>
                  <th>Prescription</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="h in history" :key="h.id">
                  <td>{{ h.doctor }}</td>
                  <td>{{ h.date }}</td>
                  <td>{{ h.diagnosis }}</td>
                  <td>{{ h.prescription }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import api from "../api";

export default {
  data() {
    return {
      departments: [],
      doctors: [],
      upcoming: [],
      history: [],
      search: "",

      selectedDoctor: null,
      slots: [],
      selectedSlotId: null,
      loadingSlots: false,
      bookingLoading: false,
      bookingMessage: null,
      bookingError: null,
    };
  },

  methods: {
    async loadDashboard() {
      const res = await api.get("/patient/dashboard");

      this.departments = res.data.departments || [];
      this.doctors = res.data.doctors || [];
      this.upcoming = res.data.upcoming_appointments || [];
      this.history = res.data.history || [];
    },

    async loadDoctors() {
      const res = await api.get("/patient/doctors", {
        params: { search: this.search },
      });
      this.doctors = res.data;
    },

    async selectDoctor(doctor) {
      this.selectedDoctor = doctor;
      this.bookingMessage = null;
      this.bookingError = null;
      this.selectedSlotId = null;
      this.slots = [];
      await this.loadDoctorAvailability(doctor.id);
    },

    async loadDoctorAvailability(doctorId) {
      this.loadingSlots = true;
      try {
        const res = await api.get(`/patient/doctors/${doctorId}/availability`);
        this.slots = res.data || [];
        if (this.slots.length > 0) {
          this.selectedSlotId = this.slots[0].id;
        }
      } catch (err) {
        console.error(err);
        this.bookingError = "Failed to load availability.";
      } finally {
        this.loadingSlots = false;
      }
    },

    async bookSelectedSlot() {
      if (!this.selectedDoctor || !this.selectedSlotId) {
        this.bookingError = "Select a doctor and a slot first.";
        return;
      }

      const slot = this.slots.find((s) => s.id === this.selectedSlotId);
      if (!slot) {
        this.bookingError = "Selected slot not found.";
        return;
      }

      this.bookingLoading = true;
      this.bookingMessage = null;
      this.bookingError = null;

      try {
        await api.post("/patient/appointments", {
          doctor_id: this.selectedDoctor.id,
          date: slot.date,
          time: slot.start_time,
        });

        this.bookingMessage = "Appointment booked successfully.";
        await this.loadDashboard(); // refresh upcoming & history
        await this.loadDoctorAvailability(this.selectedDoctor.id); // keep slots fresh
      } catch (err) {
        console.error(err);
        const msg =
          err?.response?.data?.message || "Failed to book appointment.";
        this.bookingError = msg;
      } finally {
        this.bookingLoading = false;
      }
    },
  },

  mounted() {
    this.loadDashboard();
  },
};
</script>