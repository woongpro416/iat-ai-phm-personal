package com.example.demo.dto.ai;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
@AllArgsConstructor
public class AiSafetyDetectionRequestDto {

    private Long deviceId;

    private String scenario;

}