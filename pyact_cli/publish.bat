python setup.py sdist bdist_wheel
python -m twine upload dist/* --verbose
rd /s /q "./build"
rd /s /q "./dist"
rd /s /q "./pyact_cli.egg-info"
PAUSE