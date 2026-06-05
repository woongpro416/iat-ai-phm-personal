<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from "vue";
import { dashboardApi } from "../api/dashboardApi";
import { alertApi } from "../api/alertApi";
import { safetyEventApi } from "../api/safetyEventApi";
import {
  alertTypeLabel,
  deviceStatusLabel,
  eventTypeLabel,
  readableAlertMessage,
  readableSafetyEventMessage,
  severityLabel,
} from "../utils/displayLabels";

const loading = ref(false);
const hasLoaded = ref(false);
const errorMessage = ref("");
const refreshCountdown = ref(10);
const autoRefreshing = ref(false);

let refreshTimer = null;

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
});

const recent = reactive({
  recentAlerts: [],
  recentSafetyEvents: [],
  recentDeviceStatuses: [],
});

const riskChartLogs = computed(() => {
  return [...recent.recentDeviceStatuses].reverse();
});

const riskChartPoints = computed(() => {
  const logs = riskChartLogs.value;
  const width = 360;
  const height = 120;
  const padding = 12;

  if (logs.length === 0) {
    return "";
  }

  if (logs.length === 1) {
    const x = width / 2;
    const y =
      height - padding - ((logs[0].riskScore ?? 0) / 100) * (height - padding * 2);
    return `${x},${y}`;
  }

  return logs
    .map((log, index) => {
      const riskScore = log.riskScore ?? 0;
      const x = padding + (index * (width - padding * 2)) / (logs.length - 1);
      const y = height - padding - (riskScore / 100) * (height - padding * 2);

      return `${x},${y}`;
    })
    .join(" ");
});

const deviceStatusChart = computed(() => {
  const items = [
    {
      label: deviceStatusLabel("NORMAL"),
      status: "NORMAL",
      count: summary.normalDevices,
      barClass: "bg-success",
    },
    {
      label: deviceStatusLabel("WARNING"),
      status: "WARNING",
      count: summary.warningDevices,
      barClass: "bg-warning",
    },
    {
      label: deviceStatusLabel("DANGER"),
      status: "DANGER",
      count: summary.dangerDevices,
      barClass: "bg-danger",
    },
    {
      label: deviceStatusLabel("OFFLINE"),
      status: "OFFLINE",
      count: summary.offlineDevices,
      barClass: "bg-secondary",
    },
  ];

  const maxCount = Math.max(...items.map((item) => item.count), 1);

  return items.map((item) => ({
    ...item,
    percent: Math.round((item.count / maxCount) * 100),
  }));
});

const loadDashboard = async ({ showLoading = !hasLoaded.value } = {}) => {
  if (showLoading) {
    loading.value = true;
  }

  errorMessage.value = "";

  try {
    const [summaryResponse, recentResponse] = await Promise.all([
      dashboardApi.getSummary(),
      dashboardApi.getRecent(),
    ]);

    Object.assign(summary, summaryResponse.data);
    Object.assign(recent, recentResponse.data);
  } catch (error) {
    errorMessage.value = "대시보드 데이터를 불러오지 못했습니다.";
    console.error(error);
  } finally {
    if (showLoading) {
      loading.value = false;
    }

    hasLoaded.value = true;
  }
};

const reloadDashboard = async () => {
  autoRefreshing.value = false;
  await loadDashboard();
  restartAutoRefresh();
};

const startAutoRefresh = () => {
  stopAutoRefresh();
  refreshCountdown.value = 10;
  autoRefreshing.value = false;

  refreshTimer = window.setInterval(async () => {
    refreshCountdown.value = Math.max(refreshCountdown.value - 1, 0);

    if (refreshCountdown.value === 0) {
      autoRefreshing.value = true;

      try {
        await loadDashboard({ showLoading: false });
      } finally {
        autoRefreshing.value = false;
        refreshCountdown.value = 10;
      }
    }
  }, 1000);
};

const restartAutoRefresh = () => {
  startAutoRefresh();
};

const stopAutoRefresh = () => {
  if (refreshTimer) {
    window.clearInterval(refreshTimer);
    refreshTimer = null;
  }
};

const checkRecentAlert = async (alertId) => {
  errorMessage.value = "";

  try {
    await alertApi.checkAlert(alertId);
    await loadDashboard();
  } catch (error) {
    errorMessage.value = "알림 확인 처리에 실패했습니다.";
    console.error(error);
  }
};

const resolveRecentSafetyEvent = async (eventId) => {
  errorMessage.value = "";

  try {
    await safetyEventApi.resolveSafetyEvent(eventId);
    await loadDashboard();
  } catch (error) {
    errorMessage.value = "안전 이벤트 처리 완료에 실패했습니다.";
    console.error(error);
  }
};

const statusBadgeClass = (status) => {
  if (status === "NORMAL") return "bg-success";
  if (status === "WARNING") return "bg-warning text-dark";
  if (status === "DANGER") return "bg-danger";
  if (status === "OFFLINE") return "bg-secondary";
  return "bg-light text-dark";
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

onMounted(() => {
  loadDashboard();
  startAutoRefresh();
});

onBeforeUnmount(() => {
  stopAutoRefresh();
});
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

      <div class="d-flex align-items-center gap-2">
        <span class="badge bg-light text-dark border">
          {{ autoRefreshing ? "갱신중" : `자동 갱신 ${refreshCountdown}초` }}
        </span>

        <button class="btn btn-primary" @click="reloadDashboard">새로고침</button>
      </div>
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
                {{ summary.latestRiskScore ?? "-" }}
              </h3>
              <span
                class="badge mt-2"
                :class="statusBadgeClass(summary.latestDeviceStatus)"
              >
                {{ deviceStatusLabel(summary.latestDeviceStatus) }}
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
              <h3 class="fw-bold text-danger mb-0">
                {{ summary.unresolvedSafetyEvents }}
              </h3>
            </div>
          </div>
        </div>
      </div>

      <div class="row g-3 mb-4">
        <div class="col-lg-7">
          <div class="card shadow-sm h-100">
            <div class="card-header fw-bold">최근 위험도 변화</div>

            <div class="card-body">
              <div v-if="riskChartLogs.length === 0" class="text-muted">
                표시할 위험도 데이터가 없습니다.
              </div>

              <div v-else>
                <svg viewBox="0 0 360 120" class="w-100" style="height: 180px">
                  <line x1="12" y1="108" x2="348" y2="108" stroke="#dee2e6" />
                  <line x1="12" y1="12" x2="12" y2="108" stroke="#dee2e6" />

                  <line
                    x1="12"
                    y1="60"
                    x2="348"
                    y2="60"
                    stroke="#ffc107"
                    stroke-dasharray="4 4"
                  />
                  <line
                    x1="12"
                    y1="31.2"
                    x2="348"
                    y2="31.2"
                    stroke="#dc3545"
                    stroke-dasharray="4 4"
                  />

                  <polyline
                    :points="riskChartPoints"
                    fill="none"
                    stroke="#0d6efd"
                    stroke-width="3"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />

                  <circle
                    v-for="(log, index) in riskChartLogs"
                    :key="log.statusId"
                    :cx="
                      riskChartLogs.length === 1
                        ? 180
                        : 12 + (index * 336) / (riskChartLogs.length - 1)
                    "
                    :cy="108 - ((log.riskScore ?? 0) / 100) * 96"
                    r="4"
                    fill="#0d6efd"
                  />
                </svg>

                <div class="d-flex justify-content-between small text-muted mt-2">
                  <span>낮음</span>
                  <span>주의 기준 50</span>
                  <span>위험 기준 80</span>
                  <span>높음</span>
                </div>

                <div class="table-responsive mt-3">
                  <table class="table table-sm align-middle mb-0">
                    <thead>
                      <tr>
                        <th>시간</th>
                        <th>위험도</th>
                        <th>상태</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="log in riskChartLogs" :key="`chart-${log.statusId}`">
                        <td>{{ formatDate(log.createdAt) }}</td>
                        <td>{{ log.riskScore }}</td>
                        <td>
                          <span class="badge" :class="statusBadgeClass(log.status)">
                            {{ deviceStatusLabel(log.status) }}
                          </span>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-lg-5">
          <div class="card shadow-sm h-100">
            <div class="card-header fw-bold">상태별 장비 수</div>

            <div class="card-body">
              <div v-if="summary.totalDevices === 0" class="text-muted">
                등록된 장비가 없습니다.
              </div>

              <div v-else class="d-flex flex-column gap-3">
                <div
                  v-for="item in deviceStatusChart"
                  :key="item.status"
                >
                  <div class="d-flex justify-content-between align-items-center mb-1">
                    <span class="fw-semibold">{{ item.label }}</span>
                    <span class="small text-muted">{{ item.count }}대</span>
                  </div>

                  <div
                    class="progress"
                    style="height: 18px"
                    role="progressbar"
                    :aria-label="`${item.label} 장비 수`"
                    :aria-valuenow="item.count"
                    aria-valuemin="0"
                    :aria-valuemax="summary.totalDevices"
                  >
                    <div
                      class="progress-bar"
                      :class="item.barClass"
                      :style="{ width: `${item.percent}%` }"
                    >
                      {{ item.count }}
                    </div>
                  </div>
                </div>

                <div class="border-top pt-3 small text-muted">
                  총 {{ summary.totalDevices }}대 기준 현재 장비 상태 분포입니다.
                </div>
              </div>
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
                  <strong>{{ alertTypeLabel(alert.alertType) }}</strong>
                  <span class="badge" :class="severityBadgeClass(alert.severity)">
                    {{ severityLabel(alert.severity) }}
                  </span>
                </div>
                <p class="mb-1 small">{{ readableAlertMessage(alert) }}</p>
                <small class="text-muted">{{ formatDate(alert.createdAt) }}</small>
                <div class="mt-2">
                  <button
                    class="btn btn-sm btn-outline-success"
                    :disabled="alert.checked"
                    @click="checkRecentAlert(alert.alertId)"
                  >
                    {{ alert.checked ? "확인 완료" : "확인" }}
                  </button>
                </div>
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
                  <strong>{{ eventTypeLabel(event.eventType) }}</strong>
                  <span
                    class="badge"
                    :class="event.resolved ? 'bg-success' : 'bg-danger'"
                  >
                    {{ event.resolved ? "처리 완료" : "미처리" }}
                  </span>
                </div>

                <p class="mb-1 small">{{ readableSafetyEventMessage(event) }}</p>
                <p class="mb-1 small text-muted">신뢰도 {{ event.confidence }}</p>

                <img
                  v-if="event.resultImageUrl || event.imageUrl"
                  :src="event.resultImageUrl || event.imageUrl"
                  class="img-fluid rounded border mt-2"
                  style="max-height: 180px; object-fit: cover"
                  alt="안전 이벤트 분석 이미지"
                />

                <div>
                  <small class="text-muted">{{ formatDate(event.createdAt) }}</small>
                  <div class="mt-2">
                    <button
                      class="btn btn-sm btn-outline-success"
                      :disabled="event.resolved"
                      @click="resolveRecentSafetyEvent(event.eventId)"
                    >
                      {{ event.resolved ? "완료됨" : "처리 완료" }}
                    </button>
                  </div>
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
                    <th><span class="metric-mark">℃</span> 온도</th>
                    <th><span class="metric-mark">Hz</span> 진동</th>
                    <th><span class="metric-mark">dB</span> 소음</th>
                    <th><span class="metric-mark">%</span> 위험도</th>
                    <th>상태</th>
                    <th>PHM 모델</th>
                    <th>권장 조치</th>
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
                    <td>{{ status.temperature }}℃</td>
                    <td>{{ status.vibration }}Hz</td>
                    <td>{{ status.noise }}dB</td>
                    <td>{{ status.riskScore }}%</td>
                    <td>
                      <span class="badge" :class="statusBadgeClass(status.status)">
                        {{ deviceStatusLabel(status.status) }}
                      </span>
                    </td>
                    <td class="small text-muted">{{ status.modelVersion || "-" }}</td>
                    <td class="dashboard-recommendation-cell">
                      {{ status.recommendation || "-" }}
                    </td>
                    <td>{{ formatDate(status.createdAt) }}</td>
                  </tr>
                </tbody>
              </table>

              <div v-if="recent.recentDeviceStatuses.length === 0" class="text-muted">
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

<style scoped>
.metric-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 28px;
  height: 22px;
  padding: 0 6px;
  margin-right: 4px;
  border-radius: 6px;
  background: #f1f3f5;
  color: #495057;
  font-size: 0.75rem;
  font-weight: 700;
}

.dashboard-recommendation-cell {
  min-width: 240px;
  line-height: 1.4;
  word-break: keep-all;
  overflow-wrap: anywhere;
}
</style>
