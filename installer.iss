; Inno Setup Script for NoSleep Application
; The AppId is the unique identifier for this application.
; Do not use the same AppId for other projects.

[Setup]
; Place your generated GUID here. Double '{{' is required to escape the character.
AppId={{94856465-36D1-4375-8AA5-174CB59EB8E5}
AppName=NoSleep
AppVersion=1.0
AppPublisher=Stepan Capsamun
; {autopf} points to the standard Program Files directory
DefaultDirName={autopf}\NoSleep
DefaultGroupName=NoSleep
AllowNoIcons=yes
; Installer file settings
OutputDir=.
OutputBaseFilename=NoSleepInstaller
SetupIconFile=src\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Source: The path to your compiled .exe (ensure it is in the 'dist' folder)
Source: "dist\NoSleep.exe"; DestDir: "{app}"; Flags: ignoreversion
; Include the icon file for logs and system tray usage
Source: "src\icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu and Desktop shortcuts
Name: "{group}\NoSleep"; Filename: "{app}\NoSleep.exe"; IconFilename: "{app}\icon.ico"
Name: "{autodesktop}\NoSleep"; Filename: "{app}\NoSleep.exe"; Tasks: desktopicon; IconFilename: "{app}\icon.ico"

[Run]
; Launch the application automatically after the installation finishes
Filename: "{app}\NoSleep.exe"; Description: "{cm:LaunchProgram,NoSleep}"; Flags: nowait postinstall skipifsilent