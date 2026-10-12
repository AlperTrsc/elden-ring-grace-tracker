Add-Type -AssemblyName System.Drawing

$inputPath = (Resolve-Path "web/assets/elden_ring_map_raw.jpg").Path
$outputPath = Join-Path (Split-Path $inputPath) "map_lands_between.jpg"

$src = [System.Drawing.Image]::FromFile($inputPath)
Write-Host "Original dimensions: $($src.Width) x $($src.Height)"

# Target width 2400px with high quality bicubic interpolation
$targetWidth = 2400
$targetHeight = [int]($src.Height * ($targetWidth / $src.Width))

$dest = New-Object System.Drawing.Bitmap $targetWidth, $targetHeight
$graph = [System.Drawing.Graphics]::FromImage($dest)
$graph.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$graph.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
$graph.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
$graph.CompositingQuality = [System.Drawing.Drawing2D.CompositingQuality]::HighQuality

$graph.DrawImage($src, 0, 0, $targetWidth, $targetHeight)

# Save with 85% JPEG quality for fast loading
$codec = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq 'image/jpeg' }
$encoderParams = New-Object System.Drawing.Imaging.EncoderParameters(1)
$encoderParams.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter([System.Drawing.Imaging.Encoder]::Quality, [long]85)

$dest.Save($outputPath, $codec, $encoderParams)

$graph.Dispose()
$dest.Dispose()
$src.Dispose()

Write-Host "Saved optimized map to $outputPath ($targetWidth x $targetHeight)"
