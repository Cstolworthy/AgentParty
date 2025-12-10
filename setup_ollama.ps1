# AgentParty Ollama Setup Script

Write-Host "================================" -ForegroundColor Cyan
Write-Host "  AgentParty Ollama Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Ollama installation
Write-Host "[1/5] Checking Ollama..." -ForegroundColor Yellow
$ollamaCmd = Get-Command ollama -ErrorAction SilentlyContinue

if ($ollamaCmd) {
    Write-Host "  OK - Ollama is installed" -ForegroundColor Green
    ollama --version
} else {
    Write-Host "  Installing Ollama..." -ForegroundColor Yellow
    winget install Ollama.Ollama --silent --accept-source-agreements --accept-package-agreements
    Write-Host "  OK - Installed" -ForegroundColor Green
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

Write-Host ""

# Step 2: Check service
Write-Host "[2/5] Checking service..." -ForegroundColor Yellow
ollama list | Out-Null
Write-Host "  OK - Service running" -ForegroundColor Green

Write-Host ""

# Step 3: Pull embedding model
Write-Host "[3/5] Checking nomic-embed-text..." -ForegroundColor Yellow
$models = ollama list | Out-String

if ($models -match "nomic-embed-text") {
    Write-Host "  OK - Already available" -ForegroundColor Green
} else {
    Write-Host "  Pulling nomic-embed-text (274MB)..." -ForegroundColor Yellow
    ollama pull nomic-embed-text
    Write-Host "  OK - Downloaded" -ForegroundColor Green
}

Write-Host ""

# Step 4: Pull coder model
Write-Host "[4/5] Checking qwen2.5-coder:7b..." -ForegroundColor Yellow
$models = ollama list | Out-String

if ($models -match "qwen2.5-coder:7b") {
    Write-Host "  OK - Already available" -ForegroundColor Green
} else {
    Write-Host "  Pulling qwen2.5-coder:7b (4.7GB)..." -ForegroundColor Yellow
    ollama pull qwen2.5-coder:7b
    Write-Host "  OK - Downloaded" -ForegroundColor Green
}

Write-Host ""

# Step 5: Verify
Write-Host "[5/5] Verifying..." -ForegroundColor Yellow
Write-Host ""
ollama list
Write-Host ""

Write-Host "================================" -ForegroundColor Green
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next step:" -ForegroundColor Cyan
Write-Host "  docker-compose restart agentparty-dev" -ForegroundColor White
Write-Host ""
Write-Host "100% Local AI - FREE!" -ForegroundColor Green
Write-Host ""
