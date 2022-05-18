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

# Cd to this dir for safety, ensure smooth running
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

app = Flask(__name__)

@app.route("/")
def index():
    return redirect("https://github.com/Vortetty/readme-monomatch", code=308)

@app.route("/monomatch/card/<card_id>")
def card(card_id):
    if card_id == 0:
        return send_file("./cards/0.png")
    elif card_id == 1:
        return send_file("./cards/1.png")
    else:
        abort(404)

@app.errorhandler(404)
def page_not_found(error):
   return render_template('404.html', title = '404'), 404

def main():
    serve(app, host="0.0.0.0", port=8080)

if __name__ == "__main__":
    os.environ.update({
        "FLASK_ENV": "development",
        "FLASK_DEBUG": "1"
    })
    app.run(debug=True, port=8080)
