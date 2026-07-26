# Unified startup script for AI Resume Analyzer
# Runs: Backend (FastAPI) + Frontend (Vite) + ngrok tunnel

param(
    [switch]$Ngrok,
    [string]$NgrokDomain = "",
    [int]$BackendPort = 8000,
    [int]$FrontendPort = 5173
)

$ErrorActionPreference = "Stop"

function Write-Log($msg, $color = "Green") {
    Write-Host "[$(Get-Date -Format "HH:mm:ss")] $msg" -ForegroundColor $color
}

function Check-Command($cmd) {
    $path = (Get-Command $cmd -ErrorAction SilentlyContinue).Source
    if (-not $path) {
        Write-Log "ERROR: $cmd not found in PATH" Red
        return $false
    }
    return $true
}

# Check prerequisites
Write-Log "Checking prerequisites..."
$ok = $true
$ok = Check-Command "python" -and $ok
$ok = Check-Command "npm" -and $ok
$ok = Check-Command "tesseract" -and $ok
$ok = Check-Command "pdftoppm" -and $ok

if (-not $ok) {
    Write-Log "Missing prerequisites. Please install: Python, Node.js, Tesseract OCR, Poppler" Red
    exit 1
}

# Paths
$root = "C:\Users\lhnhan\PycharmProjects\Ai_Resume_Analyzer"
$backendDir = "$root\backend"
$frontendDir = "$root\frontend"

# Start Backend
Write-Log "Starting Backend on port $BackendPort..."
$backendProc = Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "cd /d `"$backendDir`" && .\.venv\Scripts\Activate.ps1 && uvicorn app.main:app --reload --port $BackendPort" -PassThru -WindowStyle Hidden

Start-Sleep 3

# Start Frontend
Write-Log "Starting Frontend on port $FrontendPort..."
$frontendProc = Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "cd /d `"$frontendDir`" && npm run dev -- --port $FrontendPort --host" -PassThru -WindowStyle Hidden

Start-Sleep 3

$urls = @()

# ngrok
if ($Ngrok) {
    if (Check-Command "ngrok") {
        Write-Log "Starting ngrok..."
        
        # Backend tunnel
        $ngrokBackend = Start-Process -FilePath "ngrok" -ArgumentList "http", $BackendPort, "--log=stdout" -PassThru -WindowStyle Hidden
        
        # Frontend tunnel (optional)
        $ngrokFrontend = Start-Process -FilePath "ngrok" -ArgumentList "http", $FrontendPort, "--log=stdout" -PassThru -WindowStyle Hidden
        
        Start-Sleep 3
        
        # Get ngrok URLs
        try {
            $api = Invoke-RestMethod "http://localhost:4040/api/tunnels"
            foreach ($tunnel in $api.tunnels) {
                Write-Log "ngrok: $($tunnel.public_url) -> $($tunnel.config.addr)" Cyan
                $urls += $tunnel.public_url
            }
        } catch {
            Write-Log "Could not fetch ngrok URLs" Yellow
        }
    } else {
        Write-Log "ngrok not found, skipping..." Yellow
    }
}

Write-Log "=== SERVICES RUNNING ===" Cyan
Write-Log "Backend:  http://localhost:$BackendPort"
Write-Log "Frontend: http://localhost:$FrontendPort"
if ($urls) {
    Write-Log "ngrok URLs:" Cyan
    $urls | ForEach-Object { Write-Log "  $_" Cyan }
}
Write-Log ""
Write-Log "Press Ctrl+C to stop all services" Yellow

# Wait for exit
try {
    $backendProc.WaitForExit()
    $frontendProc.WaitForExit()
} finally {
    Write-Log "Stopping services..."
    Stop-Process -Id $backendProc.Id -Force -ErrorAction SilentlyContinue
    Stop-Process -Id $frontendProc.Id -Force -ErrorAction SilentlyContinue
    if ($Ngrok) {
        Get-Process ngrok -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    }
}

