package com.example.demo.service;

import com.example.demo.client.AiAnalysisClient;
import com.example.demo.common.BusinessException;
import com.example.demo.domain.Alert;
import com.example.demo.domain.Device;
import com.example.demo.domain.DeviceStatusLog;
import com.example.demo.domain.enums.AlertSeverity;
import com.example.demo.domain.enums.AlertType;
import com.example.demo.domain.enums.DeviceStatusType;
import com.example.demo.dto.request.DeviceCreateRequestDto;
import com.example.demo.dto.request.DeviceStatusCreateRequestDto;
import com.example.demo.dto.response.AiDeviceStatusResponseDto;
import com.example.demo.dto.response.AlertResponseDto;
import com.example.demo.dto.response.DeviceResponseDto;
import com.example.demo.dto.response.DeviceStatusResponseDto;
import com.example.demo.repository.AlertRepository;
import com.example.demo.repository.DeviceRepository;
import com.example.demo.repository.DeviceStatusLogRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class DeviceService {

    private final DeviceRepository deviceRepository;
    private final DeviceStatusLogRepository deviceStatusLogRepository;
    private final AlertRepository alertRepository;
    private final AiAnalysisClient aiAnalysisClient;

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

    public List<DeviceResponseDto> getDeviceList() {
        return deviceRepository.findAll()
                .stream()
                .map(DeviceResponseDto::new)
                .toList();
    }

    public DeviceResponseDto getDevice(Long deviceId) {
        Device device = getDeviceEntity(deviceId);
        return new DeviceResponseDto(device);
    }

    @Transactional
    public Long createDeviceStatusLog(DeviceStatusCreateRequestDto requestDto) {
        Device device = getDeviceEntity(requestDto.getDeviceId());

        AiDeviceStatusResponseDto aiResult = aiAnalysisClient.predictDeviceStatus(
                requestDto.getTemperature(),
                requestDto.getVibration(),
                requestDto.getNoise()
        );

        double riskScore = aiResult.getRiskScore();
        DeviceStatusType status = DeviceStatusType.valueOf(aiResult.getStatus());

        DeviceStatusLog statusLog = DeviceStatusLog.builder()
                .device(device)
                .temperature(requestDto.getTemperature())
                .vibration(requestDto.getVibration())
                .noise(requestDto.getNoise())
                .riskScore(riskScore)
                .status(status)
                .build();

        DeviceStatusLog savedLog = deviceStatusLogRepository.save(statusLog);

        device.updateStatus(status);

        if (status == DeviceStatusType.WARNING || status == DeviceStatusType.DANGER) {
            createDeviceRiskAlert(device, riskScore, status);
        }

        return savedLog.getStatusLogId();
    }

    public List<DeviceStatusResponseDto> getDeviceStatusLogs(Long deviceId) {
        getDeviceEntity(deviceId);

        return deviceStatusLogRepository.findByDevice_DeviceIdOrderByCreatedAtDesc(deviceId)
                .stream()
                .map(DeviceStatusResponseDto::new)
                .toList();
    }

    public List<AlertResponseDto> getAlertList() {
        return alertRepository.findAll()
                .stream()
                .map(AlertResponseDto::new)
                .toList();
    }

    @Transactional
    public void checkAlert(Long alertId) {
        Alert alert = alertRepository.findById(alertId)
                .orElseThrow(() -> new BusinessException(
                        HttpStatus.NOT_FOUND,
                        "존재하지 않는 알림입니다. alertId=" + alertId
                ));

        alert.check();
    }

    private Device getDeviceEntity(Long deviceId) {
        return deviceRepository.findById(deviceId)
                .orElseThrow(() -> new BusinessException(
                        HttpStatus.NOT_FOUND,
                        "존재하지 않는 장비입니다. deviceId=" + deviceId
                ));
    }

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
