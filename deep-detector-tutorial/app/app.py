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

@app.route("/get")
def get():
	try:
		upstream_container = f"http://{get_target()}:8080/get"
		response = requests.get(upstream_container)
		if response.status_code == 200:
			j = response.json()
			try:
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
					if "inference" not in j:
						j["inference"] = []
					print(inf)
					cls = "class_1" if inf <= 0 else "class_2"
					j["inference"].append({"class": cls})
			except Exception as e:
				print(e)
			finally:
				return app.response_class(
					response=json.dumps(j),
					status=200,
					mimetype='application/json')

	except Exception as e:
		print(e)

if __name__ == "__main__":
	app.run(debug=False, host='0.0.0.0', port=8080)
