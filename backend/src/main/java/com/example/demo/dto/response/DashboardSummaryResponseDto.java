package com.example.demo.dto.response;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class DashboardSummaryResponseDto {

    private long totalDevices;

    private long normalDevices;

    private long warningDevices;

    private long dangerDevices;

    private long offlineDevices;

    private long totalSafetyEvents;

    private long unresolvedSafetyEvents;

    private long totalAlerts;

    private long uncheckedAlerts;

    private Double latestRiskScore;

    private String latestDeviceStatus;
}
