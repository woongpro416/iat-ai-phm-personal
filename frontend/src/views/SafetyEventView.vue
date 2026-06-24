<script setup>
import { computed, onMounted, ref } from "vue";
import { deviceApi } from "../api/deviceApi";
import { safetyEventApi } from "../api/safetyEventApi";
import {
  eventTypeLabel,
  readableDeviceName,
  readableSafetyEventMessage,
} from "../utils/displayLabels";

const devices = ref([]);
const events = ref([]);

const selectedDeviceId = ref("");
const selectedFile = ref(null);
const previewUrl = ref("");

const loading = ref(false);
const uploading = ref(false);
const errorMessage = ref("");
const selectedEvent = ref(null);

const canUpload = computed(() => {
  return selectedDeviceId.value && selectedFile.value;
});

const loadDevices = async () => {
  const response = await deviceApi.getDevices();
  devices.value = response.data;

  if (!selectedDeviceId.value && devices.value.length > 0) {
    selectedDeviceId.value = devices.value[0].deviceId;
  }
};

const loadEvents = async () => {
  const response = await safetyEventApi.getSafetyEvents();
  events.value = response.data;
};

const loadPage = async () => {
  loading.value = true;
  errorMessage.value = "";

  try {
    await Promise.all([
      loadDevices(),
      loadEvents(),
    ]);
  } catch (error) {
    errorMessage.value = "안전 이벤트 데이터를 불러오지 못했습니다.";
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const handleFileChange = (event) => {
  const file = event.target.files?.[0];

  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value);
    previewUrl.value = "";
  }

  errorMessage.value = "";
  selectedFile.value = null;

  if (!file) {
    return;
  }

  if (!file.type.startsWith("image/")) {
    errorMessage.value = "이미지 파일만 업로드할 수 있습니다.";
    event.target.value = "";
    return;
  }

  if (file.size === 0) {
    errorMessage.value = "빈 이미지 파일은 업로드할 수 없습니다.";
    event.target.value = "";
    return;
  }

  selectedFile.value = file;
  previewUrl.value = URL.createObjectURL(file);
};

const uploadImage = async () => {
  if (!canUpload.value) return;

  uploading.value = true;
  errorMessage.value = "";

  try {
    await safetyEventApi.uploadSafetyImage(selectedDeviceId.value, selectedFile.value);

    selectedFile.value = null;
    previewUrl.value = "";

    await loadEvents();
  } catch (error) {
    errorMessage.value = "이미지 업로드 또는 AI 탐지 처리에 실패했습니다.";
    console.error(error);
  } finally {
    uploading.value = false;
  }
};

const resolveEvent = async (eventId) => {
  errorMessage.value = "";

  try {
    await safetyEventApi.resolveSafetyEvent(eventId);
    await loadEvents();
  } catch (error) {
    errorMessage.value = "안전 이벤트 처리 완료에 실패했습니다.";
    console.error(error);
  }
};

const resolveSelectedEvent = async () => {
  if (!selectedEvent.value) return;

  const eventId = selectedEvent.value.eventId;
  await resolveEvent(eventId);

  if (!errorMessage.value) {
    closeEventDetail();
  }
};

const openEventDetail = (event) => {
  selectedEvent.value = event;
};

const closeEventDetail = () => {
  selectedEvent.value = null;
};

const detectionSummaryLines = (event) => {
  if (!event?.detectionSummary) return ["탐지 상세 정보가 없습니다."];

  return event.detectionSummary
    .split("\n")
    .filter(Boolean);
};

const formatDate = (dateText) => {
  if (!dateText) return "-";
  return dateText.replace("T", " ").slice(0, 19);
};

const formatDateParts = (dateText) => {
  const formatted = formatDate(dateText);
  if (formatted === "-") {
    return {
      date: "-",
      time: "",
    };
  }

  const [date, time] = formatted.split(" ");
  return {
    date,
    time,
  };
};

const resolvedBadgeClass = (resolved) => {
  return resolved ? "bg-success" : "bg-danger";
};

const eventImages = (event) => {
  return [
    {
      label: "원본",
      url: event.imageUrl,
    },
    {
      label: "분석",
      url: event.resultImageUrl,
    },
  ].filter((image) => image.url);
};

onMounted(() => {
  loadPage();
});
</script>

<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="fw-bold mb-1">안전 이벤트 관리</h2>
        <p class="text-muted mb-0">
          AI 이미지 탐지 결과와 승객 안전 이벤트 이력을 관리합니다.
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
            <label class="form-label">대상 장비</label>
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
            <label class="form-label">분석 이미지</label>
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
              {{ uploading ? "AI 분석 중..." : "AI 안전 분석 실행" }}
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
          <table class="table table-hover align-middle safety-event-table">
            <thead>
              <tr>
                <th>번호</th>
                <th>장비</th>
                <th>이벤트 유형</th>
                <th>신뢰도</th>
                <th>내용</th>
                <th>처리 상태</th>
                <th>이미지</th>
                <th>발생 시간</th>
                <th>처리</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="event in events" :key="event.eventId">
                <td class="text-muted">#{{ event.eventId }}</td>
                <td class="device-cell">{{ readableDeviceName(event.deviceName) }}</td>
                <td class="event-type-cell">{{ eventTypeLabel(event.eventType) }}</td>
                <td>{{ event.confidence }}</td>
                <td class="event-message-cell">{{ readableSafetyEventMessage(event) }}</td>
                <td class="status-cell">
                  <span class="badge" :class="resolvedBadgeClass(event.resolved)">
                    {{ event.resolved ? "처리 완료" : "미처리" }}
                  </span>
                </td>
                <td class="image-cell">
                  <div v-if="eventImages(event).length" class="event-image-list">
                    <a
                      v-for="image in eventImages(event)"
                      :key="`${event.eventId}-${image.label}`"
                      :href="image.url"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="event-image-link"
                      :title="`${image.label} 이미지 새 창으로 보기`"
                    >
                      <img
                        :src="image.url"
                        class="event-image-thumb"
                        :alt="`${image.label} 안전 이벤트 이미지`"
                      />
                      <span class="event-image-label">{{ image.label }}</span>
                    </a>
                  </div>
                  <span v-else class="text-muted">-</span>
                </td>
                <td class="time-cell">
                  <span>{{ formatDateParts(event.createdAt).date }}</span>
                  <small>{{ formatDateParts(event.createdAt).time }}</small>
                </td>
                <td class="action-cell">
                  <button
                    class="btn btn-sm action-button btn-detail me-1"
                    @click="openEventDetail(event)"
                  >
                    상세
                  </button>
                  <button
                    class="btn btn-sm action-button"
                    :class="event.resolved ? 'btn-complete' : 'btn-resolve'"
                    :disabled="event.resolved"
                    @click="resolveEvent(event.eventId)"
                  >
                    {{ event.resolved ? "완료됨" : "처리 완료" }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div
      v-if="selectedEvent"
      class="modal-backdrop-custom"
      role="presentation"
      @click.self="closeEventDetail"
    >
      <div class="modal-dialog-custom" role="dialog" aria-modal="true" aria-labelledby="event-detail-title">
        <div class="modal-header-custom">
          <div>
            <h5 id="event-detail-title" class="fw-bold mb-1">
              안전 이벤트 #{{ selectedEvent.eventId }}
            </h5>
            <p class="text-muted mb-0">
              {{ readableDeviceName(selectedEvent.deviceName) }} / {{ formatDate(selectedEvent.createdAt) }}
            </p>
          </div>

          <button
            type="button"
            class="btn-close"
            aria-label="닫기"
            @click="closeEventDetail"
          ></button>
        </div>

        <div class="modal-body-custom">
          <div class="detail-grid mb-3">
            <div>
              <span class="detail-label">이벤트 유형</span>
              <strong>{{ eventTypeLabel(selectedEvent.eventType) }}</strong>
            </div>
            <div>
              <span class="detail-label">신뢰도</span>
              <strong>{{ selectedEvent.confidence }}</strong>
            </div>
            <div>
              <span class="detail-label">처리 상태</span>
              <span class="badge" :class="resolvedBadgeClass(selectedEvent.resolved)">
                {{ selectedEvent.resolved ? "처리 완료" : "미처리" }}
              </span>
            </div>
            <div>
              <span class="detail-label">처리 시간</span>
              <strong>{{ formatDate(selectedEvent.resolvedAt) }}</strong>
            </div>
          </div>

          <div class="mb-3">
            <span class="detail-label">원본 메시지</span>
            <p class="mb-0">{{ selectedEvent.message || "-" }}</p>
          </div>

          <div class="row g-3 mb-3">
            <div
              v-for="image in eventImages(selectedEvent)"
              :key="`detail-${image.label}`"
              class="col-md-6"
            >
              <span class="detail-label">{{ image.label }} 이미지</span>
              <a :href="image.url" target="_blank" rel="noopener noreferrer">
                <img
                  :src="image.url"
                  class="detail-image"
                  :alt="`${image.label} 안전 이벤트 이미지`"
                />
              </a>
            </div>
          </div>

          <div>
            <span class="detail-label">탐지 상세</span>
            <ul class="detection-list">
              <li
                v-for="line in detectionSummaryLines(selectedEvent)"
                :key="line"
              >
                {{ line }}
              </li>
            </ul>
          </div>
        </div>

        <div class="modal-footer-custom">
          <button class="btn btn-outline-secondary" @click="closeEventDetail">
            닫기
          </button>
          <button
            class="btn btn-success"
            :disabled="selectedEvent.resolved"
            @click="resolveSelectedEvent"
          >
            {{ selectedEvent.resolved ? "완료됨" : "처리 완료" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.safety-event-table th {
  white-space: nowrap;
}

.status-cell,
.action-cell {
  white-space: nowrap;
}

.device-cell {
  min-width: 96px;
  white-space: nowrap;
  font-weight: 700;
}

.event-type-cell {
  min-width: 128px;
  white-space: nowrap;
  font-weight: 700;
}

.time-cell {
  min-width: 116px;
  white-space: nowrap;
  line-height: 1.2;
}

.time-cell span,
.time-cell small {
  display: block;
}

.time-cell small {
  margin-top: 3px;
  color: #6c757d;
}

.action-cell {
  width: 178px;
}

.action-button {
  min-width: 70px;
  border-radius: 999px;
  font-weight: 800;
}

.btn-detail {
  border: 1px solid rgba(22, 124, 114, 0.42);
  color: #0f5f58;
  background: rgba(22, 124, 114, 0.08);
}

.btn-detail:hover {
  border-color: #167c72;
  color: #fff;
  background: #167c72;
}

.btn-resolve {
  border: 1px solid rgba(212, 147, 31, 0.48);
  color: #8c5f0d;
  background: rgba(212, 147, 31, 0.12);
}

.btn-resolve:hover {
  border-color: #d4931f;
  color: #17201b;
  background: #f1c76f;
}

.btn-complete,
.btn-complete:disabled {
  border-color: #167c72;
  color: #fff;
  background: #167c72;
  opacity: 0.86;
}

.event-message-cell {
  min-width: 280px;
  line-height: 1.45;
  word-break: keep-all;
  overflow-wrap: anywhere;
}

.image-cell {
  min-width: 168px;
}

.event-image-list {
  display: flex;
  gap: 8px;
  align-items: center;
}

.event-image-link {
  display: grid;
  gap: 4px;
  color: inherit;
  text-align: center;
  text-decoration: none;
}

.event-image-thumb {
  width: 72px;
  height: 52px;
  object-fit: cover;
  border: 1px solid #dee2e6;
  border-radius: 4px;
}

.event-image-label {
  font-size: 12px;
  color: #6c757d;
  line-height: 1;
  white-space: nowrap;
}

.modal-backdrop-custom {
  position: fixed;
  inset: 0;
  z-index: 1050;
  display: grid;
  place-items: center;
  padding: 24px;
  background: rgba(33, 37, 41, 0.55);
}

.modal-dialog-custom {
  width: min(920px, 100%);
  max-height: calc(100vh - 48px);
  overflow: auto;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.24);
}

.modal-header-custom,
.modal-footer-custom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 20px;
  border-bottom: 1px solid #dee2e6;
}

.modal-footer-custom {
  justify-content: flex-end;
  border-top: 1px solid #dee2e6;
  border-bottom: 0;
}

.modal-body-custom {
  padding: 20px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.detail-label {
  display: block;
  margin-bottom: 4px;
  color: #6c757d;
  font-size: 0.78rem;
  font-weight: 700;
}

.detail-image {
  width: 100%;
  max-height: 320px;
  object-fit: contain;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  background: #f8f9fa;
}

.detection-list {
  display: grid;
  gap: 6px;
  padding-left: 18px;
  margin-bottom: 0;
  font-family: Consolas, "Courier New", monospace;
  font-size: 0.88rem;
}

@media (max-width: 768px) {
  .detail-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
