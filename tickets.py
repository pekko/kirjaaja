#!/usr/bin/python
# *-* encoding: utf-8 *-*

import settings
import log
import urllib2, json, base64

order_ids = None

def get_ids():
    global order_ids
    if order_ids is None:
        request = urllib2.Request(settings.lippukauppa.url)
        b64 = base64.encodestring('%s:%s' % settings.lippukauppa.auth).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % b64)
        response = urllib2.urlopen(request)
        order_ids = json.load(response)

def is_ticket(order_id):
    # first is a special case for fall 2015 NääsPeksi...
    return (order_id.isdigit() and int(order_id) < 250) or order_id.startswith("LIPPUKAUPPA")

def is_naaspeksi(order_id):
    get_ids()
    # first is a special case for fall 2015 NääsPeksi...
    return (order_id.isdigit() and int(order_id) < 250) or order_ids[order_id]["performer"] == u"NääsPeksi"

def is_kiertue(order_id):
    get_ids()
    return (order_ids[order_id]["city"] != "Helsinki" and order_ids[order_id]["city"] != "Espoo")

def account(order_id):
    try:
        if is_naaspeksi(order_id):
            return settings.accounts.naaspeksi
        elif is_kiertue(order_id):
            return settings.accounts.kiertuetuotot
    except KeyError:
        log.msg("Tilausta %s ei löytynyt tietokannasta, oletetaan tiliksi %s" % settings.accounts.lipunmyynti)
    return settings.accounts.lipunmyynti

def description(order_id):
    try:
        if is_naaspeksi(order_id):
            return "Lipunmyyntitulo, NääsPeksi"
        elif is_kiertue(order_id):
            return "Lipunmyyntitulo, kiertue, " + order_ids[order_id]["city"]
    except KeyError:
        log.msg("Tilausta %s ei löytynyt tietokannasta, oletetaan kuvaus Lipunmyyntituloksi" % order_id)
    return "Lipunmyyntitulo"
