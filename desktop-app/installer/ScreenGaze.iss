; Inno Setup script for ScreenGaze (Windows installer)
; Build:
;   iscc ScreenGaze.iss

#define AppName "ScreenGaze"
#define AppPublisher "AttentionAgent"
#define AppExeName "ScreenGaze.exe"

[Setup]
AppId={{C9D9BFC5-4E88-4E7B-A32E-7E6D2BC1F95D}
AppName={#AppName}
AppVersion=1.0.0
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
Compression=lzma
SolidCompression=yes
OutputDir=Output
OutputBaseFilename={#AppName}-Setup
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "..\\dist\\ScreenGaze\\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{commondesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent

