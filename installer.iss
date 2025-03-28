[Setup]
AppName=Hello PyQt
AppVersion=1.0
DefaultDirName={pf}\HelloPyQt
DefaultGroupName=Hello PyQt
UninstallDisplayIcon={app}\MyApp.exe
OutputDir=output
OutputBaseFilename=HelloPyQtInstaller
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\MyApp.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "resources\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\Hello PyQt"; Filename: "{app}\MyApp.exe"
Name: "{commondesktop}\Hello PyQt"; Filename: "{app}\MyApp.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "其他任务"
