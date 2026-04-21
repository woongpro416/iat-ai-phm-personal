package com.example.demo.dto.request;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.RequiredArgsConstructor;

@Getter
@RequiredArgsConstructor
@AllArgsConstructor
public class AiDeviceStatusRequestDto {

    private Double temperature;

    private Double vibration;

    private Double noise;
}
