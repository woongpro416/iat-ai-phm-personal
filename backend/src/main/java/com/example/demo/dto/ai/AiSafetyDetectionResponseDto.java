package com.example.demo.dto.ai;

import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
public class AiSafetyDetectionResponseDto {

    private String eventType;

    private Double confidence;

    private String message;

    private String imagePath;

}
