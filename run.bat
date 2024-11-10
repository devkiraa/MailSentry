@echo off
IF NOT EXIST ".installed" (
    echo Installing dependencies...
    pip install -r requirements.txt

    :: Check if pip install was successful
    IF %ERRORLEVEL% NEQ 0 (
        echo Installation failed. Please check the errors above.
        pause
        exit /b %ERRORLEVEL%
    )

    echo Dependencies installed successfully.

    :: Create a marker file to indicate that dependencies are installed
    echo Installed > .installed
) ELSE (
    echo Dependencies already installed.
)

:: Run the Python mail server script
echo Running the mail server...
python mail-server.py

:: Close the terminal window after the script has started
exit
