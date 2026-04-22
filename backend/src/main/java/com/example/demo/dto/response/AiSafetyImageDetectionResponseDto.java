package com.example.demo.dto.response;

import com.example.demo.dto.ai.AiYoloDetectionBoxDto;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.util.List;

@Getter
@NoArgsConstructor
public class AiSafetyImageDetectionResponseDto {

    private String eventType;

    private Double confidence;

    private String message;

    private String imagePath;

    private List<AiYoloDetectionBoxDto> detections;
}
