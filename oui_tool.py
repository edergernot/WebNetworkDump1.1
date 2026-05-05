
import requests
import datetime
from collections import defaultdict
import json

OUI_File="OUI.txt"

def check_local_ouifile(): 
    '''
    Checks if OUI-File exists and its older than 30 Days
    '''
    import os
    if os.path.exists(OUI_File):
        print("OUI-File Exists")
        with open(OUI_File, "r")as file:
            line = file.readline()
        try :
            date=int(line[-8::])
        except TypeError:
            return(False)
        now = datetime.datetime.now()
        date_str=datetime.datetime.strptime(line[-9:-1:],"%Y%m%d")
        datediff=(now-date_str).days
        if  datediff < 30:
            print("OUI-File is not older than 30 days")
            return(True)
        else:
            print(f"File is {datediff} days old")
            return(False)
    else :
        print("Local OUI-File dont exist")
        return(False)

    
def download_oui_file():
    '''
    Download the file from IEEE
    '''
    now = datetime.datetime.now()
    now_str=now.strftime("%Y%m%d")
    if check_local_ouifile():  #file exists and is younger than 30 Days
        return()
    OUI_URL="https://standards-oui.ieee.org"
    UserAgent={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"}
    print("File get downloadet ...")
    OUI = requests.get(OUI_URL,headers=UserAgent)
    if OUI.reason != "OK":
        print("There was an error getting the file from IEEE")
        return()
    with open(OUI_File,"w") as file:
        file.write(f"Created at {now_str}\n\n")
        file.write(f"{OUI.text}")
    return

def parse_oui_file():
    global oui_to_org
    oui_to_org = {}
    global org_to_ouis 
    org_to_ouis = defaultdict(list)

    with open(OUI_File, "r") as file:
        f=file.read()
    for line in f.split("\n"):
        if "(hex)" in line:
            parts = line.split("(hex)")
            oui = parts[0].strip().replace("-", "").lower()
            org_parts = parts[1].split(",")
            org = org_parts[0].strip()
            oui_to_org[oui] = org.upper()
            org_to_ouis[org.upper()].append(oui)
    
    json_file = "oui.json"
    with open(json_file, "w") as f:
        json.dump({"oui_to_org": oui_to_org, "org_to_ouis": dict(org_to_ouis)},f)


if __name__ == "__main__":
    print("Prechecks...")
    download_oui_file()
    print("Try to parse the File")
    parse_oui_file()
    print("File parsed!")










