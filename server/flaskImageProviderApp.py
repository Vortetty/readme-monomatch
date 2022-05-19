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

try:
    match "":
        case "":
            pass
except:
    print("This program requires python >=3.10.0 due to the use of match/case")

import json
from flask import Flask, redirect, send_file, abort, render_template
from flask_compress import Compress
from waitress import serve
import os
from werkzeug.exceptions import HTTPException

# Cd to this dir for safety, ensure smooth running
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
# os.chdir(dname)

app = Flask(__name__)
Compress(app)

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
    errorMessageText = ""
    match error.code: # Match every standard error code defined by mozilla (https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
                      # 100, 101, 102, 103
                      # 200, 201, 202, 203, 204, 205, 206, 207, 208, 226
                      # 300, 301, 302, 303, 304, 305, 306, 307, 308
                      # 400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 421, 422, 423, 424, 425, 426, 426, 428, 429, 431, 451
                      # 500, 501, 502, 503, 504, 505, 506, 507, 508, 510, 511
        case 100: errorMessageText = "Continue"
        case 101: errorMessageText = "Switching Protocols"
        case 102: errorMessageText = "Processing"
        case 103: errorMessageText = "Early Hints"
        case 200: errorMessageText = "OK"
        case 201: errorMessageText = "Created"
        case 202: errorMessageText = "Accepted"
        case 203: errorMessageText = "Non-Authoritative Information"
        case 204: errorMessageText = "No Content"
        case 205: errorMessageText = "Reset Content"
        case 206: errorMessageText = "Partial Content"
        case 207: errorMessageText = "Multi-Status"
        case 208: errorMessageText = "Already Reported"
        case 226: errorMessageText = "IM Used"
        case 300: errorMessageText = "Multiple Choices"
        case 301: errorMessageText = "Moved Permanently"
        case 302: errorMessageText = "Found"
        case 303: errorMessageText = "See Other"
        case 304: errorMessageText = "Not Modified"
        case 305: errorMessageText = "Use Proxy"
        case 306: errorMessageText = "Switch Proxy"
        case 307: errorMessageText = "Temporary Redirect"
        case 308: errorMessageText = "Permanent Redirect"
        case 400: errorMessageText = "Bad Request"
        case 401: errorMessageText = "Unauthorized"
        case 402: errorMessageText = "Payment Required"
        case 403: errorMessageText = "Forbidden"
        case 404: errorMessageText = "Not Found"
        case 405: errorMessageText = "Method Not Allowed"
        case 406: errorMessageText = "Not Acceptable"
        case 407: errorMessageText = "Proxy Authentication Required"
        case 408: errorMessageText = "Request Timeout"
        case 409: errorMessageText = "Conflict"
        case 410: errorMessageText = "Gone"
        case 411: errorMessageText = "Length Required"
        case 412: errorMessageText = "Precondition Failed"
        case 413: errorMessageText = "Payload Too Large"
        case 414: errorMessageText = "URI Too Long"
        case 415: errorMessageText = "Unsupported Media Type"
        case 416: errorMessageText = "Range Not Satisfiable"
        case 417: errorMessageText = "Expectation Failed"
        case 418: errorMessageText = "I'm a teapot"
        case 421: errorMessageText = "Misdirected Request"
        case 422: errorMessageText = "Unprocessable Entity"
        case 423: errorMessageText = "Locked"
        case 424: errorMessageText = "Failed Dependency"
        case 425: errorMessageText = "Too Early"
        case 426: errorMessageText = "Upgrade Required"
        case 428: errorMessageText = "Precondition Required"
        case 429: errorMessageText = "Too Many Requests"
        case 431: errorMessageText = "Request Header Fields Too Large"
        case 451: errorMessageText = "Unavailable For Legal Reasons"
        case 500: errorMessageText = "Internal Server Error"
        case 501: errorMessageText = "Not Implemented"
        case 502: errorMessageText = "Bad Gateway"
        case 503: errorMessageText = "Service Unavailable"
        case 504: errorMessageText = "Gateway Timeout"
        case 505: errorMessageText = "HTTP Version Not Supported"
        case 506: errorMessageText = "Variant Also Negotiates"
        case 507: errorMessageText = "Insufficient Storage"
        case 508: errorMessageText = "Loop Detected"
        case 510: errorMessageText = "Not Extended"
        case 511: errorMessageText = "Network Authentication Required"

    return render_template('error_message.html', errorCode=error.code, errorMessage=errorMessageText, errorReason=error.reason), error.code

def main():
    serve(app, host="0.0.0.0", port=8080)

if __name__ == "__main__":
    os.environ.update({
        "FLASK_ENV": "development",
        "FLASK_DEBUG": "1"
    })
    app.run(debug=True, port=8080) #, use_reloader=False)
