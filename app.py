from flask import Flask, render_template
import json
import os
import logging as logger

SECRET_KEY = os.urandom(32)

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY


@app.route('/', methods=['POST', 'GET'])
def main():
    return render_template("main.html", output={})


cwd = os.getcwd()
DIR = os.path.join(cwd, "static/output/compare")
newest_date = ""
if os.path.isdir(DIR):
    yy = os.listdir(DIR)
    DIR = os.path.join(DIR, max(yy))
    mm = os.listdir(DIR)
    DIR = os.path.join(DIR, max(mm))
    dd = os.listdir(DIR)
    DIR = os.path.join(DIR, max(dd))


@app.route('/reload', methods=['POST', 'GET'])
def reload():
    COUNT_OK = 0
    COUNT_NG = 0
    for root, dirs, files in os.walk(DIR):
        for filename in files:
            if "_OK" in filename:
                COUNT_OK += 1
            elif "_NG" in filename:
                COUNT_NG += 1

    with open(os.path.join(cwd, 'cur_result.json'), 'r') as outfile:
        output = json.load(outfile)
        output["img"] = output["img"]
        output["count_ok"] = COUNT_OK
        output["count_ng"] = COUNT_NG
    return render_template("reload.html", output=output)


if __name__ == '__main__':
    logger.debug("Starting Flask Server")

    app.run(host='0.0.0.0', port=5050, debug=True, use_reloader=True)
