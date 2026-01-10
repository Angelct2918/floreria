Param(
    [string]$Base = "D:\FLORERIA-BARTOLO\josbet-florist"
)

$dirs = @('css','js','images','assets')
foreach ($d in $dirs) {
    $p = Join-Path $Base $d
    if (-not (Test-Path $p)) {
        New-Item -ItemType Directory -Path $p | Out-Null
        Write-Host "Creado: $p" -ForegroundColor Green
    } else {
        Write-Host "Ya existe: $p" -ForegroundColor Yellow
    }
}

Write-Host "Estructura creada/verificada en: $Base" -ForegroundColor Cyan
Write-Host "Puedes arrastrar las imágenes a $Base\images y luego abrir index.html en el navegador." -ForegroundColor Cyan
