<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h4 class="mb-0">Admin Dashboard</h4>
      <span class="text-muted small">Hospital Management System - V2</span>
    </div>

    <!-- Tabs -->
    <ul class="nav nav-pills mb-3">
      <li class="nav-item" v-for="tab in tabs" :key="tab.key">
        <button
          class="nav-link"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          <i :class="tab.icon" class="me-1"></i>
          {{ tab.label }}
        </button>
      </li>
    </ul>

    <!-- Toasts -->
    <div
      v-if="success"
      class="alert alert-success py-2 d-flex justify-content-between align-items-center"
    >
      <span>{{ success }}</span>
      <button
        type="button"
        class="btn-close btn-close-white"
        @click="success = null"
      ></button>
    </div>
    <div
      v-if="error"
      class="alert alert-danger py-2 d-flex justify-content-between align-items-center"
    >
      <span>{{ error }}</span>
      <button
        type="button"
        class="btn-close btn-close-white"
        @click="error = null"
      ></button>
    </div>

    <!-- Overview tab -->
    <div v-if="activeTab === 'overview'">
      <div class="row mb-3">
        <div class="col-md-4">
          <div class="card stat-card border-0 shadow-sm">
            <div class="card-body d-flex align-items-center">
              <div
                class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center me-3"
                style="width: 48px; height: 48px"
              >
                <i class="bi bi-person-badge"></i>
              </div>
              <div>
                <div class="text-muted small">Doctors</div>
                <div class="h4 mb-0">{{ stats?.doctors ?? "-" }}</div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-md-4">
          <div class="card stat-card border-0 shadow-sm">
            <div class="card-body d-flex align-items-center">
              <div
                class="rounded-circle bg-success text-white d-flex align-items-center justify-content-center me-3"
                style="width: 48px; height: 48px"
              >
                <i class="bi bi-people"></i>
              </div>
              <div>
                <div class="text-muted small">Patients</div>
                <div class="h4 mb-0">{{ stats?.patients ?? "-" }}</div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-md-4">
          <div class="card stat-card border-0 shadow-sm">
            <div class="card-body d-flex align-items-center">
              <div
                class="rounded-circle bg-info text-white d-flex align-items-center justify-content-center me-3"
                style="width: 48px; height: 48px"
              >
                <i class="bi bi-calendar-check"></i>
              </div>
              <div>
                <div class="text-muted small">Appointments</div>
                <div class="h4 mb-0">{{ stats?.appointments ?? "-" }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Upcoming preview -->
      <div class="card border-0 shadow-sm">
        <div class="card-header bg-white">
          <i class="bi bi-clock-history me-1"></i> Upcoming Appointments (top 5)
        </div>
        <div class="card-body p-0">
          <div v-if="loading" class="text-center py-4">
            <div class="spinner-border spinner-border-sm"></div>
          </div>
          <table v-else class="table table-sm mb-0">
            <thead>
              <tr>
                <th>ID</th>
                <th>Doctor</th>
                <th>Patient</th>
                <th>Date</th>
                <th>Time</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="a in previewAppointments" :key="a.id">
                <td>#{{ a.id }}</td>
                <td>{{ a.doctor }}</td>
                <td>{{ a.patient }}</td>
                <td>{{ a.date }}</td>
                <td>{{ a.time }}</td>
                <td>
                  <span class="badge" :class="statusClass(a.status)">{{
                    a.status
                  }}</span>
                </td>
              </tr>
              <tr v-if="!previewAppointments.length">
                <td colspan="6" class="text-muted text-center py-3">
                  No upcoming appointments.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Doctors tab -->
    <div v-if="activeTab === 'doctors'">
      <div class="card border-0 shadow-sm">
        <div
          class="card-header bg-white d-flex justify-content-between align-items-center"
        >
          <div>
            <i class="bi bi-person-badge me-1"></i> Registered Doctors
          </div>
          <div class="d-flex gap-2">
            <input
              class="form-control form-control-sm"
              v-model="doctorSearch"
              placeholder="Search by name"
              @input="loadDoctors"
            />
            <button
              class="btn btn-sm btn-outline-primary"
              @click="activeTab = 'addDoctor'"
            >
              <i class="bi bi-plus-lg me-1"></i> Add Doctor
            </button>
          </div>
        </div>
        <div class="card-body p-0">
          <div v-if="loadingDoctors" class="text-center py-4">
            <div class="spinner-border spinner-border-sm"></div>
          </div>
          <table v-else class="table table-hover table-sm mb-0">
            <thead class="table-light">
              <tr>
                <th>Name</th>
                <th>Username</th>
                <th>Spec.</th>
                <th>Dept.</th>
                <th style="width: 80px">Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="d in doctors" :key="d.id">
                <td>{{ d.full_name }}</td>
                <td>{{ d.username }}</td>
                <td>{{ d.specialization }}</td>
                <td>{{ d.department || "-" }}</td>
                <td class="text-end">
                  <button
                    class="btn btn-sm btn-outline-danger"
                    title="Deactivate doctor"
                    @click="deactivateDoctor(d.id)"
                  >
                    <i class="bi bi-trash"></i>
                  </button>
                </td>
              </tr>
              <tr v-if="!doctors.length">
                <td colspan="5" class="text-muted text-center py-3">
                  No doctors found.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Patients tab -->
    <div v-if="activeTab === 'patients'">
      <div class="card border-0 shadow-sm">
        <div
          class="card-header bg-white d-flex justify-content-between align-items-center"
        >
          <span><i class="bi bi-people me-1"></i> Registered Patients</span>
          <input
            class="form-control form-control-sm w-auto"
            v-model="patientSearch"
            placeholder="Search by name / phone"
            @input="loadPatients"
          />
        </div>
        <div class="card-body p-0">
          <div v-if="loadingPatients" class="text-center py-4">
            <div class="spinner-border spinner-border-sm"></div>
          </div>
          <table v-else class="table table-hover table-sm mb-0">
            <thead class="table-light">
              <tr>
                <th>Name</th>
                <th>Phone</th>
                <th>Username</th>
                <th style="width: 80px">Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="p in patients" :key="p.id">
                <td>{{ p.full_name }}</td>
                <td>{{ p.phone }}</td>
                <td>{{ p.username }}</td>
                <td class="text-end">
                  <button
                    class="btn btn-sm btn-outline-danger"
                    title="Deactivate patient"
                    @click="deactivatePatient(p.id)"
                  >
                    <i class="bi bi-trash"></i>
                  </button>
                </td>
              </tr>
              <tr v-if="!patients.length">
                <td colspan="4" class="text-muted text-center py-3">
                  No patients found.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Appointments tab -->
    <div v-if="activeTab === 'appointments'">
      <div class="card border-0 shadow-sm">
        <div class="card-header bg-white">
          <i class="bi bi-calendar-week me-1"></i> All Appointments
        </div>
        <div class="card-body p-0">
          <div v-if="loadingAppointments" class="text-center py-4">
            <div class="spinner-border spinner-border-sm"></div>
          </div>
          <table v-else class="table table-hover table-sm mb-0">
            <thead class="table-light">
              <tr>
                <th>ID</th>
                <th>Doctor</th>
                <th>Patient</th>
                <th>Date</th>
                <th>Time</th>
                <th>Status</th>
                <th style="width: 150px">Update</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="a in appointments" :key="a.id">
                <td>#{{ a.id }}</td>
                <td>{{ a.doctor }}</td>
                <td>{{ a.patient }}</td>
                <td>{{ a.date }}</td>
                <td>{{ a.time }}</td>
                <td>
                  <span class="badge" :class="statusClass(a.status)">{{
                    a.status
                  }}</span>
                </td>
                <td>
                  <select
                    class="form-select form-select-sm"
                    v-model="a.status"
                    @change="updateAppointmentStatus(a)"
                  >
                    <option>Booked</option>
                    <option>Completed</option>
                    <option>Cancelled</option>
                  </select>
                </td>
              </tr>
              <tr v-if="!appointments.length">
                <td colspan="7" class="text-muted text-center py-3">
                  No appointments.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Add Doctor tab -->
    <div v-if="activeTab === 'addDoctor'">
      <div class="card border-0 shadow-sm">
        <div class="card-header bg-white">
          <i class="bi bi-plus-lg me-1"></i> Add a New Doctor
        </div>
        <div class="card-body">
          <form class="row g-3" @submit.prevent="addDoctor">
            <div class="col-md-4">
              <label class="form-label">Username</label>
              <input
                v-model="newDoctor.username"
                class="form-control"
                required
              />
            </div>
            <div class="col-md-4">
              <label class="form-label">Password</label>
              <input
                v-model="newDoctor.password"
                type="password"
                class="form-control"
                required
              />
            </div>
            <div class="col-md-4">
              <label class="form-label">Full Name</label>
              <input
                v-model="newDoctor.full_name"
                class="form-control"
                required
              />
            </div>
            <div class="col-md-4">
              <label class="form-label">Specialization</label>
              <input
                v-model="newDoctor.specialization"
                class="form-control"
                required
              />
            </div>
            <div class="col-md-4">
              <label class="form-label">Department</label>
              <input
                v-model="newDoctor.department_name"
                class="form-control"
                placeholder="eg. Cardiology"
              />
            </div>
            <div class="col-md-12">
              <label class="form-label">Bio</label>
              <textarea
                v-model="newDoctor.bio"
                class="form-control"
                rows="2"
                placeholder="Short description about the doctor"
              ></textarea>
            </div>
            <div class="col-12 d-flex justify-content-end">
              <button class="btn btn-success" :disabled="addingDoctor">
                <span
                  v-if="addingDoctor"
                  class="spinner-border spinner-border-sm me-2"
                ></span>
                Add Doctor
              </button>
            </div>
          </form>
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
      tabs: [
        { key: "overview", label: "Overview", icon: "bi bi-speedometer2" },
        { key: "doctors", label: "Doctors", icon: "bi bi-person-badge" },
        { key: "patients", label: "Patients", icon: "bi bi-people" },
        { key: "appointments", label: "Appointments", icon: "bi bi-calendar3" },
        { key: "addDoctor", label: "Add Doctor", icon: "bi bi-plus-lg" }
      ],
      activeTab: "overview",
      stats: null,
      previewAppointments: [],
      doctors: [],
      patients: [],
      appointments: [],
      doctorSearch: "",
      patientSearch: "",
      loading: false,
      loadingDoctors: false,
      loadingPatients: false,
      loadingAppointments: false,
      addingDoctor: false,
      newDoctor: {
        username: "",
        password: "",
        full_name: "",
        specialization: "",
        department_name: "",
        bio: ""
      },
      error: null,
      success: null
    };
  },
  methods: {
    statusClass(status) {
      if (status === "Booked") return "bg-primary";
      if (status === "Completed") return "bg-success";
      if (status === "Cancelled") return "bg-secondary";
      return "bg-light text-dark";
    },
    async loadDashboard() {
      this.loading = true;
      try {
        const res = await api.get("/admin/dashboard");
        this.stats = res.data.stats;
        this.previewAppointments = res.data.upcoming_appointments || [];
      } finally {
        this.loading = false;
      }
    },
    async loadDoctors() {
      this.loadingDoctors = true;
      try {
        const res = await api.get("/admin/doctors", {
          params: { search: this.doctorSearch }
        });
        this.doctors = res.data;
      } finally {
        this.loadingDoctors = false;
      }
    },
    async loadPatients() {
      this.loadingPatients = true;
      try {
        const res = await api.get("/admin/patients", {
          params: { search: this.patientSearch }
        });
        this.patients = res.data;
      } finally {
        this.loadingPatients = false;
      }
    },
    async loadAppointments() {
      this.loadingAppointments = true;
      try {
        const res = await api.get("/admin/appointments");
        this.appointments = res.data;
      } finally {
        this.loadingAppointments = false;
      }
    },
    async addDoctor() {
      this.error = null;
      this.success = null;
      this.addingDoctor = true;
      try {
        const res = await api.post("/admin/doctors", this.newDoctor);
        this.success = res.data.message || "Doctor added successfully";
        this.newDoctor = {
          username: "",
          password: "",
          full_name: "",
          specialization: "",
          department_name: "",
          bio: ""
        };
        this.loadDoctors();
        this.loadDashboard();
      } catch (e) {
        console.error(e);
        this.error =
          e.response?.data?.message || "Error adding doctor, please try again.";
      } finally {
        this.addingDoctor = false;
      }
    },
    async updateAppointmentStatus(appt) {
      try {
        await api.patch(`/admin/appointments/${appt.id}`, {
          status: appt.status
        });
      } catch (e) {
        this.error =
          e.response?.data?.message || "Failed to update appointment status.";
      }
    },
    async deactivateDoctor(id) {
      if (!confirm("Deactivate this doctor?")) return;
      this.error = null;
      this.success = null;
      try {
        // yahi endpoint use karna jo tumne admin_routes me add kiya tha:
        await api.patch(`/admin/doctors/${id}/deactivate`);
        this.success = "Doctor removed.";
        this.loadDoctors();
        this.loadDashboard();
      } catch (e) {
        console.error(e);
        this.error =
          e.response?.data?.message || "Failed to remove doctor.";
      }
    },
    async deactivatePatient(id) {
      if (!confirm("Deactivate this patient?")) return;
      this.error = null;
      this.success = null;
      try {
        await api.patch(`/admin/patients/${id}/deactivate`);
        this.success = "Patient removed.";
        this.loadPatients();
        this.loadDashboard();
      } catch (e) {
        console.error(e);
        this.error =
          e.response?.data?.message || "Failed to remove patient.";
      }
    }
  },
  mounted() {
    this.loadDashboard();
    this.loadDoctors();
    this.loadPatients();
    this.loadAppointments();
  }
};
</script>

<style scoped>
.stat-card {
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.08);
}
</style>