package com.example.demo.dto.request;

import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@AllArgsConstructor
@NoArgsConstructor
public class DeviceStatusCreateRequestDto {

    @NotNull(message = "장비 ID 는 필수입니다.")
    private Long deviceId;

    @NotNull(message = "온도는 필수입니다.")
    private Double temperature;

    @NotNull(message = "진동은 필수입니다.")
    @DecimalMin(value = "0.0", message = "소음 값은 0 이상이어야 합니다.")
    private Double vibration;

    @NotNull(message = "소음은 필수입니다.")
    @DecimalMin(value = "0.0", message = "소음 값은 0 이상이어야 합니다.")
    private Double noise;
}
