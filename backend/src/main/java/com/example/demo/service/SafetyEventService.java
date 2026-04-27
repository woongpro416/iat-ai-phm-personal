package com.example.demo.service;

import com.example.demo.client.AiAnalysisClient;
import com.example.demo.common.BusinessException;
import com.example.demo.domain.Alert;
import com.example.demo.domain.Device;
import com.example.demo.domain.SafetyEvent;
import com.example.demo.domain.enums.AlertSeverity;
import com.example.demo.domain.enums.AlertType;
import com.example.demo.domain.enums.SafetyEventType;
import com.example.demo.dto.ai.AiSafetyDetectionResponseDto;
import com.example.demo.dto.request.SafetyEventCreateRequestDto;
import com.example.demo.dto.response.AiSafetyImageDetectionResponseDto;
import com.example.demo.dto.response.SafetyEventResponseDto;
import com.example.demo.repository.AlertRepository;
import com.example.demo.repository.DeviceRepository;
import com.example.demo.repository.SafetyEventRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class SafetyEventService {

    private final SafetyEventRepository safetyEventRepository;
    private final DeviceRepository deviceRepository;
    private final AlertRepository alertRepository;
    private final AiAnalysisClient aiAnalysisClient;


    @Transactional
    public Long createSafetyEvent(SafetyEventCreateRequestDto requestDto) {
        Device device = getDeviceEntity(requestDto.getDeviceId());

        AiSafetyDetectionResponseDto aiResult = aiAnalysisClient.detectSafetyEvent(
                requestDto.getDeviceId(),
                requestDto.getScenario()
        );

        SafetyEventType eventType = SafetyEventType.valueOf(aiResult.getEventType());

        SafetyEvent safetyEvent = SafetyEvent.builder()
                .device(device)
                .eventType(eventType)
                .confidence(aiResult.getConfidence())
                .imagePath(aiResult.getImagePath())
                .message(aiResult.getMessage())
                .resolved(false)
                .build();

        SafetyEvent safedEvent = safetyEventRepository.save(safetyEvent);

        createSafetyAlert(device, eventType, aiResult.getConfidence(), aiResult.getMessage());

        return safedEvent.getEventId();
    }


    public List<SafetyEventResponseDto> getSafetyEventList() {
        return safetyEventRepository.findAllByOrderByCreatedAtDesc()
                .stream()
                .map(SafetyEventResponseDto::new)
                .toList();
    }

    @Transactional
    public void resolveSafetyEvent(Long eventId) {
        SafetyEvent safetyEvent = safetyEventRepository.findById(eventId)
                .orElseThrow(() -> new BusinessException(
                        HttpStatus.NOT_FOUND,
                        "존재하지 않는 안전 이벤트입니다. eventId=" + eventId
                ));

        safetyEvent.resolve();
    }

    private Device getDeviceEntity(Long deviceId) {
        return deviceRepository.findById(deviceId)
                .orElseThrow(() -> new BusinessException(
                        HttpStatus.NOT_FOUND,
                        "존재하지 않는 장비입니다. deviceId=" + deviceId
                ));
    }

    private void createSafetyAlert (
            Device device,
            SafetyEventType eventType,
            Double confidence,
            String message
    ) {
        String alertMessage = String.format(
                "[%s] 안전 이벤트 감지: %s / 신뢰도 %.2f - %s",
                device.getDeviceName(),
                eventType,
                confidence,
                message
        );
        Alert alert = Alert.builder()
                .device(device)
                .alertType(AlertType.SAFETY_EVENT)
                .severity(AlertSeverity.CRITICAL)
                .message(alertMessage)
                .checked(false)
                .build();

        alertRepository.save(alert);
    }
    public List<SafetyEventResponseDto> getSafetyEventsByDevice(Long deviceId) {
        getDeviceEntity(deviceId);

        return safetyEventRepository.findByDevice_DeviceIdOrderByCreatedAtDesc(deviceId)
                .stream()
                .map(SafetyEventResponseDto::new)
                .toList();
    }

    @Transactional
    public Long createSafetyEventFromImage(Long deviceId, MultipartFile file) {
        Device device = getDeviceEntity(deviceId);

        AiSafetyImageDetectionResponseDto aiResult = aiAnalysisClient.detectSafetyEventFromImage(file);

        SafetyEventType eventType = convertSafetyEventType(aiResult.getEventType());

        SafetyEvent safetyEvent = SafetyEvent.builder()
                .device(device)
                .eventType(eventType)
                .confidence(aiResult.getConfidence())
                .imagePath(aiResult.getImagePath())
                .message(aiResult.getMessage())
                .resolved(false)
                .build();

        SafetyEvent savedEvent = safetyEventRepository.save(safetyEvent);

        createYoloSafetyAlert(
                device,
                eventType,
                aiResult.getConfidence(),
                aiResult.getMessage()
        );

        return savedEvent.getEventId();
    }

    private SafetyEventType convertSafetyEventType(String eventType) {
        try {
            return SafetyEventType.valueOf(eventType);
        } catch (IllegalArgumentException | NullPointerException e) {
            throw new BusinessException(
                    HttpStatus.BAD_GATEWAY,
                    "AI 서버가 지원하지 않는 안전 이벤트 유형을 반환했습니다. eventType=" + eventType
            );
        }
    }

    private void createYoloSafetyAlert(
            Device device,
            SafetyEventType eventType,
            Double confidence,
            String message
    ) {
        AlertSeverity severity = confidence != null && confidence >= 0.8
                ? AlertSeverity.CRITICAL
                : AlertSeverity.WARNING;

        String alertMessage = String.format(
                "[%s] YOLO 객체탐지 이벤트 발생: %s / 신뢰도 %.2f - %s",
                device.getDeviceName(),
                eventType,
                confidence != null ? confidence : 0.0,
                message
        );

        Alert alert = Alert.builder()
                .device(device)
                .alertType(AlertType.SAFETY_EVENT)
                .severity(severity)
                .message(alertMessage)
                .checked(false)
                .build();

        alertRepository.save(alert);
    }

    public List<SafetyEventResponseDto> getRecentSafetyEvents() {
        return safetyEventRepository.findTop5ByOrderByCreatedAtDesc()
                .stream()
                .map(SafetyEventResponseDto::new)
                .toList();
    }
}
