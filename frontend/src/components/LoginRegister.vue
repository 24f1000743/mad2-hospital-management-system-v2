<template>
  <div class="row justify-content-center">
    <div class="col-lg-5 col-md-7">
      <div class="card border-0 shadow-lg auth-card">
        <div class="card-body p-4 p-md-5">
          <div class="text-center mb-4">
            <div
              class="rounded-circle bg-primary text-white d-inline-flex align-items-center justify-content-center mb-2"
              style="width: 60px; height: 60px"
            >
              <i class="bi bi-person-circle fs-3"></i>
            </div>
            <h5 class="fw-semibold mb-0">
              {{ mode === "login" ? "Login" : "Patient Registration" }}
            </h5>
            <small class="text-muted">
              {{ mode === "login"
                ? "Login as Admin / Doctor / Patient"
                : "Create a patient account" }}
            </small>
          </div>

          <ul class="nav nav-pills nav-fill mb-3 small">
            <li class="nav-item">
              <button
                class="nav-link"
                :class="{ active: mode === 'login' }"
                @click="switchMode('login')"
              >
                <i class="bi bi-box-arrow-in-right me-1"></i> Login
              </button>
            </li>
            <li class="nav-item">
              <button
                class="nav-link"
                :class="{ active: mode === 'register' }"
                @click="switchMode('register')"
              >
                <i class="bi bi-person-plus me-1"></i> Patient Register
              </button>
            </li>
          </ul>

          <form @submit.prevent="submit">
            <div class="mb-3">
              <label class="form-label small">Username</label>
              <input
                v-model="form.username"
                class="form-control"
                required
                autocomplete="username"
              />
            </div>

            <div class="mb-3">
              <label class="form-label small">Password</label>
              <input
                v-model="form.password"
                type="password"
                class="form-control"
                required
                autocomplete="current-password"
              />
            </div>

            <template v-if="mode === 'register'">
              <div class="mb-3">
                <label class="form-label small">Full Name</label>
                <input
                  v-model="form.full_name"
                  class="form-control"
                  required
                />
              </div>
              <div class="mb-3">
                <label class="form-label small">Email</label>
                <input
                  v-model="form.email"
                  type="email"
                  class="form-control"
                />
              </div>
              <div class="mb-3">
                <label class="form-label small">Phone</label>
                <input v-model="form.phone" class="form-control" />
              </div>
            </template>

            <button class="btn btn-primary w-100" type="submit" :disabled="loading">
              <span
                v-if="loading"
                class="spinner-border spinner-border-sm me-2"
              ></span>
              {{ mode === "login" ? "Login" : "Register & Login" }}
            </button>
          </form>

          <div v-if="error" class="alert alert-danger mt-3 py-2 small mb-0">
            {{ error }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from "../api";

export default {
  emits: ["login-success"],
  data() {
    return {
      mode: "login",
      loading: false,
      form: {
        username: "",
        password: "",
        full_name: "",
        email: "",
        phone: ""
      },
      error: null
    };
  },
  methods: {
    switchMode(m) {
      this.mode = m;
      this.error = null;
    },
    async submit() {
      this.error = null;
      this.loading = true;
      try {
        let res;
        if (this.mode === "login") {
          res = await api.post("/auth/login", {
            username: this.form.username,
            password: this.form.password
          });
        } else {
          res = await api.post("/auth/register", this.form);
        }
        this.$emit("login-success", {
          token: res.data.token,
          role: res.data.role
        });
      } catch (e) {
        this.error =
          e.response?.data?.message || "Something went wrong. Try again.";
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.auth-card {
  border-radius: 1rem;
}
</style>