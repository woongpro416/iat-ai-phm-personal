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

    private String imageUrl;

    private String resultImagePath;

    private String resultImageUrl;

    private String message;

    private String detectionSummary;

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
        this.imageUrl = createImageUrl(safetyEvent.getImagePath());
        this.resultImagePath = safetyEvent.getResultImagePath();
        this.resultImageUrl = createImageUrl(safetyEvent.getResultImagePath());
        this.message = safetyEvent.getMessage();
        this.detectionSummary = safetyEvent.getDetectionSummary();
        this.resolved = safetyEvent.getResolved();
        this.createdAt = safetyEvent.getCreatedAt();
        this.resolvedAt = safetyEvent.getResolvedAt();
    }

    public String createImageUrl(String imagePath) {
        if (imagePath == null || imagePath.isBlank()) {
            return null;
        }

        String normalizedPath = imagePath.replace("\\", "/");
        String uploadRoot = "uploaded_images/";

        if (normalizedPath.contains(uploadRoot)) {
            String relativePath = normalizedPath.substring(normalizedPath.indexOf(uploadRoot) + uploadRoot.length());
            return "http://localhost:8000/images/" + relativePath;
        }

        String filename = normalizedPath.substring(normalizedPath.lastIndexOf("/") + 1);

        return "http://localhost:8000/images/" + filename;
    }
}
