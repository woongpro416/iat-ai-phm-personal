package com.example.demo.dto.response;

import com.example.demo.domain.Alert;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter
public class AlertResponseDto {

    private Long alertId;
    private Long deviceId;
    private String deviceName;
    private String alertType;
    private String severity;
    private String message;
    private Boolean checked;
    private LocalDateTime createdAt;
    private LocalDateTime checkedAt;

    public AlertResponseDto(Alert alert) {
        this.alertId = alert.getAlertId();

        if (alert.getDevice() != null) {
            this.deviceId = alert.getDevice().getDeviceId();
            this.deviceName = alert.getDevice().getDeviceName();
        }

        this.alertType = alert.getAlertType().name();
        this.severity = alert.getSeverity().name();
        this.message = alert.getMessage();
        this.checked = alert.getChecked();
        this.createdAt = alert.getCreatedAt();
        this.checkedAt = alert.getCheckedAt();
    }
}
