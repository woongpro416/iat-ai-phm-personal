package com.example.demo.controller;

import com.example.demo.dto.response.DashboardRecentResponseDto;
import com.example.demo.dto.response.DashboardSummaryResponseDto;
import com.example.demo.service.DashboardService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/dashboard")
public class DashboardController {

    private final DashboardService dashboardService;

    //대시보드 요약 정보
    @GetMapping("/summary")
    public ResponseEntity<DashboardSummaryResponseDto> getDashboardSummary() {
        return ResponseEntity.ok(dashboardService.getDashboardSummary());
    }

    //대시보드 최근 이력
    @GetMapping("/recent")
    public ResponseEntity<DashboardRecentResponseDto> getDashboardRecent() {
        return ResponseEntity.ok(dashboardService.getDashboardRecent());
    }
}
