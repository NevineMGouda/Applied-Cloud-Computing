#Task 2
import sys
import ast
import glob
import celery
import logging
from flask import Flask
from collections import Counter
from tasks import count_swedish_pronouns

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/multipleworkers/runtask', methods=['GET'])
def multiple_worker_task():
    global tasks_ids
    tasks_ids = []
    workers_list = []
    # 5 attempts to retrieve the task IDs incase of an error or sleeping workers
    for i in range(5):
        try:
            # gets the current celery app and collects the worker task ids
            workers_list = celery.current_app.control.inspect().stats().keys()
        except AttributeError:
            logger.error("__ACC__: Something went wrong while trying to get the workers List. Trying again...!\n")
            if i == 4:
                sys.exit(0)
            continue
        break
    # This is responsible for distributing the files equally between all workers with an accurate load balancing approach
    workers_count = len(workers_list)
    file_names = glob.glob('data_files/*')
    files_count = len(file_names)
    worker_load = files_count/workers_count

    diff = files_count - (worker_load*workers_count)
    start = 0
    end = worker_load

    for i in range(workers_count):
        if i < diff:
            end = end + 1

        worker_files = file_names[start:end]
        start = end
        end += worker_load
        result = count_swedish_pronouns.delay(worker_files)
        tasks_ids.append(result.id)
    return "Tasks were created and added to workers queue! \n"


@app.route('/multipleworkers/getstatus', methods=['GET'])
def check_status():
    global success
    success = 0
    pending = 0
    if 'tasks_ids' not in globals():
        return "Please run the task before checking the status. You can try curl -i http://<PUBLIC-IP>:5000/" \
               "multipleworkers/runtask \n"
    for task_id in tasks_ids:
        result = count_swedish_pronouns.AsyncResult(task_id)
        if result.state == "SUCCESS":
            success += 1
        else:
            pending += 1
    return str(pending) + " Worker tasks are in PENDING state. And " + str(
        success) + " Worker tasks are in SUCCESS state.\n"


@app.route('/multipleworkers/getresult', methods=['GET'])
def check_result():
    if 'tasks_ids' not in globals():
        return "Please run the task before checking the result. You can try curl -i " \
               "http://<PUBLIC-IP>:5000/multipleworkers/runtask \n"
    if 'success' not in globals():
        workers_status = check_status()
    else:
        workers_status = ""

    if success == len(tasks_ids):
        cumulative_result = Counter({})
        for task_id in tasks_ids:
                result = count_swedish_pronouns.AsyncResult(task_id).get()
                worker_task_result = ast.literal_eval(result)
                worker_task_result_counter = Counter(worker_task_result)
                cumulative_result = cumulative_result + worker_task_result_counter
        cumulative_result = dict(cumulative_result)
        return "RESULT is ready and is equal to: " + str(cumulative_result) + "\n"
    else:
        return "Result is not ready yet. " + workers_status + \
               "You can try curl -i http://<PUBLIC-IP>:5000/multipleworkers/getstatus to check status"

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
