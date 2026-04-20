package com.example.demo.repository;

import com.example.demo.domain.Device;
import com.example.demo.domain.DeviceStatusLog;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface DeviceStatusLogRepository extends JpaRepository<DeviceStatusLog, Long> {
    List<DeviceStatusLog> findByDevice_DeviceIdOrderByCreatedAtDesc(Long deviceId);
}
