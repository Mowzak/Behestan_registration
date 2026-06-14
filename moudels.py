import requests
import json
import logging
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from variable_config import USER, PASSWORD, STUDENT_NUMBER, TERM, FID

app_log = logging.getLogger("app")
err_log = logging.getLogger("error")

post_url='https://ems2.ut.ac.ir/frm/F0414_PROCESS_REGREGISTER020/F0414_PROCESS_REGREGISTER020.svc/'
    
def login():

    session = requests.Session()

    auth_url = "https://sso1.ut.ac.ir/ApiContainer.SSO.RCL1/connect/authorize"

    params = {
        "client_id": "golestanSSO-xRwHTGSHGtjmLJbqr2k9GDSOoai-TCc.apigateway.ut.ac.ir",
        "redirect_uri": "https://ems2.ut.ac.ir/index.html",
        "response_type": "code",
        "scope": "openid",
        "state": "8032122752695"
    }
    r = session.get(auth_url, params=params, allow_redirects=True)

    login_page_url = r.url

    parsed = urlparse(login_page_url)
    qs = parse_qs(parsed.query)
    return_url = qs["ReturnUrl"][0]
    soup = BeautifulSoup(r.text, "html.parser")
    token = soup.find("input", {"name": "__RequestVerificationToken"})["value"]

    login_url = "https://sso1.ut.ac.ir/ApiContainer.SSO.RCL1/Account/Login"

    data = {
        "USERname": USER,
        "Password": PASSWORD,
        "ReturnUrl": return_url,
        "captcha": "",
        "button": "login",
        "RememberLogin": "false",
        "__RequestVerificationToken": token
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": login_page_url,
        "Origin": "https://sso1.ut.ac.ir"
    }
    login_response = session.post(
        login_url,
        data=data,
        headers=headers,
        allow_redirects=True
    )

    final_url = login_response.url

    # print("Final URL:", final_url)

    parsed = urlparse(final_url)
    params = parse_qs(parsed.query)

    if "code" in params:
        code = params["code"][0]

    else:
        err_log.error("Authorization code not found. Login may have failed.EXIT")
        login()
        # raise Exception("Authorization code not found. Login may have failed.EXIT")

        


    payload = {
        "act": "09",
        "r": {
        "code": code,
        "ticket": "",
        "l": "",
        "p": "",
        "d": "0",
        "c": "",
        "rsc": "120",
        "un": STUDENT_NUMBER,
        "ut": "1"
        },
        "rp": {}
    }

    r = session.post(
        "https://ems2.ut.ac.ir/frmc/Authentication/oauth2/",
        json=payload,
        headers={
            "Origin": "https://ems2.ut.ac.ir",
            "Referer": "https://ems2.ut.ac.ir/browser/fa/"
        },
        allow_redirects=True
    )


    stroge = json.loads(r.text)

    json_data = {
        'rp': {
            'ft': '0',
            'f': FID,
            'seq': '18047409',
            'subfrm': '',
            'sid': stroge['oaut']['rp']['sid'],
            'ct': '',
            'sp': '{"UsrType":"0","TrmType":"2"}',
            'ut': '0',
        },
        't': stroge['t'],
        'r': {
            'wIk': [],
            'A32f': TERM,
            'Ajas': STUDENT_NUMBER,
        },
        'act': '09',
        'MaxHlp': 200,
    }

    print("Ss")
    return session,json_data



def action(s,json_data,nosession=False):
    if nosession:
        s,json_data = login()
    wks = (open("./action.txt","r").read()).split('\n')
    if wks==[""]:
        return
    for w in wks:

        json_data['r']['wIk'] = w
            
        response = s.post(
            post_url,
            json=json_data,
        )


        while ("شناسايي" in response.text):
            s,json_data = login()
            json_data['r']['wIk'] = w
                
            response = s.post(
                post_url,
                json=json_data,
            )
        app_log.info(w+'\n'+response.text[:500]+'\n'+"==="*10+'\n')


def check(s,json_data):
    w='[{"ci":28883,"b":0,"g":"13","req":1}]'
    json_data['r']['wIk'] = w
        
    response = s.post(
        post_url,
        json=json_data,
    )

    while ("شناسايي" in response.text):
        s,json_data = login()
        json_data['r']['wIk'] = w
            
        response = s.post(
            post_url,
            json=json_data,
        )   

    with open("information.txt","w",encoding="utf-8") as f:
        pure_data=response.json()
        try:
            for i in json.loads(pure_data['outpar']["wLy"]):
                f.write(str(i)+'\n')
        except Exception as e:
            err_log.error(f"ERROR in check function: {e}")
            check(s,json_data)

        

def load_records():
    records = []
    with open("information.txt", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(eval(line))
            except Exception as e:
                err_log.error(e)
    return records

def find_available_offers(ln_list,inexclude=[]):
    records = load_records()

    ln_to_record = {str(rec["ln"]): rec for rec in records}

    results = []

    for ln in ln_list:
        ln = str(ln)
        rec = ln_to_record.get(ln)

        if rec is None:
            app_log.info(f"[!] ln={ln} not found in file.")
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
                    err_log.error(f"{ln} get passed no exclude/include")
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
            app_log.info(f"[~] ln={ln} (ci={ci}) — no offers with rc < dc found.")

    return results

def print_results(results,doihaveit):


    found = False
    if not results:
        app_log.info("No results found.")
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
                app_log.info(str(wks_found))
                found = True

    return found

def write_action(ln_list,lessons,doihaveit):
    records = load_records()
    with open("action.txt","w") as f:
        for ln in ln_list:

            results = [d for d in records if d["ln"] == ln][0]
            ci = results['ci']
            g = lessons[ln]["lst"][0]
            ac = doihaveit[ln]
            wk = '[{"ci":28883,"b":0,"g":"7777","req":1111}]\n'
            wk = wk.replace("28883",str(ci)).replace("7777",g).replace("1111",str(ac))
            f.write(wk)



def load_lessons(path: str = "lesson.json") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
    