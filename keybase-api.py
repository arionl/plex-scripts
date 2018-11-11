import sys
from flask import Flask, request
import json
from subprocess import Popen, PIPE
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

channel = { "name": config['DEFAULT']['channel_name'],
            "members_type": "team",
            "topic_name": config['DEFAULT']['channel_topic_name'] }

app = Flask(__name__)

@app.route('/', methods=['POST'])

def webhook():
    kbmsg = dict()
    print(request.json)
    sys.stdout.flush()
    plexdata = json.loads(json.dumps(request.json))
    if plexdata['action'] == 'play':
        kbmsg['body'] = "[plex-scripts] Playing: {}".format(plexdata['title'])
    else:
        if plexdata['library_name'] and plexdata['library_name'] in config['DEFAULT']['notify_libraries']:
            if(plexdata['media_type'] == 'movie'):
                kbmsg['body'] = "[plex-scripts] New movie added: {}".format(plexdata['title'])
            if(plexdata['media_type'] == 'episode'):
                kbmsg['body'] = "[plex-scripts] New episode added: {}".format(plexdata['title'])

    params = {
        "options": {
            "channel": channel,
            "message": kbmsg
        }
    }

    jsondata = {
        "method": "send",
        "params": params
    }

    p = Popen(['/usr/bin/keybase', 'chat', 'api'], stdin=PIPE)

    p.communicate(json.dumps(jsondata).encode())

    p.stdin.close()
    p.wait()

    return '', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
