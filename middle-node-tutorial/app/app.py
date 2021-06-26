import json
import socket
import requests

from flask import Flask, render_template
app = Flask(__name__)

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

            #   augment existing data in the pipeline
            if "message" in j:
                s = j["message"]
                s = (s.replace("Hello", "Transform the") 
                      .replace("from", "with")    
                      .replace("Cratus", "Asset-Rx Edge"))
                j["message"] = s
            
            #   add new data to the pipeline
            j["another_message"] = "What you're referring to as Linux, is in fact, GNU/Linux, or as I've recently taken to calling it, GNU plus Linux. Linux is not an operating system unto itself, but rather another free component of a fully functioning GNU system made useful by the GNU corelibs, shell utilities and vital system components comprising a full OS as defined by POSIX."

            return app.response_class(
                response=json.dumps(j),
                status=200,
                mimetype='application/json')

    except Exception as e:
        print(e)

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=8080)
