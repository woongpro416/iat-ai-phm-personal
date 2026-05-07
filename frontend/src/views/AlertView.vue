<script setup>
import { onMounted, ref } from 'vue'
import { alertApi } from '../api/alertApi'

const alerts = ref([])
const loading = ref(false)
const errorMessage = ref('')

const loadAlerts = async () => {
  loading.value = true
  errorMessage.value = ''

  try {
    const response = await alertApi.getAlerts()
    alerts.value = response.data
  } catch (error) {
    errorMessage.value = '알림 목록을 불러오지 못했습니다.'
    console.error(error)
  } finally {
    loading.value = false
  }
}

const checkAlert = async (alertId) => {
  errorMessage.value = ''

  try {
    await alertApi.checkAlert(alertId)
    await loadAlerts()
  } catch (error) {
    errorMessage.value = '알림 확인 처리에 실패했습니다.'
    console.error(error)
  }
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
  loadAlerts()
})
</script>

<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="fw-bold mb-1">알림 관리</h2>
        <p class="text-muted mb-0">장비 위험 및 안전 이벤트 알림을 확인합니다.</p>
      </div>

      <button class="btn btn-outline-primary" @click="loadAlerts">
        새로고침
      </button>
    </div>

    <div v-if="errorMessage" class="alert alert-danger">
      {{ errorMessage }}
    </div>

    <div class="card shadow-sm">
      <div class="card-header fw-bold">알림 목록</div>

      <div class="card-body">
        <div v-if="loading" class="alert alert-info mb-0">
          알림을 불러오는 중입니다.
        </div>

        <div v-else-if="alerts.length === 0" class="text-muted">
          등록된 알림이 없습니다.
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover align-middle">
            <thead>
              <tr>
                <th>ID</th>
                <th>장비</th>
                <th>유형</th>
                <th>심각도</th>
                <th>메시지</th>
                <th>확인 상태</th>
                <th>발생 시간</th>
                <th>처리</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="alert in alerts" :key="alert.alertId">
                <td>{{ alert.alertId }}</td>
                <td>{{ alert.deviceName ?? '-' }}</td>
                <td>{{ alert.alertType }}</td>
                <td>
                  <span class="badge" :class="severityBadgeClass(alert.severity)">
                    {{ alert.severity }}
                  </span>
                </td>
                <td>{{ alert.message }}</td>
                <td>
                  <span class="badge" :class="alert.checked ? 'bg-success' : 'bg-secondary'">
                    {{ alert.checked ? '확인 완료' : '미확인' }}
                  </span>
                </td>
                <td>{{ formatDate(alert.createdAt) }}</td>
                <td>
                  <button
                    class="btn btn-sm btn-outline-success"
                    :disabled="alert.checked"
                    @click="checkAlert(alert.alertId)"
                  >
                    확인
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>
