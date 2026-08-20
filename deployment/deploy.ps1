# Deployment script for Agentic KPI Builder

$AppName = "agentic-kpi-app"
$ZipName = "$AppName.zip"

Write-Host "Cleaning old build..."
Remove-Item $ZipName -ErrorAction SilentlyContinue

Write-Host "Creating deployment package..."
Compress-Archive -Path `
    app.py,`
    appstategraph.py,`
    .env,`
    requirements.txt, `
    README.md, `
    data/operations_events.csv, `
    kpi\*.py, `
    kpi\tools\*.py, `
    assets\styles.css, `
    deployment\deploy.ps1, `
    tests\*.py, `
    workflow\*.py, `
    workflow\*.json, `
    workflow\*.yaml, `
    images\*.png, `
    docker\dockerfile, `
    dockerCompose/docker-compose.yml, `
    ak8/*.yaml `
    -DestinationPath $ZipName

Write-Host "Deployment package created: $ZipName"
