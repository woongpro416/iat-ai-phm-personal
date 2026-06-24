<script setup>
const entryCards = [
  {
    title: "관제 대시보드",
    caption: "장비 상태와 알림 우선순위",
    to: "/dashboard",
    metric: "10초",
    label: "자동 갱신",
  },
  {
    title: "장비 상태 분석",
    caption: "PHM rule baseline 근거 확인",
    to: "/device-status",
    metric: "3개",
    label: "센서 feature",
  },
  {
    title: "안전 이벤트",
    caption: "YOLO bbox 이미지 판독",
    to: "/safety-events",
    metric: "2장",
    label: "원본/분석",
  },
  {
    title: "알림 처리",
    caption: "미확인 이력 확인 처리",
    to: "/alerts",
    metric: "상세",
    label: "운영 메시지",
  },
];
</script>

<template>
  <section class="home-view">
    <div class="home-hero">
      <div class="hero-copy">
        <span class="home-eyebrow">IAT AI Safety System</span>
        <h1>무인 셔틀 관제 흐름을 한 화면에서 시작합니다.</h1>
        <p>
          장비 센서 위험도, YOLO 안전 이벤트, 알림 처리, PHM 학습 산출물을
          연결한 포트폴리오 관제 시스템입니다.
        </p>

        <div class="home-actions">
          <RouterLink class="btn btn-primary btn-lg" to="/dashboard">
            대시보드 열기
          </RouterLink>
          <RouterLink class="btn btn-outline-light btn-lg" to="/device-status">
            상태 분석
          </RouterLink>
        </div>
      </div>

      <div class="operations-panel" aria-label="관제 시스템 요약">
        <div class="panel-topline">
          <span>셔틀 운행 관제</span>
          <strong>LIVE</strong>
        </div>

        <div class="route-visual" aria-hidden="true">
          <svg viewBox="0 0 420 240" class="route-map">
            <text class="chart-title" x="24" y="28">최근 위험도 추이</text>
            <text class="chart-label" x="356" y="80">위험 80</text>
            <text class="chart-label" x="356" y="130">주의 50</text>

            <line class="chart-axis" x1="38" y1="204" x2="386" y2="204" />
            <line class="chart-axis" x1="38" y1="52" x2="38" y2="204" />
            <line class="chart-threshold danger" x1="38" y1="78" x2="386" y2="78" />
            <line class="chart-threshold warning" x1="38" y1="128" x2="386" y2="128" />

            <polyline
              class="risk-area"
              points="38,176 92,166 146,150 200,120 254,92 308,74 362,84 362,204 38,204"
            />
            <polyline
              class="risk-line"
              points="38,176 92,166 146,150 200,120 254,92 308,74 362,84"
            />

            <circle class="risk-point normal" cx="38" cy="176" r="5" />
            <circle class="risk-point normal" cx="92" cy="166" r="5" />
            <circle class="risk-point warning" cx="146" cy="150" r="5" />
            <circle class="risk-point warning" cx="200" cy="120" r="5" />
            <circle class="risk-point danger" cx="254" cy="92" r="5" />
            <circle class="risk-point danger active" cx="308" cy="74" r="7" />
            <circle class="risk-point danger" cx="362" cy="84" r="5" />

            <rect class="event-bar" x="64" y="214" width="22" height="8" rx="4" />
            <rect class="event-bar warning" x="172" y="214" width="38" height="8" rx="4" />
            <rect class="event-bar danger" x="278" y="214" width="56" height="8" rx="4" />
          </svg>
        </div>

        <div class="signal-grid">
          <div>
            <span>PHM 위험도</span>
            <strong>82%</strong>
          </div>
          <div>
            <span>안전 이벤트</span>
            <strong>YOLO</strong>
          </div>
          <div>
            <span>미확인 알림</span>
            <strong>4</strong>
          </div>
        </div>
      </div>
    </div>

    <div class="entry-grid">
      <RouterLink
        v-for="card in entryCards"
        :key="card.to"
        class="entry-card"
        :to="card.to"
      >
        <div>
          <span class="entry-caption">{{ card.caption }}</span>
          <h2>{{ card.title }}</h2>
        </div>
        <div class="entry-metric">
          <strong>{{ card.metric }}</strong>
          <span>{{ card.label }}</span>
        </div>
      </RouterLink>
    </div>
  </section>
</template>
