package com.example.demo.dto.request;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
@AllArgsConstructor
public class SafetyEventCreateRequestDto {

    private Long deviceId;

    // 테스트용 시나리오 : FALL, DOOR, OBSTACLE, DANGER_ZONE
    private String scenario;
}
