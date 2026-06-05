package com.example.demo.dto.response;

import lombok.Getter;

import java.util.List;
import java.util.Map;

@Getter
public class AiDeviceStatusResponseDto {

    private Double riskScore;

    private String status;

    private String message;

    private String modelVersion;

    private String predictionHorizon;

    private Map<String, Double> contributionScores;

    private List<String> thresholdViolations;

    private String recommendation;
}
