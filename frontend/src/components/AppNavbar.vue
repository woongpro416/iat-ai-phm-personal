<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container">
      <RouterLink class="navbar-brand fw-bold" to="/dashboard">
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
      </div>
    </div>
  </nav>
</template>