<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { deviceApi } from "../api/deviceApi";
import { deviceStatusLabel, deviceTypeLabel, readableDeviceName } from "../utils/displayLabels";

const devices = ref([]);
const statusLogs = ref([]);
const selectedDeviceId = ref("");

const loading = ref(false);
const savingDevice = ref(false);
const savingStatus = ref(false);
const errorMessage = ref("");
const successMessage = ref("");

const deviceForm = reactive({
  deviceName: "",
  deviceType: "AUTONOMOUS_SHUTTLE",
  location: "",
});

const statusForm = reactive({
  temperature: "",
  vibration: "",
  noise: "",
});

const selectedDevice = computed(() => {
  return devices.value.find((device) => device.deviceId === Number(selectedDeviceId.value));
});

const toNumberOrNull = (value) => {
  if (value === "" || value === null || value === undefined) {
    return null;
  }

  return Number(value);
};

const getApiErrorMessage = (error, fallbackMessage) => {
  const responseData = error.response?.data;
  const fieldErrors = responseData?.fieldErrors;

  if (fieldErrors && Object.keys(fieldErrors).length > 0) {
    return Object.values(fieldErrors).join(" ");
  }

  return responseData?.message || fallbackMessage;
};

const loadDevices = async () => {
  const response = await deviceApi.getDevices();
  devices.value = response.data;

  if (!selectedDeviceId.value && devices.value.length > 0) {
    selectedDeviceId.value = devices.value[0].deviceId;
  }
};

const loadStatusLogs = async () => {
  if (!selectedDeviceId.value) {
    statusLogs.value = [];
    return;
  }

  const response = await deviceApi.getDeviceStatusLogs(selectedDeviceId.value);
  statusLogs.value = response.data;
};

const loadPage = async () => {
  loading.value = true;
  errorMessage.value = "";

  try {
    await loadDevices();
    await loadStatusLogs();
  } catch (error) {
    errorMessage.value = "장비 상태 데이터를 불러오지 못했습니다.";
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const createDevice = async () => {
  savingDevice.value = true;
  errorMessage.value = "";
  successMessage.value = "";

  try {
    await deviceApi.createDevice({ ...deviceForm });

    deviceForm.deviceName = "";
    deviceForm.deviceType = "AUTONOMOUS_SHUTTLE";
    deviceForm.location = "";

    successMessage.value = "장비가 등록되었습니다.";
    await loadDevices();
  } catch (error) {
    errorMessage.value = getApiErrorMessage(error, "장비 등록에 실패했습니다.");
    console.error(error);
  } finally {
    savingDevice.value = false;
  }
};

const createStatusLog = async () => {
  if (!selectedDeviceId.value) return;

  savingStatus.value = true;
  errorMessage.value = "";
  successMessage.value = "";

  try {
    await deviceApi.createDeviceStatus({
      deviceId: Number(selectedDeviceId.value),
      temperature: toNumberOrNull(statusForm.temperature),
      vibration: toNumberOrNull(statusForm.vibration),
      noise: toNumberOrNull(statusForm.noise),
    });

    statusForm.temperature = "";
    statusForm.vibration = "";
    statusForm.noise = "";

    successMessage.value = "장비 상태 로그가 등록되었습니다.";
    await loadDevices();
    await loadStatusLogs();
  } catch (error) {
    errorMessage.value = getApiErrorMessage(error, "장비 상태 로그 등록에 실패했습니다.");
    console.error(error);
  } finally {
    savingStatus.value = false;
  }
};

const changeDevice = async () => {
  errorMessage.value = "";

  try {
    await loadStatusLogs();
  } catch (error) {
    errorMessage.value = "장비 상태 로그를 불러오지 못했습니다.";
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

const thresholdViolationLabels = {
  TEMPERATURE_WARNING: "온도 주의",
  TEMPERATURE_DANGER: "온도 위험",
  VIBRATION_WARNING: "진동 주의",
  VIBRATION_DANGER: "진동 위험",
  NOISE_WARNING: "소음 주의",
  NOISE_DANGER: "소음 위험",
};

const formatThresholdViolations = (thresholdViolations) => {
  if (!thresholdViolations) return "기준 초과 없음";

  return thresholdViolations
    .split(",")
    .filter(Boolean)
    .map((violation) => thresholdViolationLabels[violation] || violation)
    .join(", ");
};

const formatScore = (score) => {
  return score === null || score === undefined ? "-" : score;
};

const formatDate = (dateText) => {
  if (!dateText) return "-";
  return dateText.replace("T", " ").slice(0, 19);
};

onMounted(() => {
  loadPage();
});
</script>

<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="fw-bold mb-1">장비 상태 모니터링</h2>
        <p class="text-muted mb-0">
          장비 등록, 센서 상태 입력, 위험도 분석 결과를 관리합니다.
        </p>
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
              <input
                v-model="deviceForm.deviceName"
                class="form-control"
                placeholder="예: 셔틀 1호기"
              />
            </div>

            <div class="mb-3">
              <label class="form-label">장비 종류</label>
              <input v-model="deviceForm.deviceType" class="form-control" />
              <div class="form-text">
                현재 입력값: {{ deviceTypeLabel(deviceForm.deviceType) }}
              </div>
            </div>

            <div class="mb-3">
              <label class="form-label">운행 위치</label>
              <input
                v-model="deviceForm.location"
                class="form-control"
                placeholder="예: 인천공항 제1터미널"
              />
            </div>

            <button
              class="btn btn-primary w-100"
              :disabled="savingDevice"
              @click="createDevice"
            >
              {{ savingDevice ? "등록 중..." : "장비 등록" }}
            </button>
          </div>
        </div>
      </div>

      <div class="col-lg-7">
        <div class="card shadow-sm h-100">
          <div class="card-header fw-bold">상태 로그 등록</div>
          <div class="card-body">
            <div class="mb-3">
              <label class="form-label">대상 장비</label>
              <select v-model="selectedDeviceId" class="form-select" @change="changeDevice">
                <option value="" disabled>장비 선택</option>
                <option v-for="device in devices" :key="device.deviceId" :value="device.deviceId">
                  {{ readableDeviceName(device.deviceName) }} / {{ device.location }}
                </option>
              </select>
            </div>

            <div v-if="selectedDevice" class="mb-3 d-flex flex-wrap gap-2">
              <span class="badge" :class="statusBadgeClass(selectedDevice.status)">
                현재 상태: {{ deviceStatusLabel(selectedDevice.status) }}
              </span>
              <span class="badge bg-light text-dark border">
                장비 종류: {{ deviceTypeLabel(selectedDevice.deviceType) }}
              </span>
            </div>

            <div class="row g-3">
              <div class="col-md-4">
                <label class="form-label">
                  <span class="metric-mark">℃</span>
                  온도
                </label>
                <input
                  v-model="statusForm.temperature"
                  type="number"
                  class="form-control"
                  placeholder="예: 36"
                />
              </div>

              <div class="col-md-4">
                <label class="form-label">
                  <span class="metric-mark">Hz</span>
                  진동
                </label>
                <input
                  v-model="statusForm.vibration"
                  type="number"
                  step="0.1"
                  class="form-control"
                  placeholder="예: 1.4"
                />
              </div>

              <div class="col-md-4">
                <label class="form-label">
                  <span class="metric-mark">dB</span>
                  소음
                </label>
                <input
                  v-model="statusForm.noise"
                  type="number"
                  step="0.1"
                  class="form-control"
                  placeholder="예: 62"
                />
              </div>
            </div>

            <button
              class="btn btn-danger w-100 mt-3"
              :disabled="!selectedDeviceId || savingStatus"
              @click="createStatusLog"
            >
              {{ savingStatus ? "분석 중..." : "상태 분석 로그 등록" }}
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
                <th>번호</th>
                <th><span class="metric-mark">℃</span> 온도</th>
                <th><span class="metric-mark">Hz</span> 진동</th>
                <th><span class="metric-mark">dB</span> 소음</th>
                <th><span class="metric-mark">%</span> 위험도</th>
                <th>판정 상태</th>
                <th>PHM 모델</th>
                <th>분석 근거</th>
                <th>권장 조치</th>
                <th>등록 시간</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="log in statusLogs" :key="log.statusId">
                <td class="text-muted">#{{ log.statusId }}</td>
                <td>{{ log.temperature }}℃</td>
                <td>{{ log.vibration }}Hz</td>
                <td>{{ log.noise }}dB</td>
                <td class="risk-score-cell">
                  <div class="fw-bold">{{ log.riskScore }}%</div>
                  <div class="score-breakdown">
                    온도 {{ formatScore(log.temperatureScore) }} /
                    진동 {{ formatScore(log.vibrationScore) }} /
                    소음 {{ formatScore(log.noiseScore) }}
                  </div>
                </td>
                <td>
                  <span class="badge" :class="statusBadgeClass(log.status)">
                    {{ deviceStatusLabel(log.status) }}
                  </span>
                </td>
                <td class="model-cell">
                  <div>{{ log.modelVersion || "-" }}</div>
                  <small class="text-muted">{{ log.predictionHorizon || "-" }}</small>
                </td>
                <td class="analysis-cell">
                  <div>{{ formatThresholdViolations(log.thresholdViolations) }}</div>
                  <small class="text-muted">{{ log.analysisMessage || "-" }}</small>
                </td>
                <td class="recommendation-cell">{{ log.recommendation || "-" }}</td>
                <td>{{ formatDate(log.createdAt) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
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

.risk-score-cell {
  min-width: 150px;
}

.score-breakdown {
  color: #6c757d;
  font-size: 0.78rem;
  line-height: 1.35;
  white-space: nowrap;
}

.model-cell {
  min-width: 160px;
  font-size: 0.86rem;
}

.analysis-cell {
  min-width: 260px;
  line-height: 1.4;
  word-break: keep-all;
  overflow-wrap: anywhere;
}

.recommendation-cell {
  min-width: 280px;
  line-height: 1.4;
  word-break: keep-all;
  overflow-wrap: anywhere;
}
</style>
