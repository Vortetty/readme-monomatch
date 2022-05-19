# Copyright 2022 Winter/Vortetty
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
from flask import Flask, redirect, send_file, abort, render_template
from waitress import serve
import os
from werkzeug.exceptions import HTTPException

# Cd to this dir for safety, ensure smooth running
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
# os.chdir(dname)

app = Flask(__name__)

class abortReason (HTTPException):
    def __init__(self, code: int, reason: str=""):
        self.code = code
        self.reason = reason

@app.route("/")
def index():
    return redirect("https://github.com/Vortetty/readme-monomatch", code=308)

@app.route("/monomatch/card/<card_id>")
def card(card_id: str):
    if int(card_id) == 0:
        try:
            return send_file(os.path.join(dname, "cards/0.png"))
        except FileNotFoundError:
            #raise abortReason(404)
            return send_file(os.path.join(dname, "404.png"))
    elif int(card_id) == 1:
        try:
            return send_file(os.path.join(dname, "cards/1.png"))
        except FileNotFoundError:
            #raise abortReason(404)
            return send_file(os.path.join(dname, "404.png"))
    else:
        raise abortReason(403)

@app.route("/monomatch/icon/<filetype>")
@app.route("/monomatch/icon/<filetype>/<icon_id>")
def icon(filetype: str, icon_id: str|None=None):
    if icon_id == None:
        raise abortReason(403, reason="No icon id was provided")
    if not icon_id.isdigit() or icon_id.find(".") != -1 or int(icon_id) < 0:
        raise abortReason(403, reason="Icon id must be a positive whole number")
    elif icon_id.find("\\") != -1 or icon_id.find("/") != -1:
        raise abortReason(403, reason="It seems you may have attempted to use a path to hack this, good try but no.")

    try:
        if filetype.lower() == "png":
            return send_file(f"generator/symbols/png/{int(icon_id)}.png")
        elif filetype.lower() == "svg":
            return send_file(f"generator/symbols/{int(icon_id)}.svg")
        else:
            raise abortReason(404, reason="Filetype not supported")
    except FileNotFoundError as e:
        raise abortReason(404, reason=f"Invalid image ID, valid range is 0-{len(os.listdir(os.path.join(dname, 'generator/symbols/png')))-1}")

@app.errorhandler(abortReason)
def page_not_found(error: abortReason):
    if error.code == 403:
        return render_template('error_message.html', errorCode='403', errorMessage="Forbidden", errorReason=error.reason), 403
    elif error.code == 404:
        return render_template('error_message.html', errorCode='404', errorMessage="Resource not found", errorReason=error.reason), 404

def main():
    serve(app, host="0.0.0.0", port=8080)

if __name__ == "__main__":
    os.environ.update({
        "FLASK_ENV": "development",
        "FLASK_DEBUG": "1"
    })
    app.run(debug=True, port=8080) #, use_reloader=False)
