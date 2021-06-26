import socket
import numpy as np
import json
import requests
import json
import base64
import io
import argparse

from PIL import Image, ImageOps
import numpy as np
import torch
from flask import Flask
app = Flask(__name__)

from model import ConvNet, MODEL, IM_SCALE

DEBUG_TARGET = False
TARGET_PORT = 8080

NET = ConvNet().float()#.half().cuda()
NET.load_state_dict(torch.load(MODEL))
NET.eval()

local_docker_network_ip = None
def get_target():
    global local_docker_network_ip
    if (not local_docker_network_ip):
        local_docker_network_ip = socket.gethostbyname(socket.gethostname())    
        subnet_mask = local_docker_network_ip[:-2]
    target = subnet_mask + ".0" + str(3)
    return target
def get_debug_target():
    return "0.0.0.0"

@app.route("/get")
def get():
    try:
        target = get_target() if not DEBUG_TARGET else get_debug_target()
        endpoint = f"http://{target}:{TARGET_PORT}/get"
        response = requests.get(endpoint)
        if response.status_code == 200:
            j = response.json()
            if "image" in j:
                im_64 = j["image"]
                im_raw = base64.b64decode(im_64)
                im = Image.open(io.BytesIO(im_raw))
                im = im.resize(IM_SCALE)
                im = ImageOps.grayscale(im)
                im = np.array(im) / 255.0
                im = torch.tensor(im, dtype=torch.float32).unsqueeze(0).unsqueeze(0)#.cuda().half()

                with torch.no_grad():
                    inf = NET(im).item()
                if inf == 0:
                    blink = False
                else:
                    blink = True
                
                data = j
                if "inference" not in data:
                    data["inference"] = []
                if blink:
                    data["inference"].append({"class": "blink"})

                return app.response_class(
                    response=json.dumps(data),
                    status=200,
                    mimetype='application/json')

    except Exception as e:
        print(e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-p', "--port", type=int, default=8080,help='the port its hosted on')
    parser.add_argument('-t', "--target-port", type=int, default=8080,help='the port to bang')
    parser.add_argument('-l', "--localhost-target", action='store_true', help='enable if not running in docker virtual network')
    args = parser.parse_args()
    
    DEBUG_TARGET = args.localhost_target
    TARGET_PORT = args.target_port

    app.run(debug=False, host='0.0.0.0', port=args.port)
