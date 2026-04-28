while (Get-Process pip -ErrorAction SilentlyContinue) { Start-Sleep -Seconds 5 }
.\.venv\Scripts\python -m pip freeze > requirements.txt
Write-Host "Froze requirements.txt."
Remove-Item -Path ".venv" -Recurse -Force
Write-Host "Deleted .venv."
python -m venv .venv
Write-Host "Created new .venv. Reinstalling from frozen requirements..."
.\.venv\Scripts\python -m pip install -r requirements.txt
Write-Host "Reinstall complete."
