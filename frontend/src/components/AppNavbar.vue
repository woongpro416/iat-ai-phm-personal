<script setup>
import { computed, ref } from 'vue'

const DEMO_WRITE_TOKEN_KEY = 'iatDemoWriteToken'

const tokenInput = ref('')
const storedToken = ref(sessionStorage.getItem(DEMO_WRITE_TOKEN_KEY) || '')

const adminUnlocked = computed(() => storedToken.value.length > 0)

const unlockAdmin = () => {
  const token = tokenInput.value.trim()

  if (!token) {
    return
  }

  sessionStorage.setItem(DEMO_WRITE_TOKEN_KEY, token)
  storedToken.value = token
  tokenInput.value = ''
}

const lockAdmin = () => {
  sessionStorage.removeItem(DEMO_WRITE_TOKEN_KEY)
  storedToken.value = ''
  tokenInput.value = ''
}
</script>

<template>
  <nav class="navbar navbar-expand-lg app-navbar">
    <div class="container-fluid app-navbar-inner">
      <RouterLink class="navbar-brand fw-bold" to="/">
        IAT AI Safety
      </RouterLink>

      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarNav"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <div id="navbarNav" class="collapse navbar-collapse">
        <ul class="navbar-nav ms-auto">
          <li class="nav-item">
            <RouterLink class="nav-link" to="/">홈</RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink class="nav-link" to="/dashboard">대시보드</RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink class="nav-link" to="/safety-events">안전 이벤트</RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink class="nav-link" to="/alerts">알림</RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink class="nav-link" to="/device-status">장비 상태</RouterLink>
          </li>
        </ul>

        <form class="admin-unlock" @submit.prevent="unlockAdmin">
          <span
            class="admin-state"
            :class="adminUnlocked ? 'is-unlocked' : 'is-locked'"
          >
            {{ adminUnlocked ? 'Admin' : 'Read only' }}
          </span>

          <input
            v-if="!adminUnlocked"
            v-model="tokenInput"
            class="form-control form-control-sm admin-token-input"
            type="password"
            autocomplete="off"
            placeholder="Write token"
            aria-label="Demo write token"
          />

          <button
            v-if="!adminUnlocked"
            class="btn btn-sm btn-outline-light admin-button"
            type="submit"
          >
            Unlock
          </button>

          <button
            v-else
            class="btn btn-sm btn-outline-light admin-button"
            type="button"
            @click="lockAdmin"
          >
            Lock
          </button>
        </form>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.admin-unlock {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: 18px;
  padding-left: 18px;
  border-left: 1px solid rgba(255, 255, 255, 0.18);
}

.admin-state {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 74px;
  height: 28px;
  padding: 0 10px;
  border: 1px solid rgba(255, 255, 255, 0.22);
  border-radius: 6px;
  font-size: 0.76rem;
  font-weight: 700;
  white-space: nowrap;
}

.admin-state.is-unlocked {
  color: #052e16;
  background: #bbf7d0;
  border-color: #86efac;
}

.admin-state.is-locked {
  color: #f8fafc;
  background: rgba(255, 255, 255, 0.08);
}

.admin-token-input {
  width: 150px;
  min-height: 30px;
}

.admin-button {
  min-width: 64px;
  min-height: 30px;
  font-weight: 700;
}

@media (max-width: 991.98px) {
  .admin-unlock {
    align-items: stretch;
    margin: 12px 0 0;
    padding: 12px 0 0;
    border-left: 0;
    border-top: 1px solid rgba(255, 255, 255, 0.18);
  }

  .admin-token-input {
    width: min(100%, 220px);
  }
}
</style>
