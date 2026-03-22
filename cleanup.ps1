# Cleanup script for EduTrack workspace
$unwantedFiles = @(
    'tempCodeRunnerFile.py',
    'fire_cert.pdf',
    'test_fire_cert.jpg',
    'COMPLETION_SUMMARY.md',
    'EXECUTION_COMPLETE.md',
    'FILE_STRUCTURE_AND_CHANGES.md',
    'FRONTEND_COLOR_PALETTE_COMPLETE.md',
    'FRONTEND_COMPLETE.md',
    'FRONTEND_SETUP_COMPLETE.md',
    'IMPLEMENTATION_VERIFICATION_CHECKLIST.md',
    'LAUNCH_GUIDE.md',
    'PROJECT_COMPLETION.md',
    'README_DOCUMENTATION_INDEX.md',
    'risk_model.pkl',
    'scaler.pkl'
)

$projectRoot = 'c:\edutech'

# Remove files
foreach ($file in $unwantedFiles) {
    $filePath = Join-Path $projectRoot $file
    if (Test-Path $filePath) {
        Remove-Item $filePath -Force
        Write-Host "Removed: $file"
    }
}

# Remove __pycache__ directories recursively
Get-ChildItem -Path $projectRoot -Name '__pycache__' -Directory -Recurse | ForEach-Object {
    $cachePath = Join-Path $projectRoot $_
    Remove-Item $cachePath -Recurse -Force
    Write-Host "Removed: $_"
}

Write-Host "Cleanup complete!"
