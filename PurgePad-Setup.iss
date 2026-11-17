; PurgePad - Windows installer. Needs Inno Setup.
[Setup]
AppName=PurgePad
AppVersion=1.0
DefaultDirName={autopf}\PurgePad
DefaultGroupName=PurgePad
OutputDir=.
OutputBaseFilename=PurgePad-Setup
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64

[Files]
Source: "PurgePad\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{autodesktop}\PurgePad"; Filename: "{app}\PurgePad.exe"
Name: "{group}\PurgePad"; Filename: "{app}\PurgePad.exe"

[Run]
Filename: "{app}\PurgePad.exe"; Description: "Run PurgePad"; Flags: postinstall nowait skipifsilent
