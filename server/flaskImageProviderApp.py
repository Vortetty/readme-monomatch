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
    exit(1)

try:
    import magic
except:
    print("This program requires libmagic to be installed")

from io import BytesIO
import json
from flask import Flask, redirect, Response, request
from flask_compress import Compress
from waitress import serve
import os
from werkzeug.exceptions import HTTPException
from jinja2 import Environment, PackageLoader, select_autoescape
import numpy as np
import colorsys

# Cd to this dir for safety, ensure smooth running
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
fname = os.path.basename(__file__)
# os.chdir(dname)

app = Flask(__name__)
app.config.update(
    {
        "COMPRESS_MIMETYPES": [
            "text/html",
            "image/png",
            "image/svg+xml",
            "application/json",
            "image/x-icon"
        ],
        "COMPRESS_LEVEL": 9,
        "COMPRESS_BR_LEVEL": 11,
        "COMPRESS_BR_WINDOW": 24,
        "COMPRESS_BR_BLOCK": 24,
        "COMPRESS_DEFLATE_LEVEL": 9,
        "COMPRESS_MIN_SIZE": 50
    }
)
compress = Compress(app)
mimeFind = magic.Magic(mime=True)
jinjaEnv = Environment(
    loader=PackageLoader(fname.replace(".py", ""), "templates"),
    autoescape=select_autoescape()
)
ICON_COLORS = [
    tuple(int(i) for i in colorsys.hsv_to_rgb(i/512*360, .5, 1)*np.array([255, 255, 255])) for i in range(512)
]

def send_file(file_path: str) -> Response:
    return Response(
        open(file_path, "rb").read() if os.path.isfile(file_path) else "",
        mimetype=mimeFind.from_file(file_path)
    )

def render_template(template_path: str, **kwargs):
    template = jinjaEnv.get_template(template_path)
    rendered = template.render(**kwargs)
    return compress.after_request(Response(
        rendered.encode("utf-8"),
        mimetype="text/html"
    ))

class abortReason (HTTPException):
    def __init__(self, code: int, reason: str="", overrideErrorMessageText: str=None):
        self.code = code
        self.reason = reason
        self.overrideErrorMessageText = overrideErrorMessageText

@app.route("/")
def index():
    return redirect("https://github.com/Vortetty/readme-monomatch", code=308)

@app.route("/monomatch/card/<filetype>/<card_id>")
def card(filetype: str, card_id: str|None=None):
    ext = ""
    if filetype.lower() == "png":
        ext = "png"
    elif filetype.lower() == "webp":
        ext = "webp"
    else:
        raise abortReason(404, reason="Filetype not supported, please use png or webp")

    if int(card_id) == 0:
        try:
            return send_file(os.path.join(dname, f"cards/0.{ext}"))
        except FileNotFoundError:
            return send_file(os.path.join(dname, "404.png"))
    elif int(card_id) == 1:
        try:
            return send_file(os.path.join(dname, f"cards/1.{ext}"))
        except FileNotFoundError:
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
            return send_file(os.path.join(dname, f"generator/symbols/png/{int(icon_id)}.png"))
        elif filetype.lower() == "webp":
            return send_file(os.path.join(dname, f"generator/symbols/webp/{int(icon_id)}.webp"))
        elif filetype.lower() == "svg":
            return send_file(os.path.join(dname, f"generator/symbols/{int(icon_id)}.svg"))
        else:
            raise abortReason(404, reason="Filetype not supported, please use png, webp, or svg")
    except FileNotFoundError:
        raise abortReason(404, reason=f"Invalid image ID, valid range is 0-{len(os.listdir(os.path.join(dname, 'generator/symbols/png')))-1}")
    except Exception:
        raise abortReason(500)

@app.errorhandler(abortReason)
def page_not_found(error: abortReason):
    errorMessageText = error.overrideErrorMessageText
    if errorMessageText == None:
        match error.code: # Match every standard error code defined by mozilla (https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
                          # 100, 101, 102, 103
                          # 200, 201, 202, 203, 204, 205, 206, 207, 208, 226
                          # 300, 301, 302, 303, 304, 305, 306, 307, 308
                          # 400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 421, 422, 423, 424, 425, 426, 428, 429, 431, 451
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
            case 306: errorMessageText = "Unused"
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
            case _:   errorMessageText = "Unknown Error"

    return render_template('error_message.html', errorCode=error.code, errorMessage=errorMessageText, errorReason=error.reason), error.code

@app.route('/favicon.ico')
def favicon():
    return Response(
        open(os.path.join(dname, 'favicon.ico'), "rb").read().replace(b"\xFF\xFF\xFF", bytes(reversed(ICON_COLORS[np.random.randint(0, 2**31-1, 3)[0]%len(ICON_COLORS)]))),
        mimetype="image/x-icon"
    ) # 70b icon https://github.com/mathiasbynens/small/blob/master/ico.ico

def main():
    serve(app, host="0.0.0.0", port=8080)

if __name__ == "__main__":
    os.environ.update({
        "FLASK_ENV": "development",
        "FLASK_DEBUG": "1"
    })
    app.run(debug=True, port=8080) #, use_reloader=False)
