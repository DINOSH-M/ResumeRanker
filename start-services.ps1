# PowerShell script to start all microservices
# This script handles Docker cleanup and proper startup

Write-Host "=== AI Resume Ranker Platform - Service Startup ===" -ForegroundColor Green
Write-Host ""

# Check if Docker is running
Write-Host "Checking Docker status..." -ForegroundColor Yellow
$dockerRunning = $false
try {
    $null = docker ps 2>&1
    if ($LASTEXITCODE -eq 0) {
        $dockerRunning = $true
        Write-Host "Docker is running!" -ForegroundColor Green
    }
} catch {
    Write-Host "Docker is not responding. Starting Docker Desktop..." -ForegroundColor Red
}

if (-not $dockerRunning) {
    Write-Host "Please ensure Docker Desktop is running before proceeding." -ForegroundColor Red
    Write-Host "Waiting 10 seconds for Docker to initialize..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    
    try {
        $null = docker ps 2>&1
        if ($LASTEXITCODE -eq 0) {
            $dockerRunning = $true
        }
    } catch {
        Write-Host "Docker is still not ready. Please start Docker Desktop manually." -ForegroundColor Red
        exit 1
    }
}

# Clean up existing containers and images
Write-Host ""
Write-Host "Cleaning up existing containers..." -ForegroundColor Yellow
docker compose -p resumeranker down --remove-orphans 2>&1 | Out-Null

# Remove corrupted images
Write-Host "Removing any corrupted images..." -ForegroundColor Yellow
docker images --filter "reference=resumeranker-*" --format "{{.ID}}" | ForEach-Object {
    docker rmi $_ -f 2>&1 | Out-Null
}
docker images --filter "reference=github-*" --format "{{.ID}}" | ForEach-Object {
    docker rmi $_ -f 2>&1 | Out-Null
}

# Build images
Write-Host ""
Write-Host "Building Docker images..." -ForegroundColor Yellow
docker compose -p resumeranker build --no-cache 2>&1 | Tee-Object -Variable buildOutput
if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed. Check output above." -ForegroundColor Red
    exit 1
}

# Start services
Write-Host ""
Write-Host "Starting all services..." -ForegroundColor Yellow
docker compose -p resumeranker up -d 2>&1 | Tee-Object -Variable startOutput
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=== Services Started Successfully! ===" -ForegroundColor Green
    Write-Host ""
    Write-Host "Service URLs:" -ForegroundColor Cyan
    Write-Host "  - Eureka Dashboard: http://localhost:8761" -ForegroundColor White
    Write-Host "  - API Gateway: http://localhost:8080" -ForegroundColor White
    Write-Host "  - Auth Service: http://localhost:8081" -ForegroundColor White
    Write-Host "  - Resume Client Service: http://localhost:8082" -ForegroundColor White
    Write-Host "  - Resume Ranker Service: http://localhost:8000" -ForegroundColor White
    Write-Host "  - FastAPI Docs: http://localhost:8000/docs" -ForegroundColor White
    Write-Host ""
    Write-Host "Check service status: docker compose -p resumeranker ps" -ForegroundColor Yellow
    Write-Host "View logs: docker compose -p resumeranker logs -f" -ForegroundColor Yellow
} else {
    Write-Host "Failed to start services. Check output above." -ForegroundColor Red
    exit 1
}

