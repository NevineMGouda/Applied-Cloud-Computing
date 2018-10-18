#Task 1
from pronounstasks import count_swedish_pronouns
from flask import Flask

app = Flask(__name__)


@app.route('/pronouns/runtask', methods=['GET'])
def run_task():
    global pronoun_result
    pronoun_result = count_swedish_pronouns.delay()
    return 'Count of Pronouns task have been created and added to queue! \n'

@app.route('/pronouns/getstatus', methods=['GET'])
def check_status():
   if 'pronoun_result' not in globals():
        return "Please run the task before checking the status. You can try curl -i http://<PUBLIC-IP>:5000/pronouns/runtask \n"

   return "The STATUS of the task is: " + str(pronoun_result.state) + ".\n"

@app.route('/pronouns/getresult', methods=['GET'])
def check_result():
   if 'pronoun_result' not in globals():
        return "Please run the task before checking the status. You can try curl -i http://<PUBLIC-IP>:5000/pronouns/runtask \n"
   ready = pronoun_result.ready()
   if (ready == False):
        return "STATUS is " + str(pronoun_result.state) + ". Therefore result is not ready yet. \n"
   else:
        return "RESULT is ready and is equal to: "+ str(pronoun_result.get(timeout=1))+ "\n"

@app.route('/pronouns/executetask', methods=['GET'])
def execute_task():
    result = count_swedish_pronouns.delay()
    return "RESULT is ready and is equal to: " + str(result.get())+ "\n"

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
