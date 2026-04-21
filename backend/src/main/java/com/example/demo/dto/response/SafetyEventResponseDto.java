package com.example.demo.dto.response;

import com.example.demo.domain.SafetyEvent;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter
public class SafetyEventResponseDto {

    private Long eventId;

    private Long deviceId;

    private String deviceName;

    private String eventType;

    private Double confidence;

    private String imagePath;

    private String message;

    private Boolean resolved;

    private LocalDateTime createdAt;

    private LocalDateTime resolvedAt;

    public SafetyEventResponseDto(SafetyEvent safetyEvent) {
        this.eventId = safetyEvent.getEventId();
        this.deviceId = safetyEvent.getDevice().getDeviceId();
        this.deviceName = safetyEvent.getDevice().getDeviceName();
        this.eventType = safetyEvent.getEventType().name();
        this.confidence = safetyEvent.getConfidence();
        this.imagePath = safetyEvent.getImagePath();
        this.message = safetyEvent.getMessage();
        this.resolved = safetyEvent.getResolved();
        this.createdAt = safetyEvent.getCreatedAt();
        this.resolvedAt = safetyEvent.getResolvedAt();
    }

}
