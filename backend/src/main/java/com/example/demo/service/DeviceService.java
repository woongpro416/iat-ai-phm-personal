package com.example.demo.service;

import com.example.demo.domain.Alert;
import com.example.demo.domain.Device;
import com.example.demo.domain.DeviceStatusLog;
import com.example.demo.domain.enums.AlertSeverity;
import com.example.demo.domain.enums.AlertType;
import com.example.demo.domain.enums.DeviceStatusType;
import com.example.demo.dto.request.DeviceCreateRequestDto;
import com.example.demo.dto.request.DeviceStatusCreateRequestDto;
import com.example.demo.dto.response.AlertResponseDto;
import com.example.demo.dto.response.DeviceResponseDto;
import com.example.demo.dto.response.DeviceStatusResponseDto;
import com.example.demo.repository.AlertRepository;
import com.example.demo.repository.DeviceRepository;
import com.example.demo.repository.DeviceStatusLogRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class DeviceService {

    private final DeviceRepository deviceRepository;
    private final DeviceStatusLogRepository deviceStatusLogRepository;
    private final AlertRepository alertRepository;

    // 장비 등록
    @Transactional
    public Long createDevice(DeviceCreateRequestDto requestDto) {
        Device device = Device.builder()
                .deviceName(requestDto.getDeviceName())
                .deviceType(requestDto.getDeviceType())
                .location(requestDto.getLocation())
                .build();
        Device savedDevice = deviceRepository.save(device);
        return savedDevice.getDeviceId();
    }

    // 장비 전체 목록 조회

    public List<DeviceResponseDto> getDeviceList() {
        return deviceRepository.findAll()
                .stream()
                .map(DeviceResponseDto::new)
                .toList();
    }

    // 장비 단건 조회
    public DeviceResponseDto getDevice(Long deviceId) {
        Device device = getDeviceEntity(deviceId);
        return new DeviceResponseDto(device);
    }

    // 장비 상태 로그 등록
    @Transactional
    public Long createDeviceStatusLog(DeviceStatusCreateRequestDto requestDto) {
        Device device = getDeviceEntity(requestDto.getDeviceId());

        double riskScore = calculateRiskScore(
                requestDto.getTemperature(),
                requestDto.getVibration(),
                requestDto.getNoise()
        );

        DeviceStatusType status = decideDeviceStatus(riskScore);

        DeviceStatusLog statusLog = DeviceStatusLog.builder()
                .device(device)
                .temperature(requestDto.getTemperature())
                .vibration(requestDto.getVibration())
                .noise(requestDto.getNoise())
                .riskScore(riskScore)
                .status(status)
                .build();

        DeviceStatusLog savedLog = deviceStatusLogRepository.save(statusLog);

        // 장비 현재 상태 업데이트
        device.updateStatus(status);

        // WARNING 이상이면 알림 자동 생성
        if (status == DeviceStatusType.WARNING || status == DeviceStatusType.DANGER) {
            createDeviceRiskAlert(device, riskScore, status);
        }

        return savedLog.getStatusLogId();
    }

    // 특정 장비의 상태 로그 조회
    public List<DeviceStatusResponseDto> getDeviceStatusLogs(Long deviceId) {
        getDeviceEntity(deviceId);

        return deviceStatusLogRepository.findByDevice_DeviceIdOrderByCreatedAtDesc(deviceId)
                .stream()
                .map(DeviceStatusResponseDto::new)
                .toList();
    }

    // 전체 알림 목록 조회
    public List<AlertResponseDto> getAlertList() {
        return alertRepository.findAll()
                .stream()
                .map(AlertResponseDto::new)
                .toList();
    }

    // 알림 확인 처리
    @Transactional
    public void checkAlert(Long alertId) {
        Alert alert = alertRepository.findById(alertId)
                .orElseThrow(() -> new IllegalStateException("존재하지 않는 알립입니다. alertId=" + alertId));

        alert.check();
    }


    // 내부 공통 : 장비 Entity 조회
    private Device getDeviceEntity(Long deviceId) {
        return deviceRepository.findById(deviceId)
                .orElseThrow(() -> new IllegalStateException("존재하지 않는 장비입니다. deviceId=" + deviceId));
    }

    // 임시 위험도 계산 로직(추후 FastAPI 또는 AI 모델 결과로 대체 예정)
    private double calculateRiskScore(Double temperature, Double vibration, Double noise) {
        if (temperature == null || vibration == null || noise == null) {
            throw new IllegalArgumentException("온도, 진동, 소음 값을 필수입니다.");
        }

        double tempScore = temperature * 0.8;
        double vibrationScore = vibration * 40.0;
        double noiseScore = noise * 0.3;

        double totalScore = tempScore + vibrationScore + noiseScore;

        return Math.min(100.0, Math.round(totalScore * 10.0) / 10.0);
    }

    // 위험도 기준 상태 분류
    private DeviceStatusType decideDeviceStatus(double riskScore) {
        if (riskScore >= 80) {
            return DeviceStatusType.DANGER;
        }
        if (riskScore >= 50) {
            return DeviceStatusType.WARNING;
        }
        return DeviceStatusType.NORMAL;
    }

    //장비 위험 알림 생성
    private void createDeviceRiskAlert(Device device, double riskScore, DeviceStatusType status) {
        AlertSeverity severity = status == DeviceStatusType.DANGER
                ? AlertSeverity.CRITICAL
                : AlertSeverity.WARNING;

        String message = String.format(
                "[%s] 장비 위험도 %.1f점 감지. 현재 상태: %s",
                device.getDeviceName(),
                riskScore,
                status
        );

        Alert alert = Alert.builder()
                .device(device)
                .alertType(AlertType.DEVICE_RISK)
                .severity(severity)
                .message(message)
                .checked(false)
                .build();

        alertRepository.save(alert);
    }


}
