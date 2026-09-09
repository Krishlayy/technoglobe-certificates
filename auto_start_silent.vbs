Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd.exe /c ""C:\Certificate\start_background_service.bat""", 0, False
Set WshShell = Nothing
