package com.example.demo.service;

import com.example.demo.domain.Device;
import com.example.demo.dto.request.DeviceCreateRequestDto;
import com.example.demo.dto.request.DeviceStatusCreateRequestDto;
import com.example.demo.dto.response.DeviceResponseDto;
import com.example.demo.repository.AlertRepository;
import com.example.demo.repository.DeviceRepository;
import com.example.demo.repository.DeviceStatusLogRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

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

    // 장비 전체 목록 조회

    public List<DeviceResponseDto> getDeviceList() {
        return deviceRepository.findAll()
                .stream()
                .map(DeviceResponseDto::new)
                .collect(Collectors.toList());
    }

    // 장비 단건 조회
    public DeviceResponseDto getDevice(Long deviceId) {
        Device device = getDeviceEntity(deviceId);
        return new DeviceResponseDto(device);
    }

    // 장비 상태 로그 등록
    @Transactional
    public Long createDeviceStatusLog(DeviceStatusCreateRequestDto requestDto) {
        Device device = getDeviceEntity(requestDto, getDeviceId());

        double riskScore = calculateRiskScore(
                
        )
    }
}
