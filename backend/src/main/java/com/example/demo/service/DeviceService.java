package com.example.demo.service;

import com.example.demo.domain.Device;
import com.example.demo.dto.request.DeviceCreateRequestDto;
import com.example.demo.dto.request.DeviceStatusCreateRequestDto;
import com.example.demo.repository.AlertRepository;
import com.example.demo.repository.DeviceRepository;
import com.example.demo.repository.DeviceStatusLogRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class DeviceService {

    private final DeviceRepository deviceRepository;
    private final DeviceStatusLogRepository deviceStatusLogRepository;
    private final AlertRepository alertRepository;

    // 장비 등록
    @Transactional
    public Long createDevice(DeviceCreateRequestDto requestDto) {
        Device device = Device.builder()
                .deviceName(requestDto.getDeviceName())
                .deviceType(requestDto.getDeviceType())
                .location(requestDto.getLocation())
                .build();
        Device savedDevice = deviceRepository.save(device);
        return savedDevice.getDeviceId();
    }


}
