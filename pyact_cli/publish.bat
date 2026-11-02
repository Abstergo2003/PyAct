"C:\Users\Radek\AppData\Local\Python\pythoncore-3.14-64/python.exe" setup.py sdist bdist_wheel
"C:\Users\Radek\AppData\Local\Python\pythoncore-3.14-64/python.exe" -m twine upload dist/* --verbose
rd /s /q "./build"
rd /s /q "./dist"
rd /s /q "./pyact_cli.egg-info"
PAUSE