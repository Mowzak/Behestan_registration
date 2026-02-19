from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.chrome.options import Options
from time import sleep
import requests
import json
import pyautogui
import ast
import os



# options = Options()
# options.add_argument('--headless')  # Headless mode
# options.add_argument('--no-sandbox')
# options.add_argument('--disable-dev-shm-usage')
# options.add_argument('--disable-gpu')
# options.add_argument('--window-size=1920,1080')  


user = "mm.yadi"
pas = os.getenv("UTPASS")
post_url='https://ems2.ut.ac.ir/frm/F0414_PROCESS_REGREGISTER020/F0414_PROCESS_REGREGISTER020.svc/'


# dev  = webdriver.Chrome()
dev  = webdriver.Firefox()
# dev.maximize_window()
# dev  = webdriver.Chrome(options=options)
def login(first):


    dev.get("https://ems2.ut.ac.ir/browser/fa/#/auth/login")
    dev.refresh()
    try:
        (WebDriverWait(dev,10).until(EC.presence_of_element_located((By.XPATH,'/html/body/app-root/app-auth/nb-layout/div/div/div/div/div/nb-layout-column/div/div/div/div[2]/div/div[5]/app-login/div[1]/button')))).click() 
    
    except:
        try:
            (WebDriverWait(dev,10).until(EC.presence_of_element_located((By.XPATH,'/html/body/app-root/app-pages/app-one-column-layout/nb-layout/div[1]/div/div/div/div/nb-layout-column/div/div/app-home/div/app-working-table/div/div/app-desktop-sidebar/div/div[1]/app-np-box-template[2]/nb-card/nb-card-body/app-np-list-template/nb-list/nb-list-item[1]/div/div[4]/a')))).click() 
        except:
            login(False)
    
    if first:

        (WebDriverWait(dev,10).until(EC.presence_of_element_located((By.ID,'Username')))).send_keys(user) 
        (WebDriverWait(dev,10).until(EC.presence_of_element_located((By.ID,'password')))).send_keys(pas)
        (WebDriverWait(dev,10).until(EC.presence_of_element_located((By.NAME,'button')))).click() 

    dev.get("https://ems2.ut.ac.ir/browser/fa/")

    try:
        (WebDriverWait(dev,10).until(EC.presence_of_element_located((By.XPATH,'/html/body/app-root/app-pages/app-one-column-layout/nb-layout/div[1]/div/div/div/div/nb-layout-column/div/div/app-home/div/app-working-table/div/div/app-desktop-sidebar/div/div[1]/app-np-box-template[2]/nb-card/nb-card-body/app-np-list-template/nb-list/nb-list-item[1]/div/div[4]/a')))).click() 
    except:
        login(False)        
    while True:
        stroge = dev.execute_script("""
        const out = {};
        for (let i = 0; i < window.localStorage.length; i++) {
            const k = window.localStorage.key(i);
            out[k] = window.localStorage.getItem(k);
        }
        return out;
        """)
        try:
            stroge["t"]
            break
        except:
            continue


    cookie = dev.get_cookies()
    # print(cookie)
   

    # print(stroge)  


    s = requests.Session()

    for c in cookie:
        s.cookies.set(
            name=c["name"],
            value=c["value"],
            domain=c.get("domain"),
            path=c.get("path", "/"),
        )


    s.get("https://ems2.ut.ac.ir/browser/fa/#/pages")




    json_data = {
        'rp': {
            'ft': '0',
            'f': '12100',
            'seq': '18047409',
            'subfrm': '',
            'sid': stroge['sid'],
            'ct': '',
            'sp': '{"UsrType":"0","TrmType":"2"}',
            'ut': '0',
        },
        't': stroge['t'],
        'r': {
            'wIk': [],
            'A32f': '4042',
            'Ajas': '810403324',
        },
        'act': '09',
        'MaxHlp': 200,
    }

    s.headers.update({
        'Cookie':cookie[0]["name"]+"="+cookie[0]["value"]+"; p="+cookie[1]["value"],
    })

    return s,json_data


def action(s,json_data):
    wks = (open("./action.txt","r").read()).split('\n')
    for w in wks:

        json_data['r']['wIk'] = w
            
        response = s.post(
            post_url,
            json=json_data,
        )


        while ("شناسايي" in response.text):
            s,json_data = login(False)
            json_data['r']['wIk'] = w
                
            response = s.post(
                post_url,
                json=json_data,
            )

        with open("log.txt","a",encoding="utf-8") as f:
            f.write(w+'\n'+response.text[:500]+'\n'+"==="*10+'\n')


def check(s,json_data):
    w='[{"ci":28883,"b":0,"g":"13","req":1}]'
    json_data['r']['wIk'] = w
        
    response = s.post(
        post_url,
        json=json_data,
    )


    while ("شناسايي" in response.text):
        s,json_data = login(False)
        json_data['r']['wIk'] = w
            
        response = s.post(
            post_url,
            json=json_data,
        )   
    with open("information.txt","w",encoding="utf-8") as f:
        pure_data=response.json()
        for i in json.loads(pure_data['outpar']["wLy"]):

            f.write(str(i)+'\n')
        

def load_records(filepath):
    records = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(ast.literal_eval(line))
            except Exception as e:
                print(e)
    return records

def find_available_offers(ln_list, filepath="information.txt",inexclude=[]):
    records = load_records(filepath)

    ln_to_record = {str(rec["ln"]): rec for rec in records}

    results = []

    for ln in ln_list:
        ln = str(ln)
        rec = ln_to_record.get(ln)

        if rec is None:
            print(f"[!] ln={ln} not found in file.")
            continue

        ci = rec["ci"]
        course_name = rec.get("n", "")
        matching_offers = []

        for ofr in rec.get("ofr", []):
            match inexclude[ln][0]:
                case "e":
                    if ofr["g"] in inexclude[ln]:
                        continue
                case "i":
                    if not(ofr["g"] in inexclude[ln]):
                        continue
                case _:
                    print(f"{ln} get passed no exclude/include")
                    pass
            rc = ofr.get("rc", 0)
            dc = ofr.get("dc", 0)
            if rc < dc:
                matching_offers.append({
                    "g":  ofr["g"],
                    "rc": rc,
                    "dc": dc,
                    "available_seats": dc - rc
                })

        if matching_offers:
            results.append({
                "ln":      ln,
                "ci":      ci,
                "name":    course_name,
                "offers":  matching_offers
            })
        else:
            print(f"[~] ln={ln} (ci={ci}) — no offers with rc < dc found.")

    return results

def print_results(results,doihaveit):


    found = False
    if not results:
        print("No results found.")
        return found
    
    with open("action.txt","w") as f:
        for entry in results:
            for ofr in entry["offers"]:
                wks_found=[]
                wk = {}
                wk["ci"] = entry['ci']
                wk["b"] = 0
                wk["g"] = ofr['g']
                wk["req"] = doihaveit[entry['ln']]
                wks_found.append(wk)
                wks_found = str(wks_found).replace("'",'"').replace(" ","")
                f.write(str(wks_found))
                print(wks_found)
                found = True

    return found


lessons = eval(open("lesson.json","r").read())
my_ln_list = [i for i in lessons.keys()]

#### 3list entezar 5taghirgroh 4hazf 1sabt
doihaveit = {i:lessons[i]["ac"] for i in my_ln_list}
##this can be include, edit all exlude var and put a false befor condition
inexclude = {i:[lessons[i]["fil"]]+lessons[i]["lst"] for i in my_ln_list}
#8104269 kargah     1120018 zaban  8104389 az shimi
counter=0

s,json_data =  login(True)
open("log.txt",'w')
while True:
    counter+=1
    pyautogui.click()
    check(s,json_data)
    results = find_available_offers(my_ln_list, inexclude=inexclude,filepath="information.txt",)
    found = print_results(results,doihaveit),
    if found:
        action(s,json_data)
    print(counter)


    