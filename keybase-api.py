'''
This script allows you to send messages to KeyBase chat channels (including teams). It works by exposing a
webhook to Tautulli that is triggered when certain Plex events occur.

This script expects a file called 'config.ini' in the same directory with the following layout:
    [DEFAULT]
    plex_libraries =
      the_list_of_libraries_you_care_about
    channel_name = keybase_team_name
    channel_topic_name = keybase_team_channel

Tautulli should be configured with a web hook that sends the following JSON data:
    {
    "action": "{action}",
    "media_type" : "{media_type}",
    "title": "{title}",
    "library_name": "{library_name}",
    "show_name": "{show_name}",
    "episode_name": "{episode_name}",
    "artist_name": "{artist_name}",
    "album_name": "{album_name}",
    "track_name": "{track_name}",
    "track_artist": "{track_artist}",
    "year": "{year}"
    }

KeyBase: https://keybase.io/
Tautulli: https://tautulli.com/

'''

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

def send_to_keybase(message):
    params = {
        "options": {
            "channel": channel,
            "message": message
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


@app.route('/', methods=['POST'])
def tautulli_webhook():
    kbmsg = dict()
    print(request.json)
    sys.stdout.flush()
    plexdata = json.loads(json.dumps(request.json))
    if plexdata['action'] == 'play':
        if plexdata['library_name'] and plexdata['library_name'] in config['DEFAULT']['plex_libraries']:
            kbmsg['body'] = "[Plex] Playing: {} ({})".format(plexdata['title'],plexdata['year'])
            send_to_keybase(kbmsg)
    elif plexdata['action'] == 'created':
        if plexdata['library_name'] and plexdata['library_name'] in config['DEFAULT']['plex_libraries']:
            if plexdata['media_type'] == 'movie':
                kbmsg['body'] = "*[Plex] New movie added: {} ({})*".format(plexdata['title'],plexdata['year'])
                send_to_keybase(kbmsg)
            if plexdata['media_type'] == 'episode':
                kbmsg['body'] = "[Plex] New episode added: {}".format(plexdata['title'])
                send_to_keybase(kbmsg)
    else:
        print("No action matched.")

    return '', 200

@app.route('/alert', methods=['POST'])
def alertManagerWebhook():
    kbmsg = dict()
    print(request.json)
    sys.stdout.flush()
    amdata = json.loads(json.dumps(request.json))
    if amdata['commonLabels']['alertname'] == 'HighCPU':
        if amdata['status'] == "firing":
            kbmsg['body'] = "_[Plex] WARNING: CPU usage at {}%_".format(amdata['commonAnnotations']['cpupct'])
            send_to_keybase(kbmsg)
        else:
            kbmsg['body'] = "_[Plex] RESOLVED: CPU back to normal_"
            send_to_keybase(kbmsg)

    return '', 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(config['DEFAULT']['flask_port']))
