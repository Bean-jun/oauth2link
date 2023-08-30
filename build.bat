rd /S /Q build
rd /S /Q oauth2link.egg-info
del /Q dist\*
python setup.py bdist_wheel
python -m twine upload dist/*