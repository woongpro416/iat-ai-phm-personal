package com.example.demo.repository;

import com.example.demo.domain.SafetyEvent;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface SafetyEventRepository extends JpaRepository<SafetyEvent, Long> {

    List<SafetyEvent> findAllByOrderByCreatedAtDesc();

    List<SafetyEvent> findByDevice_DeviceIdOrderByCreatedAtDesc(Long deviceId);

    List<SafetyEvent> findTop5ByOrderByCreatedAtDesc();

    long countByResolvedFalse();
}
