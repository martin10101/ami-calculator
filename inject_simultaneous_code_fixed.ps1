# inject_simultaneous_code_fixed.ps1 - Fixed version
param([string]$PythonFile = "DUAL_PROCESS_GENESIS_NYC_AUTOMATION.py")

Write-Host "Injecting SIMULTANEOUS file opener code into $PythonFile" -ForegroundColor Green

# Check if file exists
if (-not (Test-Path $PythonFile)) {
    Write-Host "Error: File $PythonFile not found!" -ForegroundColor Red
    Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow
    Write-Host "Available Python files:" -ForegroundColor Yellow
    Get-ChildItem *.py | ForEach-Object { Write-Host "   - $($_.Name)" -ForegroundColor Cyan }
    exit 1
}

# Create backup
$backupFile = "$PythonFile.backup_simultaneous"
Copy-Item $PythonFile $backupFile
Write-Host "Created backup: $backupFile" -ForegroundColor Yellow

# Read the file
$content = Get-Content $PythonFile
$newContent = @()
$importAdded = $false
$functionAdded = $false

Write-Host "Processing file..." -ForegroundColor Cyan

foreach ($line in $content) {
    # Add import after selenium imports
    if (($line -match "^from selenium" -or $line -match "^import.*selenium") -and !$importAdded) {
        $newContent += $line
        # Check if this is the last selenium import
        $isLastSeleniumImport = $true
        $currentIndex = [array]::IndexOf($content, $line)
        for ($i = $currentIndex + 1; $i -lt $content.Length; $i++) {
            if ($content[$i] -match "^from selenium" -or $content[$i] -match "^import.*selenium") {
                $isLastSeleniumImport = $false
                break
            }
            if ($content[$i] -match "^from " -or $content[$i] -match "^import ") {
                break
            }
        }
        
        if ($isLastSeleniumImport) {
            $newContent += "from SIMULTANEOUS_FILE_OPENER import start_file_search_now"
            $importAdded = $true
            Write-Host "Added import for simultaneous file opener" -ForegroundColor Green
        }
    }
    # Add function call after "Starting Triple Automation" log
    elseif ($line -match "Starting Triple Automation" -and !$functionAdded) {
        $newContent += $line
        # Add the function call after this line
        $newContent += ""
        $newContent += "        # Launch file opener immediately (simultaneous execution)"
        $newContent += "        start_file_search_now(property_address)"
        $newContent += ""
        $functionAdded = $true
        Write-Host "Added simultaneous file opener call" -ForegroundColor Green
    }
    else {
        $newContent += $line
    }
}

# Write back to file
$newContent | Set-Content $PythonFile

Write-Host ""
Write-Host "SIMULTANEOUS file opener injection completed!" -ForegroundColor Green
Write-Host "Changes made:" -ForegroundColor White
if ($importAdded) {
    Write-Host "   Added import: from SIMULTANEOUS_FILE_OPENER import start_file_search_now" -ForegroundColor Green
} else {
    Write-Host "   Import not added automatically" -ForegroundColor Red
}
if ($functionAdded) {
    Write-Host "   Added function call: start_file_search_now(property_address)" -ForegroundColor Green
} else {
    Write-Host "   Function call not added automatically" -ForegroundColor Red
}

Write-Host ""
Write-Host "File opener now runs IMMEDIATELY when automation starts!" -ForegroundColor Cyan
Write-Host "No waiting for Genesis - completely independent!" -ForegroundColor Cyan

Write-Host ""
Write-Host "To verify changes:" -ForegroundColor White
Write-Host "   findstr `"from SIMULTANEOUS_FILE_OPENER`" $PythonFile" -ForegroundColor Gray
Write-Host "   findstr `"start_file_search_now`" $PythonFile" -ForegroundColor Gray

Write-Host ""
Write-Host "To rollback:" -ForegroundColor Yellow
Write-Host "   Copy-Item $backupFile $PythonFile" -ForegroundColor Gray

