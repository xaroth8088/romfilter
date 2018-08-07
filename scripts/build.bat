rmdir /S /Q build
rmdir /S /Q dist
pyinstaller --onefile --windowed __main__.py
rmdir /S /Q build
move dist\__main__.exe dist\romfilter.exe
