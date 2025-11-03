# Activate virtual environment and clear any conflicting Django environment variables
# This prevents conflicts with other Django projects

# Clear the DJANGO_SETTINGS_MODULE if it exists
$env:DJANGO_SETTINGS_MODULE = ""

# Activate the virtual environment
& ".\venv\Scripts\Activate.ps1"

Write-Host "Virtual environment activated and Django settings cleared!" -ForegroundColor Green
Write-Host "You can now run Django commands safely." -ForegroundColor Green
