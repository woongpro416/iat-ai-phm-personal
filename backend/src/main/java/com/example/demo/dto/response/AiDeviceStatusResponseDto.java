package com.example.demo.dto.response;

import lombok.Getter;

@Getter
public class AiDeviceStatusResponseDto {

    private Double riskScore;

    private String status;

    private String message;
}
