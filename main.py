import logging

from logging_config import setup_logging
from variable_config import PASSWORD,HAZF_EZAFE
from moudels import login, check, find_available_offers, print_results, action, write_action, load_lessons
setup_logging()

app_log = logging.getLogger("app")
err_log = logging.getLogger("error")


print(PASSWORD)
if PASSWORD is None:
    err_log.error("PASSWORD is incorrect")
    exit()

s,json_data =  login()

counter = 0
while True:
    
    try:

        lessons = load_lessons()
        ln_list = [i for i in lessons.keys()]
        doihaveit = {i:lessons[i]["ac"] for i in ln_list}
        inexclude = {i:[lessons[i]["fil"]]+lessons[i]["lst"] for i in ln_list}

        check(s,json_data)

        if (HAZF_EZAFE):

            results = find_available_offers(ln_list, inexclude)
            found = print_results(results,doihaveit)

            if found:
                action(s,json_data)
        else:
            
            write_action(ln_list,lessons,doihaveit)
            action(s,json_data)


        counter+=1
        app_log.info(counter)
        print(counter)

    except Exception as e:
        err_log.error(e)
        continue    