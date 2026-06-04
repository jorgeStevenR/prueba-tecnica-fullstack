$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "Construyendo y levantando contenedores..." -ForegroundColor Cyan
docker compose up --build -d

Write-Host "Esperando backend y frontend..." -ForegroundColor Cyan
$ready = $false
for ($i = 0; $i -lt 60; $i++) {
    $backendOk = $false
    $frontendOk = $false
    try {
        Invoke-WebRequest -Uri "http://localhost:8080/health" -UseBasicParsing -TimeoutSec 2 | Out-Null
        $backendOk = $true
    } catch {}
    try {
        Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 2 | Out-Null
        $frontendOk = $true
    } catch {}
    if ($backendOk -and $frontendOk) {
        $ready = $true
        break
    }
    Start-Sleep -Seconds 2
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Green
Write-Host "  Listo - Prueba Tecnica Fullstack" -ForegroundColor Green
Write-Host ""
Write-Host "  Frontend:  http://localhost:3000"
Write-Host "  Backend:   http://localhost:8080"
Write-Host "  Swagger:   http://localhost:8080/docs"
Write-Host ""
Write-Host "  Login:     admin / 1234"
Write-Host "==================================================" -ForegroundColor Green
Write-Host ""

if (-not $ready) {
    Write-Host "Los servicios tardan mas de lo esperado. Revisa: docker compose logs -f" -ForegroundColor Yellow
} else {
    Write-Host "Ver logs en vivo: docker compose logs -f" -ForegroundColor DarkGray
    Write-Host "Detener:         docker compose down" -ForegroundColor DarkGray
}
