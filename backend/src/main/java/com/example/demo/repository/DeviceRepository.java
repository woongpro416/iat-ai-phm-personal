package com.example.demo.repository;

import com.example.demo.domain.Device;
import com.example.demo.domain.enums.DeviceStatusType;
import org.springframework.data.jpa.repository.JpaRepository;

public interface DeviceRepository extends JpaRepository<Device, Long> {

    long countByStatus(DeviceStatusType status);
}
