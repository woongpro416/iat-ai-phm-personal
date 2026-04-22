package com.example.demo.controller;

import com.example.demo.dto.request.SafetyEventCreateRequestDto;
import com.example.demo.dto.response.SafetyEventResponseDto;
import com.example.demo.service.SafetyEventService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/safety-events")
public class SafetyEventController {

    private final SafetyEventService safetyEventService;

    @PostMapping
    public ResponseEntity<Long> createSafetyEvent(
            @RequestBody @Valid SafetyEventCreateRequestDto requestDto
            ) {
        Long eventId = safetyEventService.createSafetyEvent(requestDto);
        return ResponseEntity.status(HttpStatus.CREATED).body(eventId);
    }

    @GetMapping
    public ResponseEntity<List<SafetyEventResponseDto>> getSafetyEventList() {
        return ResponseEntity.ok(safetyEventService.getSafetyEventList());
    }

    @GetMapping("/device/{deviceId}")
    public ResponseEntity<List<SafetyEventResponseDto>> getSafetyEventsByDevice(
            @PathVariable Long deviceId
    ) {
        return ResponseEntity.ok(safetyEventService.getSafetyEventsByDevice(deviceId));
    }

    @PatchMapping("/{eventId}/resolve")
    public ResponseEntity<Void> resolveSafetyEvent(@PathVariable Long eventId) {
        safetyEventService.resolveSafetyEvent(eventId);
        return ResponseEntity.noContent().build();
    }

    @PostMapping(value = "/image", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<Long> createSafetyEventFromImage(
            @RequestParam("deviceId") Long deviceId,
            @RequestParam("file") MultipartFile file
    ) {
        Long eventId = safetyEventService.createSafetyEventFromImage(deviceId, file);
        return ResponseEntity.status(HttpStatus.CREATED).body(eventId);
    }

    @GetMapping("/recent")
    public ResponseEntity<List<SafetyEventResponseDto>> getRecentSafetyEvents() {
        return ResponseEntity.ok(safetyEventService.getRecentSafetyEvents());
    }
}
