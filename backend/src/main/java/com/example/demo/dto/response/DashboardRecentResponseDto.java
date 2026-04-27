package com.example.demo.dto.response;

import lombok.AllArgsConstructor;
import lombok.Getter;

import java.util.List;

@Getter
@AllArgsConstructor
public class DashboardRecentResponseDto {

    private List<AlertResponseDto> recentAlerts;

    private List<SafetyEventResponseDto> recentSafetyEvents;

    private List<DeviceStatusResponseDto> recentDeviceStatuses;
}
