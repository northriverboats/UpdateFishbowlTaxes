# UpdateFishbowlTaxes
Update the tax tables for States that are currently in Fishbowl. Any current 
rate is UPDATEd, any new rate is INSERTED. There must be a mapping between 
the state abreviation and the fishbowl ID for the state. The CSV files 
contain one state but the program is capable of procssing csv files 
containing multiple states.

Currently the program can only process one  `csv` at a time. That `csv` file 
must be passed via the environmental variable `FILE`. A gui is to be added at 
a later point to allow Windows users to drag-n-drop a `csv` to update with.

## Requirements
Any modern version of Python3.9+ should do. At the time of writing the current 
version is Python 3.11. The infomration and credentials for read only database 
access to the fishbowl server is also required.

Also the Firebird 2.5.x client driver `fbclient.dll` is requered.

## Installing
1. Clone from github
2. Setup directory as at least a python3.9 venv
3. Activate venv
4. Update pip
5. Install wheel
6. Install requirements.txt
7. Copy `env.sample` to `.env` and populate with information

Additionally for Windows install the `fbclient.dll` drives as needed.

```
git clone git@github.com:northriverboats/UpdateFishbowlTaxes.git
cd UpdateFishbowlTaxes

# For Linux
python3.11 -m venv
source venv/bin/activate

# For Windows
"\Program Files\python311\python" -m venv venv
venv\Scripts\activate

python -m pip install --upgrade pip
pip install wheel
pip install -r requirements.txt

cp env.sample .env
```
## Installing the fbclient.dll driver
The `fblcient.dll` is required for this program to run

1. The fishbowl server software installs this driver.
2. Versons `fbclient32.dll` and `fbclient64.dll` do not work.
3. No need to install the server version, just place the `fbclient.dll` in `C:\Prgram Files\Fishbowl\database\bin` folder and install the Firebird.reg file.
4. If this program crahses and keeps `fbclient.dll` open, if you run Fishbowl you will get an error that the Fisbhowl server can not be ound.
5. If Fisbhbowl is running, then this script will fail to run properly.

The registry key that tells `fdb` where to find `fbclient.dll`:
```
SOFTWARE\\Firebird Project\\Firebird Server\\Instances
```
The contents of the `Firebird.reg` file:
```
Windows Registry Editor Version 5.00

[HKEY_LOCAL_MACHINE\SOFTWARE\Firebird Project\Firebird Server\Instances]
"DefaultInstance"="C:\\Program Files\\Fishbowl\\database\\"
```

## Running
1. Activate venv
2. In `.env` update the `FILE=` entry to reflect the `csv` file to import
3. Run `updatefishbowltaxes.py` 

## Creating an Executable
Use:
```
pyinstaller.exe updatefishbowltaxes.spec
```
Inital setup can be done with:
```
pyinstaller.exe --onefile --noconsole --add-data ".env;." -i Taxes.ico updatefishbowltaxes.py
```

## Todo
* Create Graphic UI
* GUI allowing drag-n-drop of csv files
* Displaying statistics before processing files
* Create `.spec` file for pyinstaller
* Update Documentation
