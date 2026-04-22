package com.example.demo.service;

import com.example.demo.domain.DeviceStatusLog;
import com.example.demo.domain.enums.DeviceStatusType;
import com.example.demo.dto.response.*;
import com.example.demo.repository.AlertRepository;
import com.example.demo.repository.DeviceRepository;
import com.example.demo.repository.DeviceStatusLogRepository;
import com.example.demo.repository.SafetyEventRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class DashboardService {

    private final AlertRepository alertRepository;
    private final DeviceRepository deviceRepository;
    private final DeviceStatusLogRepository deviceStatusLogRepository;
    private final SafetyEventRepository safetyEventRepository;

    //대시보드 요약 정보 조회
    public DashboardSummaryResponseDto getDashboardSummary() {
        long totalDevices = deviceRepository.count();

        long normalDevices = deviceRepository.countByStatus(DeviceStatusType.NORMAL);
        long warningDevices = deviceRepository.countByStatus(DeviceStatusType.WARNING);
        long dangerDevices = deviceRepository.countByStatus(DeviceStatusType.DANGER);
        long offlineDevices = deviceRepository.countByStatus(DeviceStatusType.OFFLINE);

        long totalSafetyEvents = safetyEventRepository.count();
        long unresolvedSafetyEvents = safetyEventRepository.countByResolvedFalse();

        long totalAlerts = alertRepository.count();
        long uncheckedAlerts = alertRepository.countByCheckedFalse();

        Optional<DeviceStatusLog> latestStatusLogOptional =
                deviceStatusLogRepository.findTop1ByOrderByCreatedAtDesc();

        Double latestRiskScore = latestStatusLogOptional
                .map(DeviceStatusLog::getRiskScore)
                .orElse(null);

        String latestDeviceStatus = latestStatusLogOptional
                .map(log -> log.getStatus().name())
                .orElse(null);

        return new DashboardSummaryResponseDto(
                totalDevices,
                normalDevices,
                warningDevices,
                dangerDevices,
                offlineDevices,
                totalSafetyEvents,
                unresolvedSafetyEvents,
                totalAlerts,
                uncheckedAlerts,
                latestRiskScore,
                latestDeviceStatus
        );
    }

    //대시보드 최근 이력 조회
    public DashboardRecentResponseDto getDashboardRecent() {
        List<AlertResponseDto> recentAlerts = alertRepository.findTop5ByOrderByCreatedAtDesc()
                .stream()
                .map(AlertResponseDto::new)
                .toList();

        List<SafetyEventResponseDto> recentSafetyEvents = safetyEventRepository.findTop5ByOrderByCreatedAtDesc()
                .stream()
                .map(SafetyEventResponseDto::new)
                .toList();

        List<DeviceStatusResponseDto> recentDeviceStatuses = deviceStatusLogRepository.findTop5ByOrderByCreatedAtDesc()
                .stream()
                .map(DeviceStatusResponseDto::new)
                .toList();

        return new DashboardRecentResponseDto(
                recentAlerts,
                recentSafetyEvents,
                recentDeviceStatuses
        );
    }

}
