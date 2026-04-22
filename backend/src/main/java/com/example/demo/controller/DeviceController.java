package com.example.demo.controller;

import com.example.demo.dto.request.DeviceCreateRequestDto;
import com.example.demo.dto.request.DeviceStatusCreateRequestDto;
import com.example.demo.dto.response.AlertResponseDto;
import com.example.demo.dto.response.DeviceResponseDto;
import com.example.demo.dto.response.DeviceStatusResponseDto;
import com.example.demo.service.DeviceService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api")
public class DeviceController {

    private final DeviceService deviceService;


    //장비 등록
    @PostMapping("/devices")
    public ResponseEntity<Long> createDevice(
            @RequestBody @Valid DeviceCreateRequestDto requestDto) {
        Long deviceId = deviceService.createDevice(requestDto);
        return ResponseEntity.status(HttpStatus.CREATED).body(deviceId);
    }

    //장비 전체 목록 조회
    @GetMapping("/devices")
    public ResponseEntity<List<DeviceResponseDto>> getDeviceList() {
        return ResponseEntity.ok(deviceService.getDeviceList());
    }

    //장비 단건 조회
    @GetMapping("/devices/{deviceId}")
    public ResponseEntity<DeviceResponseDto> getDevice(@PathVariable Long deviceId) {
        return ResponseEntity.ok(deviceService.getDevice(deviceId));
    }

    //장비 상태 로그 등록
    @PostMapping("/device-status")
    public ResponseEntity<Long> createDeviceStatusLog(
            @RequestBody @Valid DeviceStatusCreateRequestDto requestDto
    ) {
        Long statusLogId = deviceService.createDeviceStatusLog(requestDto);
        return ResponseEntity.status(HttpStatus.CREATED).body(statusLogId);
    }

    // 특정 장비의 상태 로그 조회
    @GetMapping("/device-status/{deviceId}")
    public ResponseEntity<List<DeviceStatusResponseDto>> getDeviceStatusLogs(@PathVariable Long deviceId) {
        return ResponseEntity.ok(deviceService.getDeviceStatusLogs(deviceId));
    }

    // 전체 알림 목록 조회
    @GetMapping("/alerts")
    public ResponseEntity<List<AlertResponseDto>> getAlertList() {
        return ResponseEntity.ok(deviceService.getAlertList());
    }

    // 알림 확인 처리
    @PatchMapping("/alerts/{alertId}/check")
    public ResponseEntity<Void> checkAlert(@PathVariable Long alertId) {
        deviceService.checkAlert(alertId);
        return ResponseEntity.noContent().build();
    }



}
