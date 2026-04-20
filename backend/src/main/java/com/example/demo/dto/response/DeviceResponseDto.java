package com.example.demo.dto.response;

import com.example.demo.domain.Device;
import lombok.Getter;

@Getter
public class DeviceResponseDto {

    private Long deviceId;

    private String deviceName;

    private String deviceType;

    private String location;

    private String status;

    public DeviceResponseDto(Device device) {
        this.deviceId = device.getDeviceId();
        this.deviceName = device.getDeviceName();
        this.deviceType = device.getDeviceType();
        this.location = device.getLocation();
        this.status = device.getStatus().name();
    }
}
