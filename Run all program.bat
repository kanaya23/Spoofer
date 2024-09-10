@echo off
echo Running all spoofing scripts...

echo Running GEOPOOF.py...
python GEOPOOF.py

echo Running hwidhinf.py...
python hwidhinf.py

echo Running IP SPOOF.py...
python "IP SPOOF.py"

echo Running WINSPOOF.py...
python WINSPOOF.py

echo All spoofing scripts have been executed.
pause