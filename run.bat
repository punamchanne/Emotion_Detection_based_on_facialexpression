@echo off
echo Starting Emotion Music Recommendation System...
echo using virtual environment .venv_fix

:: Fix for potential hangs
set OMP_NUM_THREADS=1
set TF_ENABLE_ONEDNN_OPTS=0

.\.venv_fix\Scripts\python.exe app.py
pause
