<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { deviceApi } from '../api/deviceApi'

const devices = ref([])
const statusLogs = ref([])
const selectedDeviceId = ref('')

const loading = ref(false)
const savingDevice = ref(false)
const savingStatus = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const deviceForm = reactive({
  deviceName: '',
  deviceType: 'AUTONOMOUS_SHUTTLE',
  location: '',
})

const statusForm = reactive({
  temperature: '',
  vibration: '',
  noise: '',
})

const selectedDevice = computed(() => {
  return devices.value.find((device) => device.deviceId === Number(selectedDeviceId.value))
})

const loadDevices = async () => {
  const response = await deviceApi.getDevices()
  devices.value = response.data

  if (!selectedDeviceId.value && devices.value.length > 0) {
    selectedDeviceId.value = devices.value[0].deviceId
  }
}

const loadStatusLogs = async () => {
  if (!selectedDeviceId.value) {
    statusLogs.value = []
    return
  }

  const response = await deviceApi.getDeviceStatusLogs(selectedDeviceId.value)
  statusLogs.value = response.data
}

const loadPage = async () => {
  loading.value = true
  errorMessage.value = ''

  try {
    await loadDevices()
    await loadStatusLogs()
  } catch (error) {
    errorMessage.value = '장비 상태 데이터를 불러오지 못했습니다.'
    console.error(error)
  } finally {
    loading.value = false
  }
}

const createDevice = async () => {
  savingDevice.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    await deviceApi.createDevice({ ...deviceForm })

    deviceForm.deviceName = ''
    deviceForm.deviceType = 'AUTONOMOUS_SHUTTLE'
    deviceForm.location = ''

    successMessage.value = '장비가 등록되었습니다.'
    await loadDevices()
  } catch (error) {
    errorMessage.value = '장비 등록에 실패했습니다.'
    console.error(error)
  } finally {
    savingDevice.value = false
  }
}

const createStatusLog = async () => {
  if (!selectedDeviceId.value) return

  savingStatus.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    await deviceApi.createDeviceStatus({
      deviceId: Number(selectedDeviceId.value),
      temperature: Number(statusForm.temperature),
      vibration: Number(statusForm.vibration),
      noise: Number(statusForm.noise),
    })

    statusForm.temperature = ''
    statusForm.vibration = ''
    statusForm.noise = ''

    successMessage.value = '장비 상태 로그가 등록되었습니다.'
    await loadDevices()
    await loadStatusLogs()
  } catch (error) {
    errorMessage.value = '장비 상태 로그 등록에 실패했습니다.'
    console.error(error)
  } finally {
    savingStatus.value = false
  }
}

const changeDevice = async () => {
  errorMessage.value = ''

  try {
    await loadStatusLogs()
  } catch (error) {
    errorMessage.value = '장비 상태 로그를 불러오지 못했습니다.'
    console.error(error)
  }
}

const statusBadgeClass = (status) => {
  if (status === 'NORMAL') return 'bg-success'
  if (status === 'WARNING') return 'bg-warning text-dark'
  if (status === 'DANGER') return 'bg-danger'
  if (status === 'OFFLINE') return 'bg-secondary'
  return 'bg-light text-dark'
}

const formatDate = (dateText) => {
  if (!dateText) return '-'
  return dateText.replace('T', ' ').slice(0, 19)
}

onMounted(() => {
  loadPage()
})
</script>


<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="fw-bold mb-1">장비 상태 모니터링</h2>
        <p class="text-muted mb-0">장비 등록, 센서 상태 입력, 위험도 분석 결과를 관리합니다.</p>
      </div>

      <button class="btn btn-outline-primary" @click="loadPage">
        새로고침
      </button>
    </div>

    <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>
    <div v-if="successMessage" class="alert alert-success">{{ successMessage }}</div>

    <div class="row g-4 mb-4">
      <div class="col-lg-5">
        <div class="card shadow-sm h-100">
          <div class="card-header fw-bold">장비 등록</div>
          <div class="card-body">
            <div class="mb-3">
              <label class="form-label">장비명</label>
              <input v-model="deviceForm.deviceName" class="form-control" />
            </div>

            <div class="mb-3">
              <label class="form-label">장비 유형</label>
              <input v-model="deviceForm.deviceType" class="form-control" />
            </div>

            <div class="mb-3">
              <label class="form-label">위치</label>
              <input v-model="deviceForm.location" class="form-control" />
            </div>

            <button
              class="btn btn-primary w-100"
              :disabled="savingDevice"
              @click="createDevice"
            >
              {{ savingDevice ? '등록 중...' : '장비 등록' }}
            </button>
          </div>
        </div>
      </div>

      <div class="col-lg-7">
        <div class="card shadow-sm h-100">
          <div class="card-header fw-bold">상태 로그 등록</div>
          <div class="card-body">
            <div class="mb-3">
              <label class="form-label">장비 선택</label>
              <select v-model="selectedDeviceId" class="form-select" @change="changeDevice">
                <option value="" disabled>장비 선택</option>
                <option v-for="device in devices" :key="device.deviceId" :value="device.deviceId">
                  {{ device.deviceName }} / {{ device.location }}
                </option>
              </select>
            </div>

            <div v-if="selectedDevice" class="mb-3">
              <span class="badge" :class="statusBadgeClass(selectedDevice.status)">
                현재 상태: {{ selectedDevice.status }}
              </span>
            </div>

            <div class="row g-3">
              <div class="col-md-4">
                <label class="form-label">온도</label>
                <input v-model="statusForm.temperature" type="number" class="form-control" />
              </div>

              <div class="col-md-4">
                <label class="form-label">진동</label>
                <input v-model="statusForm.vibration" type="number" step="0.1" class="form-control" />
              </div>

              <div class="col-md-4">
                <label class="form-label">소음</label>
                <input v-model="statusForm.noise" type="number" step="0.1" class="form-control" />
              </div>
            </div>

            <button
              class="btn btn-danger w-100 mt-3"
              :disabled="!selectedDeviceId || savingStatus"
              @click="createStatusLog"
            >
              {{ savingStatus ? '분석 중...' : '위험도 분석 등록' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="card shadow-sm">
      <div class="card-header fw-bold">장비 상태 로그</div>

      <div class="card-body">
        <div v-if="loading" class="alert alert-info mb-0">
          장비 상태 데이터를 불러오는 중입니다.
        </div>

        <div v-else-if="statusLogs.length === 0" class="text-muted">
          선택한 장비의 상태 로그가 없습니다.
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover align-middle">
            <thead>
              <tr>
                <th>ID</th>
                <th>온도</th>
                <th>진동</th>
                <th>소음</th>
                <th>위험도</th>
                <th>상태</th>
                <th>등록 시간</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="log in statusLogs" :key="log.statusId">
                <td>{{ log.statusId }}</td>
                <td>{{ log.temperature }}</td>
                <td>{{ log.vibration }}</td>
                <td>{{ log.noise }}</td>
                <td>{{ log.riskScore }}</td>
                <td>
                  <span class="badge" :class="statusBadgeClass(log.status)">
                    {{ log.status }}
                  </span>
                </td>
                <td>{{ formatDate(log.createdAt) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>
