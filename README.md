# FileSync_ARS

A file synchronization project inspired by FreeFileSync with some tweaks, changes, and improvements. 

## Highlights

*	Modern and simplistic UI thanks to the PyQt – a popular cross-platform GUI toolkit.
*	Automation mode to launch the application minimized and execute a set of pre-defined functions on startup.
*	Watchdog implementation for monitoring file changes.
*	Extended sync attributes.
*	Ability to reference a media drive by its volume name.
*	YAML configuration autosave & load.
*	Input data validation and QOL end-user improvements.
*	Tray icon & menu implementation.
*	All functions aggregated to a singular dashboard in contrast to FreeFileSync.

## Note

* Due to extensive use of Windows Management Instrumentation (WMI), this application is limited to Windows-based systems for now only, unfortunately. 
* Windows 10/11 recommended.

## Prerequisites
The following command will install the packages according to the configuration file "requirements.txt"
```
pip install -r requirements.txt
```
Put requirements.txt in the directory where the command will be executed. If it is in another directory, specify its path like path/to/requirements.txt.

## Usage
* Run the ARS_GUI.py.
* Done!
