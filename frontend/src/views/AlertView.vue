<script setup>
import { computed, onMounted, ref } from "vue";
import { alertApi } from "../api/alertApi";
import {
  alertTypeLabel,
  readableDeviceName,
  readableAlertMessage,
  severityLabel,
} from "../utils/displayLabels";

const alerts = ref([]);
const loading = ref(false);
const processingAlertId = ref(null);
const activeTab = ref("unchecked");
const errorMessage = ref("");
const toastMessage = ref("");
const showToast = ref(false);
const selectedAlert = ref(null);

const uncheckedAlerts = computed(() => {
  return alerts.value.filter((alert) => !alert.checked);
});

const checkedAlerts = computed(() => {
  return alerts.value.filter((alert) => alert.checked);
});

const visibleAlerts = computed(() => {
  return activeTab.value === "unchecked" ? uncheckedAlerts.value : checkedAlerts.value;
});

const openToast = (message) => {
  toastMessage.value = message;
  showToast.value = true;

  window.setTimeout(() => {
    showToast.value = false;
  }, 2500);
};

const loadAlerts = async () => {
  loading.value = true;
  errorMessage.value = "";

  try {
    const response = await alertApi.getAlerts();
    alerts.value = response.data;
  } catch (error) {
    errorMessage.value = "알림 목록을 불러오지 못했습니다.";
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const checkAlert = async (alertId) => {
  errorMessage.value = "";
  processingAlertId.value = alertId;

  try {
    await alertApi.checkAlert(alertId);
    await loadAlerts();
    openToast(`알림 #${alertId} 확인 처리가 완료되었습니다.`);
  } catch (error) {
    errorMessage.value = "알림 확인 처리에 실패했습니다.";
    console.error(error);
  } finally {
    processingAlertId.value = null;
  }
};

const checkSelectedAlert = async () => {
  if (!selectedAlert.value) return;

  const alertId = selectedAlert.value.alertId;
  await checkAlert(alertId);

  if (!errorMessage.value) {
    closeAlertDetail();
  }
};

const openAlertDetail = (alert) => {
  selectedAlert.value = alert;
};

const closeAlertDetail = () => {
  selectedAlert.value = null;
};

const severityBadgeClass = (severity) => {
  if (severity === "CRITICAL") return "bg-danger";
  if (severity === "WARNING") return "bg-warning text-dark";
  if (severity === "INFO") return "bg-info text-dark";
  return "bg-secondary";
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

onMounted(() => {
  loadAlerts();
});
</script>

<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="fw-bold mb-1">알림 관리</h2>
        <p class="text-muted mb-0">
          장비 이상과 안전 이벤트 알림을 확인하고 처리 상태를 관리합니다.
        </p>
      </div>

      <button class="btn btn-outline-primary" @click="loadAlerts">
        새로고침
      </button>
    </div>

    <div v-if="errorMessage" class="alert alert-danger">
      {{ errorMessage }}
    </div>

    <div class="card shadow-sm">
      <div class="card-header d-flex justify-content-between align-items-center">
        <span class="fw-bold">알림 목록</span>

        <div class="btn-group btn-group-sm">
          <button
            class="btn"
            :class="activeTab === 'unchecked' ? 'btn-dark' : 'btn-outline-dark'"
            @click="activeTab = 'unchecked'"
          >
            미확인 {{ uncheckedAlerts.length }}
          </button>

          <button
            class="btn"
            :class="activeTab === 'checked' ? 'btn-dark' : 'btn-outline-dark'"
            @click="activeTab = 'checked'"
          >
            확인 완료 {{ checkedAlerts.length }}
          </button>
        </div>
      </div>

      <div class="card-body">
        <div v-if="loading" class="alert alert-info mb-0">
          알림을 불러오는 중입니다.
        </div>

        <div v-else-if="visibleAlerts.length === 0" class="text-muted py-3">
          {{ activeTab === "unchecked" ? "미확인 알림이 없습니다." : "확인 완료된 알림이 없습니다." }}
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover align-middle alert-table">
            <thead>
              <tr>
                <th class="col-id">번호</th>
                <th class="col-device">장비</th>
                <th class="col-type">알림 유형</th>
                <th class="col-severity">중요도</th>
                <th>내용</th>
                <th class="col-status">확인 상태</th>
                <th class="col-time">발생 시간</th>
                <th class="col-action">처리</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="alert in visibleAlerts" :key="alert.alertId">
                <td class="text-muted">#{{ alert.alertId }}</td>
                <td class="device-cell">{{ readableDeviceName(alert.deviceName) }}</td>
                <td>{{ alertTypeLabel(alert.alertType) }}</td>
                <td>
                  <span class="badge" :class="severityBadgeClass(alert.severity)">
                    {{ severityLabel(alert.severity) }}
                  </span>
                </td>
                <td class="message-cell">{{ readableAlertMessage(alert) }}</td>
                <td>
                  <span class="badge" :class="alert.checked ? 'bg-success' : 'bg-secondary'">
                    {{ alert.checked ? "확인 완료" : "미확인" }}
                  </span>
                </td>
                <td class="time-cell">
                  <span>{{ formatDateParts(alert.createdAt).date }}</span>
                  <small>{{ formatDateParts(alert.createdAt).time }}</small>
                </td>
                <td class="action-cell">
                  <button
                    class="btn btn-sm action-button btn-detail me-1"
                    @click="openAlertDetail(alert)"
                  >
                    상세
                  </button>
                  <button
                    class="btn btn-sm action-button"
                    :class="alert.checked ? 'btn-complete' : 'btn-check-soft'"
                    :disabled="alert.checked || processingAlertId === alert.alertId"
                    @click="checkAlert(alert.alertId)"
                  >
                    {{ alert.checked ? "완료" : processingAlertId === alert.alertId ? "처리 중..." : "확인" }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div
      v-if="selectedAlert"
      class="modal-backdrop-custom"
      role="presentation"
      @click.self="closeAlertDetail"
    >
      <div class="modal-dialog-custom" role="dialog" aria-modal="true" aria-labelledby="alert-detail-title">
        <div class="modal-header-custom">
          <div>
            <h5 id="alert-detail-title" class="fw-bold mb-1">
              알림 #{{ selectedAlert.alertId }}
            </h5>
            <p class="text-muted mb-0">
              {{ readableDeviceName(selectedAlert.deviceName) }}
            </p>
          </div>

          <button
            type="button"
            class="btn-close"
            aria-label="닫기"
            @click="closeAlertDetail"
          ></button>
        </div>

        <div class="modal-body-custom">
          <div class="detail-grid mb-3">
            <div>
              <span class="detail-label">알림 유형</span>
              <strong>{{ alertTypeLabel(selectedAlert.alertType) }}</strong>
            </div>
            <div>
              <span class="detail-label">중요도</span>
              <span class="badge" :class="severityBadgeClass(selectedAlert.severity)">
                {{ severityLabel(selectedAlert.severity) }}
              </span>
            </div>
            <div>
              <span class="detail-label">확인 상태</span>
              <span class="badge" :class="selectedAlert.checked ? 'bg-success' : 'bg-secondary'">
                {{ selectedAlert.checked ? "확인 완료" : "미확인" }}
              </span>
            </div>
            <div>
              <span class="detail-label">발생 시간</span>
              <strong>{{ formatDate(selectedAlert.createdAt) }}</strong>
            </div>
          </div>

          <div class="mb-3">
            <span class="detail-label">운영자 메시지</span>
            <p class="mb-0">{{ readableAlertMessage(selectedAlert) }}</p>
          </div>

          <div class="mb-3">
            <span class="detail-label">원본 메시지</span>
            <p class="raw-message mb-0">{{ selectedAlert.message || "-" }}</p>
          </div>

          <div>
            <span class="detail-label">확인 시간</span>
            <p class="mb-0">{{ formatDate(selectedAlert.checkedAt) }}</p>
          </div>
        </div>

        <div class="modal-footer-custom">
          <button class="btn btn-outline-secondary" @click="closeAlertDetail">
            닫기
          </button>
          <button
            class="btn btn-success"
            :disabled="selectedAlert.checked || processingAlertId === selectedAlert.alertId"
            @click="checkSelectedAlert"
          >
            {{ selectedAlert.checked ? "확인 완료" : "확인 처리" }}
          </button>
        </div>
      </div>
    </div>

    <div
      class="toast-container position-fixed bottom-0 end-0 p-3"
      style="z-index: 1080"
    >
      <div
        v-if="showToast"
        class="toast show"
        role="status"
        aria-live="polite"
        aria-atomic="true"
      >
        <div class="toast-header">
          <strong class="me-auto">알림 처리</strong>
          <button
            type="button"
            class="btn-close"
            aria-label="닫기"
            @click="showToast = false"
          ></button>
        </div>
        <div class="toast-body">
          {{ toastMessage }}
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.alert-table {
  font-size: 0.9rem;
}

.alert-table th,
.alert-table td {
  vertical-align: middle;
}

.col-id {
  width: 72px;
}

.col-device {
  width: 110px;
}

.col-type {
  width: 160px;
}

.col-severity {
  width: 100px;
}

.col-status {
  width: 110px;
}

.col-time {
  width: 170px;
}

.col-action {
  width: 150px;
}

.device-cell {
  min-width: 96px;
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
  white-space: nowrap;
}

.action-button {
  min-width: 64px;
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

.btn-check-soft {
  border: 1px solid rgba(118, 87, 168, 0.36);
  color: #5e4785;
  background: rgba(118, 87, 168, 0.1);
}

.btn-check-soft:hover {
  border-color: #7657a8;
  color: #fff;
  background: #7657a8;
}

.btn-complete,
.btn-complete:disabled {
  border-color: #167c72;
  color: #fff;
  background: #167c72;
  opacity: 0.86;
}

.message-cell {
  min-width: 280px;
  max-width: 520px;
  line-height: 1.45;
  word-break: keep-all;
  overflow-wrap: anywhere;
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
  width: min(760px, 100%);
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

.raw-message {
  padding: 12px;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  background: #f8f9fa;
  word-break: keep-all;
  overflow-wrap: anywhere;
}

@media (max-width: 768px) {
  .detail-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
