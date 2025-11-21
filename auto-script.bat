@echo off
REM =============================
REM Open important web links 
REM =============================

REM Open Azure DevOps work items assigned to you
start https://dev.azure.com/raboweb-ftbtr/FtBtR/_workitems/assignedtome/

REM Open Rabobank service desk tickets
start https://service.rabobank.nl/tickets?area=4&mainview=team&viewid=1&selid=8803&sellevel=2&selparentid=wrt%20mt%20murex%20production%20services%20murex

REM Open useful GitHub project/tool
start https://ajayparihar.github.io/Compy2.0/

REM =============================
REM Launch frequently used applications
REM =============================

REM Open Microsoft Outlook
start OUTLOOK.exe

REM =============================
REM Open a specific folder in VS Code with Explorer view
REM =============================

REM Set the folder path you want to open in VS Code
set folderPath=C:UsersSinghA14OneDrive - RabowebDocumentsSaves

REM Set the path for VS Code executable
set vscodePath="C:UsersSinghA14AppDataLocalProgramsMicrosoft VS CodeCode.exe"

REM Open the folder in VS Code with specific flags
start "" %vscodePath% --force-node-api-uncaught-exceptions-policy=true "%folderPath%"