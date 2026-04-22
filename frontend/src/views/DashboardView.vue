<script setup>
import { onMounted, reactive, ref } from 'vue'
import { dashboardApi } from '../api/dashboardApi'

const loading = ref(false)
const errorMessage = ref('')

const summary = reactive({
  totalDevices: 0,
  normalDevices: 0,
  warningDevices: 0,
  dangerDevices: 0,
  offlineDevices: 0,
  totalSafetyEvents: 0,
  unresolvedSafetyEvents: 0,
  totalAlerts: 0,
  uncheckedAlerts: 0,
  latestRiskScore: null,
  latestDeviceStatus: null,
})

const recent = reactive({
  recentAlerts: [],
  recentSafetyEvents: [],
  recentDeviceStatuses: [],
})

const loadDashboard = async () => {
  loading.value = true
  errorMessage.value = ''

  try {
    const [summaryResponse, recentResponse] = await Promise.all([
      dashboardApi.getSummary(),
      dashboardApi.getRecent(),
    ])

    Object.assign(summary, summaryResponse.data)
    Object.assign(recent, recentResponse.data)
  } catch (error) {
    errorMessage.value = '대시보드 데이터를 불러오지 못했습니다.'
    console.error(error)
  } finally {
    loading.value = false
  }
}

const statusBadgeClass = (status) => {
  if (status === 'NORMAL') return 'bg-success'
  if (status === 'WARNING') return 'bg-warning text-dark'
  if (status === 'DANGER') return 'bg-danger'
  if (status === 'OFFLINE') return 'bg-secondary'
  return 'bg-light text-dark'
}

const severityBadgeClass = (severity) => {
  if (severity === 'CRITICAL') return 'bg-danger'
  if (severity === 'WARNING') return 'bg-warning text-dark'
  if (severity === 'INFO') return 'bg-info text-dark'
  return 'bg-secondary'
}

const formatDate = (dateText) => {
  if (!dateText) return '-'
  return dateText.replace('T', ' ').slice(0, 19)
}

onMounted(() => {
  loadDashboard()
})
</script>

<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="fw-bold mb-1">AI 무인 셔틀 관제 대시보드</h2>
        <p class="text-muted mb-0">
          장비 상태, YOLO 안전 이벤트, 알림 현황을 통합 조회합니다.
        </p>
      </div>

      <button class="btn btn-primary" @click="loadDashboard">
        새로고침
      </button>
    </div>

    <div v-if="loading" class="alert alert-info">
      대시보드 데이터를 불러오는 중입니다.
    </div>

    <div v-else>
      <div class="row g-3 mb-4">
        <div class="col-md-3">
          <div class="card shadow-sm">
            <div class="card-body">
              <p class="text-muted mb-1">전체 장비</p>
              <h3 class="fw-bold mb-0">{{ summary.totalDevices }}</h3>
            </div>
          </div>
        </div>

        <div class="col-md-3">
          <div class="card shadow-sm">
            <div class="card-body">
              <p class="text-muted mb-1">주의 장비</p>
              <h3 class="fw-bold text-warning mb-0">{{ summary.warningDevices }}</h3>
            </div>
          </div>
        </div>

        <div class="col-md-3">
          <div class="card shadow-sm">
            <div class="card-body">
              <p class="text-muted mb-1">위험 장비</p>
              <h3 class="fw-bold text-danger mb-0">{{ summary.dangerDevices }}</h3>
            </div>
          </div>
        </div>

        <div class="col-md-3">
          <div class="card shadow-sm">
            <div class="card-body">
              <p class="text-muted mb-1">미확인 알림</p>
              <h3 class="fw-bold mb-0">{{ summary.uncheckedAlerts }}</h3>
            </div>
          </div>
        </div>
      </div>

      <div class="row g-3 mb-4">
        <div class="col-md-4">
          <div class="card shadow-sm">
            <div class="card-body">
              <p class="text-muted mb-1">최근 위험도</p>
              <h3 class="fw-bold mb-0">
                {{ summary.latestRiskScore ?? '-' }}
              </h3>
              <span class="badge mt-2" :class="statusBadgeClass(summary.latestDeviceStatus)">
                {{ summary.latestDeviceStatus ?? 'NO DATA' }}
              </span>
            </div>
          </div>
        </div>

        <div class="col-md-4">
          <div class="card shadow-sm">
            <div class="card-body">
              <p class="text-muted mb-1">전체 안전 이벤트</p>
              <h3 class="fw-bold mb-0">{{ summary.totalSafetyEvents }}</h3>
            </div>
          </div>
        </div>

        <div class="col-md-4">
          <div class="card shadow-sm">
            <div class="card-body">
              <p class="text-muted mb-1">미처리 안전 이벤트</p>
              <h3 class="fw-bold text-danger mb-0">{{ summary.unresolvedSafetyEvents }}</h3>
            </div>
          </div>
        </div>
      </div>

      <div class="row g-3">
        <div class="col-lg-6">
          <div class="card shadow-sm h-100">
            <div class="card-header fw-bold">최근 알림</div>
            <div class="card-body">
              <div v-if="recent.recentAlerts.length === 0" class="text-muted">
                최근 알림이 없습니다.
              </div>

              <div
                v-for="alert in recent.recentAlerts"
                :key="alert.alertId"
                class="border-bottom pb-2 mb-2"
              >
                <div class="d-flex justify-content-between">
                  <strong>{{ alert.alertType }}</strong>
                  <span class="badge" :class="severityBadgeClass(alert.severity)">
                    {{ alert.severity }}
                  </span>
                </div>
                <p class="mb-1 small">{{ alert.message }}</p>
                <small class="text-muted">{{ formatDate(alert.createdAt) }}</small>
              </div>
            </div>
          </div>
        </div>

        <div class="col-lg-6">
          <div class="card shadow-sm h-100">
            <div class="card-header fw-bold">최근 안전 이벤트</div>
            <div class="card-body">
              <div v-if="recent.recentSafetyEvents.length === 0" class="text-muted">
                최근 안전 이벤트가 없습니다.
              </div>

              <div
                v-for="event in recent.recentSafetyEvents"
                :key="event.eventId"
                class="border-bottom pb-3 mb-3"
              >
                <div class="d-flex justify-content-between">
                  <strong>{{ event.eventType }}</strong>
                  <span class="badge" :class="event.resolved ? 'bg-success' : 'bg-danger'">
                    {{ event.resolved ? '처리 완료' : '미처리' }}
                  </span>
                </div>

                <p class="mb-1 small">{{ event.message }}</p>
                <p class="mb-1 small text-muted">
                  신뢰도: {{ event.confidence }}
                </p>

                <img
                  v-if="event.imageUrl"
                  :src="event.imageUrl"
                  class="img-fluid rounded border mt-2"
                  style="max-height: 180px; object-fit: cover;"
                  alt="탐지 이미지"
                />

                <div>
                  <small class="text-muted">{{ formatDate(event.createdAt) }}</small>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-12">
          <div class="card shadow-sm">
            <div class="card-header fw-bold">최근 장비 상태 로그</div>
            <div class="card-body table-responsive">
              <table class="table table-hover align-middle">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>장비 ID</th>
                    <th>온도</th>
                    <th>진동</th>
                    <th>소음</th>
                    <th>위험도</th>
                    <th>상태</th>
                    <th>시간</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="status in recent.recentDeviceStatuses"
                    :key="status.statusId"
                  >
                    <td>{{ status.statusId }}</td>
                    <td>{{ status.deviceId }}</td>
                    <td>{{ status.temperature }}</td>
                    <td>{{ status.vibration }}</td>
                    <td>{{ status.noise }}</td>
                    <td>{{ status.riskScore }}</td>
                    <td>
                      <span class="badge" :class="statusBadgeClass(status.status)">
                        {{ status.status }}
                      </span>
                    </td>
                    <td>{{ formatDate(status.createdAt) }}</td>
                  </tr>
                </tbody>
              </table>

              <div
                v-if="recent.recentDeviceStatuses.length === 0"
                class="text-muted"
              >
                최근 장비 상태 로그가 없습니다.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="errorMessage" class="alert alert-danger mt-4">
      {{ errorMessage }}
    </div>
  </div>
</template>

