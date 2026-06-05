package com.example.demo.dto.response;

import com.example.demo.domain.DeviceStatusLog;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter
public class DeviceStatusResponseDto {

    private Long statusId;

    private Long deviceId;

    private Double temperature;

    private Double vibration;

    private Double noise;

    private Double riskScore;

    private String status;

    private String modelVersion;

    private String predictionHorizon;

    private String analysisMessage;

    private String recommendation;

    private String thresholdViolations;

    private Double temperatureScore;

    private Double vibrationScore;

    private Double noiseScore;

    private LocalDateTime createdAt;

    public DeviceStatusResponseDto(DeviceStatusLog log) {
        this.statusId = log.getStatusLogId();
        this.deviceId = log.getDevice().getDeviceId();
        this.temperature = log.getTemperature();
        this.vibration = log.getVibration();
        this.noise = log.getNoise();
        this.riskScore = log.getRiskScore();
        this.status = log.getStatus().name();
        this.modelVersion = log.getModelVersion();
        this.predictionHorizon = log.getPredictionHorizon();
        this.analysisMessage = log.getAnalysisMessage();
        this.recommendation = log.getRecommendation();
        this.thresholdViolations = log.getThresholdViolations();
        this.temperatureScore = log.getTemperatureScore();
        this.vibrationScore = log.getVibrationScore();
        this.noiseScore = log.getNoiseScore();
        this.createdAt = log.getCreatedAt();
    }
}
