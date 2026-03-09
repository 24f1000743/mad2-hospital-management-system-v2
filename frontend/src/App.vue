<template>
  <div class="h-100 app-bg">
    <!-- Top navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm">
      <div class="container">
        <a class="navbar-brand fw-semibold" href="#">
          <i class="bi bi-hospital me-2"></i>
          Hospital Management System - V2
        </a>

        <div class="ms-auto d-flex align-items-center" v-if="token">
          <span class="badge bg-light text-dark me-2 text-uppercase">
            {{ role }}
          </span>
          <button
            class="btn btn-outline-light btn-sm"
            type="button"
            @click="logout"
          >
            <i class="bi bi-box-arrow-right me-1"></i>
            Logout
          </button>
        </div>
      </div>
    </nav>

    <!-- Main area -->
    <div class="container py-4">
      <div v-if="!token">
        <LoginRegister @login-success="onLoginSuccess" />
      </div>

      <div v-else>
        <div class="row">
          
          <div class="col-md-3 mb-3 d-none d-md-block">
            <div class="card border-0 shadow-sm">
              <div class="card-header bg-white fw-semibold">
                <i class="bi bi-grid-3x3-gap me-1"></i> Menu
              </div>
              <div class="list-group list-group-flush small">
                <button
                  class="list-group-item list-group-item-action"
                  disabled
                >
                  <i class="bi bi-speedometer2 me-1"></i>
                  Dashboard
                </button>
                <button
                  class="list-group-item list-group-item-action"
                  disabled
                  v-if="role === 'admin'"
                >
                  <i class="bi bi-person-badge me-1"></i> Doctors
                </button>
                <button
                  class="list-group-item list-group-item-action"
                  disabled
                  v-if="role === 'admin'"
                >
                  <i class="bi bi-people me-1"></i> Patients
                </button>
                <button
                  class="list-group-item list-group-item-action"
                  disabled
                  v-if="role !== 'admin'"
                >
                  <i class="bi bi-calendar-check me-1"></i> Appointments
                </button>
                <button
                  class="list-group-item list-group-item-action"
                  disabled
                  v-if="role === 'patient'"
                >
                  <i class="bi bi-file-earmark-medical me-1"></i> History
                </button>
              </div>
            </div>
          </div>

          <div class="col-md-9">
            <AdminDashboard v-if="role === 'admin'" />
            <DoctorDashboard v-else-if="role === 'doctor'" />
            <PatientDashboard v-else />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import LoginRegister from "./components/LoginRegister.vue";
import AdminDashboard from "./components/AdminDashboard.vue";
import DoctorDashboard from "./components/DoctorDashboard.vue";
import PatientDashboard from "./components/PatientDashboard.vue";

export default {
  components: {
    LoginRegister,
    AdminDashboard,
    DoctorDashboard,
    PatientDashboard
  },
  data() {
    return {
      token: localStorage.getItem("hms_token") || null,
      role: localStorage.getItem("hms_role") || null
    };
  },
  methods: {
    onLoginSuccess(payload) {
      this.token = payload.token;
      this.role = payload.role;
      localStorage.setItem("hms_token", payload.token);
      localStorage.setItem("hms_role", payload.role);
    },
    logout() {
      this.token = null;
      this.role = null;
      localStorage.removeItem("hms_token");
      localStorage.removeItem("hms_role");
    }
  }
};
</script>

<style>
html,
body,
#app {
  height: 100%;
}
.app-bg {
  min-height: 100%;
  background: linear-gradient(
      135deg,
      rgba(13, 110, 253, 0.04),
      rgba(32, 201, 151, 0.04)
    ),
    #f8fafc;
}
</style>