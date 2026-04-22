package com.example.demo.dto.ai;

import lombok.Getter;
import lombok.NoArgsConstructor;

import java.util.Map;

@Getter
@NoArgsConstructor
public class AiYoloDetectionBoxDto {

    private Integer classId;

    private String className;

    private Double confidence;

    private Map<String, Double> bbox;
}
