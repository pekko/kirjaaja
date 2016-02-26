#!/usr/bin/python
# *-* encoding: utf-8 *-*

import settings
import requests

order_ids = None

def get_ids():
    global order_ids
    if order_ids is None:
        response = requests.get(settings.lippukauppa.url, auth=settings.lippukauppa.auth)
        if response.status_code != 200:
            raise Exception("Ongelma Lippukauppa-API:n kanssa, ei skulaa")
        if hasattr(response.json, '__call__'):
            order_ids = response.json() # a function on my python..
        else:
            order_ids = response.json # is a key on your (kapsi's) python

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
    if is_naaspeksi(order_id):
        return settings.accounts.naaspeksi
    elif is_kiertue(order_id):
        return settings.accounts.kiertuetuotot

    return settings.accounts.lipunmyynti

def description(order_id):
    if is_naaspeksi(order_id):
        return "Lipunmyyntitulo, NääsPeksi"
    elif is_kiertue(order_id):
        return "Lipunmyyntitulo, kiertue, " + order_ids[order_id]["city"]

    return "Lipunmyyntitulo"
