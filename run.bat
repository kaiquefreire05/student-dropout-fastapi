@echo off
chcp 65001 > nul
echo ========================================================
echo   Iniciando Student Dropout Prediction API (FastAPI)
echo ========================================================
echo.

REM Verifica se os artefatos do modelo existem
if not exist "models\best_model.joblib" (
    echo [*] Modelo nao encontrado. Executando treinamento...
    python scripts\train.py
)

echo [*] Iniciando servidor Uvicorn em http://127.0.0.1:8000
echo [*] Documentacao Swagger disponivel em: http://127.0.0.1:8000/docs
echo [*] Interface Web disponivel em: http://127.0.0.1:8000/
echo.
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause
