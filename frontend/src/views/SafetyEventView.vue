<script setup>
import { computed, onMounted, ref } from 'vue'
import { deviceApi } from '../api/deviceApi'
import { safetyEventApi } from '../api/safetyEventApi'

const devices = ref([])
const events = ref([])

const selectedDeviceId = ref('')
const selectedFile = ref(null)
const previewUrl = ref('')

const loading = ref(false)
const uploading = ref(false)
const errorMessage = ref('')

const canUpload = computed(() => {
  return selectedDeviceId.value && selectedFile.value
})

const loadDevices = async () => {
  const response = await deviceApi.getDevices()
  devices.value = response.data

  if (!selectedDeviceId.value && devices.value.length > 0) {
    selectedDeviceId.value = devices.value[0].deviceId
  }
}

const loadEvents = async () => {
  const response = await safetyEventApi.getSafetyEvents()
  events.value = response.data
}

const loadPage = async () => {
  loading.value = true
  errorMessage.value = ''

  try {
    await Promise.all([
      loadDevices(),
      loadEvents(),
    ])
  } catch (error) {
    errorMessage.value = '안전 이벤트 데이터를 불러오지 못했습니다.'
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleFileChange = (event) => {
  const file = event.target.files?.[0]
  selectedFile.value = file || null

  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
  }

  previewUrl.value = file ? URL.createObjectURL(file) : ''
}

const uploadImage = async () => {
  if (!canUpload.value) return

  uploading.value = true
  errorMessage.value = ''

  try {
    await safetyEventApi.uploadSafetyImage(selectedDeviceId.value, selectedFile.value)

    selectedFile.value = null
    previewUrl.value = ''

    await loadEvents()
  } catch (error) {
    errorMessage.value = '이미지 업로드 또는 YOLO 탐지 처리에 실패했습니다.'
    console.error(error)
  } finally {
    uploading.value = false
  }
}

const resolveEvent = async (eventId) => {
  errorMessage.value = ''

  try {
    await safetyEventApi.resolveSafetyEvent(eventId)
    await loadEvents()
  } catch (error) {
    errorMessage.value = '안전 이벤트 처리 완료에 실패했습니다.'
    console.error(error)
  }
}

const formatDate = (dateText) => {
  if (!dateText) return '-'
  return dateText.replace('T', ' ').slice(0, 19)
}

const resolvedBadgeClass = (resolved) => {
  return resolved ? 'bg-success' : 'bg-danger'
}

onMounted(() => {
  loadPage()
})
</script>

<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="fw-bold mb-1">안전 이벤트 관제</h2>
        <p class="text-muted mb-0">
          YOLO 이미지 탐지 결과와 안전 이벤트 이력을 관리합니다.
        </p>
      </div>

      <button class="btn btn-outline-primary" @click="loadPage">
        새로고침
      </button>
    </div>

    <div v-if="errorMessage" class="alert alert-danger">
      {{ errorMessage }}
    </div>

    <div class="card shadow-sm mb-4">
      <div class="card-header fw-bold">이미지 기반 안전 이벤트 등록</div>

      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-4">
            <label class="form-label">장비</label>
            <select v-model="selectedDeviceId" class="form-select">
              <option value="" disabled>장비 선택</option>
              <option
                v-for="device in devices"
                :key="device.deviceId"
                :value="device.deviceId"
              >
                {{ device.deviceName }} / {{ device.location }}
              </option>
            </select>
          </div>

          <div class="col-md-5">
            <label class="form-label">이미지 파일</label>
            <input
              class="form-control"
              type="file"
              accept="image/*"
              @change="handleFileChange"
            />
          </div>

          <div class="col-md-3 d-flex align-items-end">
            <button
              class="btn btn-primary w-100"
              :disabled="!canUpload || uploading"
              @click="uploadImage"
            >
              {{ uploading ? '탐지 중...' : 'YOLO 탐지 실행' }}
            </button>
          </div>
        </div>

        <div v-if="previewUrl" class="mt-3">
          <p class="text-muted mb-2">업로드 이미지 미리보기</p>
          <img
            :src="previewUrl"
            class="img-fluid rounded border"
            style="max-height: 260px;"
            alt="업로드 이미지 미리보기"
          />
        </div>
      </div>
    </div>

    <div class="card shadow-sm">
      <div class="card-header fw-bold">안전 이벤트 목록</div>

      <div class="card-body">
        <div v-if="loading" class="alert alert-info mb-0">
          안전 이벤트를 불러오는 중입니다.
        </div>

        <div v-else-if="events.length === 0" class="text-muted">
          등록된 안전 이벤트가 없습니다.
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover align-middle">
            <thead>
              <tr>
                <th>ID</th>
                <th>장비</th>
                <th>유형</th>
                <th>신뢰도</th>
                <th>상태</th>
                <th>이미지</th>
                <th>발생 시간</th>
                <th>처리</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="event in events" :key="event.eventId">
                <td>{{ event.eventId }}</td>
                <td>{{ event.deviceName }}</td>
                <td>{{ event.eventType }}</td>
                <td>{{ event.confidence }}</td>
                <td>
                  <span class="badge" :class="resolvedBadgeClass(event.resolved)">
                    {{ event.resolved ? '처리 완료' : '미처리' }}
                  </span>
                </td>
                <td>
                  <img
                    v-if="event.imageUrl"
                    :src="event.imageUrl"
                    class="rounded border"
                    style="width: 96px; height: 64px; object-fit: cover;"
                    alt="안전 이벤트 이미지"
                  />
                  <span v-else class="text-muted">-</span>
                </td>
                <td>{{ formatDate(event.createdAt) }}</td>
                <td>
                  <button
                    class="btn btn-sm btn-outline-success"
                    :disabled="event.resolved"
                    @click="resolveEvent(event.eventId)"
                  >
                    처리 완료
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
