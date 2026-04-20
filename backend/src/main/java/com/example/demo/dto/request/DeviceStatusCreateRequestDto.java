package com.example.demo.dto.request;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@AllArgsConstructor
@NoArgsConstructor
public class DeviceStatusCreateRequestDto {

    private Long deviceId;

    private Double temperature;

    private Double vibration;

    private Double noise;
}
