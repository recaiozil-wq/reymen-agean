Add-Type -AssemblyName System.Windows.Forms
$wshell = New-Object -ComObject WScript.Shell
# aktif pencereye odaklan ve Alt+PrtScn’i gönder
$wshell.SendKeys('%{PRTSC}')
Start-Sleep -Milliseconds 800
$img = [System.Windows.Forms.Clipboard]::GetImage()
if ($img -ne $null) {
  $out = 'C:\Users\marko\Desktop\ekran_gorselleri\aktif_pencere.png'
  $dir = Split-Path $out
  if (-not (Test-Path $dir)) { New-Item -Path $dir -ItemType Directory | Out-Null }
  $img.Save($out)
  Write-Output "OK saved to $out"
  exit 0
} else {
  Write-Output 'HATA: pano bos'
  exit 1
}
