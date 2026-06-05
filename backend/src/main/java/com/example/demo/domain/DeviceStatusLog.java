package com.example.demo.domain;

import com.example.demo.domain.enums.DeviceStatusType;
import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "device_status_logs")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor
@Builder
public class DeviceStatusLog {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long statusLogId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(nullable = false, name = "device_id")
    private Device device;

    @Column(nullable = false)
    private Double temperature;

    @Column(nullable = false)
    private Double vibration;

    @Column(nullable = false)
    private Double noise;

    @Column(nullable = false)
    private Double riskScore;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private DeviceStatusType status;

    @Column(length = 80)
    private String modelVersion;

    @Column(length = 50)
    private String predictionHorizon;

    @Column(length = 700)
    private String analysisMessage;

    @Column(length = 700)
    private String recommendation;

    @Column(length = 500)
    private String thresholdViolations;

    private Double temperatureScore;

    private Double vibrationScore;

    private Double noiseScore;

    @Column(nullable = false)
    private LocalDateTime createdAt;

    @PrePersist
    public void prePersist() {
        this.createdAt = LocalDateTime.now();
    }
}
