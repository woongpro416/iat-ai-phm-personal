package com.example.demo.client;

import com.example.demo.dto.ai.AiSafetyDetectionRequestDto;
import com.example.demo.dto.ai.AiSafetyDetectionResponseDto;
import com.example.demo.dto.request.AiDeviceStatusRequestDto;
import com.example.demo.dto.response.AiDeviceStatusResponseDto;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

@Component
@RequiredArgsConstructor
public class AiAnalysisClient {

    private final RestClient restClient;

    @Value("${ai.server.url}")
    private String aiServerUrl;

    public AiDeviceStatusResponseDto predictDeviceStatus(
            Double temperature,
            Double vibration,
            Double noise
    ) {
        AiDeviceStatusRequestDto requestDto = new AiDeviceStatusRequestDto(
                temperature,
                vibration,
                noise
        );

        return restClient.post()
                .uri(aiServerUrl + "/predict/device-status")
                .body(requestDto)
                .retrieve()
                .body(AiDeviceStatusResponseDto.class);
    }

    public AiSafetyDetectionResponseDto detectSafetyEvent(
            Long deviceId,
            String scenario
    ) {
        AiSafetyDetectionRequestDto requestDto = new AiSafetyDetectionRequestDto(
                deviceId,
                scenario
        );

        return restClient.post()
                .uri(aiServerUrl + "/detect/safety")
                .body(requestDto)
                .retrieve()
                .body(AiSafetyDetectionResponseDto.class);
    }
}