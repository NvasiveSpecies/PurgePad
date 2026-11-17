; PC Tools Pack - Windows installer. Needs Inno Setup.
[Setup]
AppName=PC Tools Pack
AppVersion=2.0
DefaultDirName={autopf}\PC Tools Pack
DefaultGroupName=PC Tools Pack
OutputDir=.
OutputBaseFilename=PC-Tools-Pack-Setup
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64

[Files]
Source: "PC-Tools-Pack\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{autodesktop}\PC Tools Pack"; Filename: "{app}\PC-Tools-Pack.exe"
Name: "{group}\PC Tools Pack"; Filename: "{app}\PC-Tools-Pack.exe"

[Run]
Filename: "{app}\PC-Tools-Pack.exe"; Description: "Run PC Tools Pack"; Flags: postinstall nowait skipifsilent
