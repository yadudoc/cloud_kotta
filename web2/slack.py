#!/usr/bin/env python
import requests
import logging

def post_message(app, payload):
    
    try:
        webhook_url = open(app.config["slack.webhook"], 'r').read()        
        print webhook_url
        r = requests.post(webhook_url, data=payload)
        print r.text
        return True

    except FileNotFoundError:
        print "Cound not find the slack.webhook file"
        return False

    except Exception, e:
        print "Sending message failed, error : ",e
        return False


if __name__ == "__main__":
    import config_manager as cm

    payload={"channel": "#cloudkotta", 
             "username": "webhookbot", 
             "text": "This is posted to #cloudkotta and comes from a bot named webhookbot.", 
             "icon_emoji": ":ghost:"}
    app = cm.load_configs("production.conf")
    post_message(app, payload)
