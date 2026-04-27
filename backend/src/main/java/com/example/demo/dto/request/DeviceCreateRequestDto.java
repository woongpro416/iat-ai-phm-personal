package com.example.demo.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
@AllArgsConstructor
public class DeviceCreateRequestDto {

    @NotBlank(message = "장비명은 필수입니다.")
    @Size(max = 100, message = "장비명은 100자 이하여야 합니다.")
    private String deviceName;

    @NotBlank(message = "장비 유형은 필수입니다.")
    @Size(max = 50, message = "장비 유형은 50자 이하여야 합니다.")
    private String deviceType;

    @NotBlank(message = "위치는 필수입니다.")
    @Size(max = 150, message = "위치는 150자 이하여야 합니다.")
    private String location;
}
