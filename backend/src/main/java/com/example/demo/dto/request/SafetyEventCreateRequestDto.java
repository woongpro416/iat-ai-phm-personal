package com.example.demo.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
@AllArgsConstructor
public class SafetyEventCreateRequestDto {

    @NotNull(message = "장비 ID는 필수입니다.")
    private Long deviceId;

    @NotBlank(message = "시나리오는 필수입니다.")
    @Pattern(
            regexp = "FALL|DOOR|OBSTACLE|DANGER_ZONE",
            message = "시나리오는 FALL, DOOR, OBSTACLE, DANGER_ZONE 중 하나여야 합니다."
    )
    private String scenario;
}
