@REM Require
@REM - build
@REM - hatchling
@REM - twine

.venv\Scripts\python.exe -m build
.venv\Scripts\twine.exe upload dist/*
@REM .venv\Scripts\twine.exe upload --repository testpypi dist/*
