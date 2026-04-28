while (Get-Process pip -ErrorAction SilentlyContinue) { Start-Sleep -Seconds 5 }
Start-Process -NoNewWindow -FilePath ".\.venv\Scripts\uvicorn.exe" -ArgumentList "api:app --host 127.0.0.1 --port 8000"
Start-Sleep -Seconds 10
Start-Process -NoNewWindow -FilePath ".\.venv\Scripts\streamlit.exe" -ArgumentList "run app.py"
Write-Host "Services started!"
