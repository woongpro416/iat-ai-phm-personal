$baseUrl = "http://localhost:8402"
$runId = Get-Date -Format "MMdd-HHmmss"

function New-RandomDouble($min, $max, $digits = 1) {
  $random = (Get-Random -Minimum 0 -Maximum 1000000) / 1000000
  return [math]::Round($min + ($random * ($max - $min)), $digits)
}

function Invoke-JsonPost($path, $body) {
  return Invoke-RestMethod `
    -Method Post `
    -Uri "$baseUrl$path" `
    -ContentType "application/json" `
    -Body ($body | ConvertTo-Json -Depth 5)
}

function New-SensorPayload($deviceId, $profile) {
  if ($profile -eq "NORMAL") {
    return @{
      deviceId = $deviceId
      temperature = New-RandomDouble 20 28
      vibration = New-RandomDouble 0.05 0.20 2
      noise = New-RandomDouble 30 40
    }
  }

  if ($profile -eq "WARNING") {
    return @{
      deviceId = $deviceId
      temperature = New-RandomDouble 35 45
      vibration = New-RandomDouble 0.25 0.50 2
      noise = New-RandomDouble 45 55
    }
  }

  return @{
    deviceId = $deviceId
    temperature = New-RandomDouble 60 75
    vibration = New-RandomDouble 0.70 1.20 2
    noise = New-RandomDouble 65 85
  }
}

Write-Host "Creating demo devices..."

$deviceProfiles = @(
  @{ name = "IAT-SHUTTLE-001-$runId"; location = "Terminal 1 Platform A"; profile = "NORMAL" },
  @{ name = "IAT-SHUTTLE-002-$runId"; location = "Terminal 1 Platform B"; profile = "WARNING" },
  @{ name = "IAT-SHUTTLE-003-$runId"; location = "Terminal 2 Platform A"; profile = "DANGER" },
  @{ name = "IAT-SHUTTLE-004-$runId"; location = "Terminal 2 Platform B"; profile = "NORMAL" },
  @{ name = "IAT-SHUTTLE-005-$runId"; location = "Maintenance Zone"; profile = "WARNING" },
  @{ name = "IAT-SHUTTLE-006-$runId"; location = "Cargo Shuttle Gate"; profile = "DANGER" }
)

$devices = @()

foreach ($deviceProfile in $deviceProfiles) {
  $deviceId = Invoke-JsonPost "/api/devices" @{
    deviceName = $deviceProfile.name
    deviceType = "AUTONOMOUS_SHUTTLE"
    location = $deviceProfile.location
  }

  $devices += @{
    id = $deviceId
    profile = $deviceProfile.profile
  }

  Write-Host "Created device $deviceId / $($deviceProfile.profile)"
}

Write-Host "Creating randomized device status logs..."

foreach ($device in $devices) {
  for ($i = 1; $i -le 5; $i++) {
    $payload = New-SensorPayload $device.id $device.profile
    Invoke-JsonPost "/api/device-status" $payload | Out-Null
  }

  Write-Host "Created status logs for device $($device.id)"
}

Write-Host "Creating safety events..."

$scenarios = @("FALL", "OBSTACLE", "DOOR", "DANGER_ZONE")

for ($i = 0; $i -lt $devices.Count; $i++) {
  $scenario = $scenarios[$i % $scenarios.Count]

  Invoke-JsonPost "/api/safety-events" @{
    deviceId = $devices[$i].id
    scenario = $scenario
  } | Out-Null

  Write-Host "Created safety event $scenario for device $($devices[$i].id)"
}

Write-Host ""
Write-Host "Demo seed completed."
Write-Host "Dashboard: http://localhost:5173/dashboard"
Write-Host "Swagger:   http://localhost:8402/swagger-ui/index.html"