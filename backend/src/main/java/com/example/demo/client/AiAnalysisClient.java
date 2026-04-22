package com.example.demo.client;

import com.example.demo.dto.ai.AiSafetyDetectionRequestDto;
import com.example.demo.dto.ai.AiSafetyDetectionResponseDto;
import com.example.demo.dto.request.AiDeviceStatusRequestDto;
import com.example.demo.dto.response.AiDeviceStatusResponseDto;
import com.example.demo.dto.response.AiSafetyImageDetectionResponseDto;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.HttpEntity;
import org.springframework.http.MediaType;
import org.springframework.http.client.MultipartBodyBuilder;
import org.springframework.stereotype.Component;
import org.springframework.util.MultiValueMap;
import org.springframework.util.StringUtils;
import org.springframework.web.client.RestClient;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;

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

    public AiSafetyImageDetectionResponseDto detectSafetyEventFromImage(MultipartFile file) {
        try {
            String originalFilename = StringUtils.hasText(file.getOriginalFilename())
                    ? file.getOriginalFilename()
                    : "upload-image.jpg";

            ByteArrayResource fileResource = new ByteArrayResource(file.getBytes()) {
                @Override
                public String getFilename() {
                    return originalFilename;
                }
            };

            MultipartBodyBuilder bodyBuilder = new MultipartBodyBuilder();
            bodyBuilder.part("file", fileResource)
                    .filename(originalFilename)
                    .contentType(MediaType.parseMediaType(file.getContentType() != null
                            ? file.getContentType()
                            : MediaType.APPLICATION_OCTET_STREAM_VALUE));

            MultiValueMap<String, HttpEntity<?>> multipartBody = bodyBuilder.build();

            return restClient.post()
                    .uri(aiServerUrl + "/detect/safety/image")
                    .contentType(MediaType.MULTIPART_FORM_DATA)
                    .body(multipartBody)
                    .retrieve()
                    .body(AiSafetyImageDetectionResponseDto.class);

        } catch (IOException e) {
            throw new IllegalStateException("이미지 파일을 읽는 중 오류가 발생했습니다.", e);
        }
    }
}