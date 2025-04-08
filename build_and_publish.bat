@REM Require
@REM - build
@REM - hatchling
@REM - twine

python -m build
twine upload dist/*
@REM twine upload --repository testpypi dist/*
