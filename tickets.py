#!/usr/bin/python
# *-* encoding: utf-8 *-*

import settings
import urllib2

kiertue_ids = None

def is_ticket(order_id):
    return int(order_id) < 20000

def is_naaspeksi(order_id):
    return int(order_id) < 2000

def is_kiertue(order_id):
    global kiertue_ids
    if kiertue_ids is None:
        socket = urllib2.urlopen("http://teekkarispeksi.nappikauppa.net/admin/orders_kiertue.php")
        kiertue_ids = socket.read().split(";")

    return order_id in kiertue_ids

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
        return "Lipunmyyntitulo, kiertue"
        
    return "Lipunmyyntitulo"
