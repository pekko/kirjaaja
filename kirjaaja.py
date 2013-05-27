#!/usr/bin/python
# *-* encoding: utf-8 *-*

from datetime import date
import sys

import export
import log
import payment
import settings
import tiliote

def kirjaaja(tiliote_filename, verkkomaksut_filename):
    log.msg("Starting Kirjaaja with tiliote %s and verkkomaksut %s" % (tiliote_filename, verkkomaksut_filename))
    payment.init_verkkomaksut(verkkomaksut_filename)

    # paper = tiliote.Konek(tiliote_filename)
    paper = tiliote.TabSeperated(tiliote_filename)
    data = paper.parse()

    payments = []
    for p in data:
        payments.append(p.accounting())

    export.tilitin(payments)
    update_last_updated()

    totals = {}
    # for d in data: 
    #     vp = d.vastapuoli.rstrip().lower()
    #     if vp not in totals:
    #         totals[vp] = 0
    #     totals[vp] += d.summa
    # for (k,v) in totals.iteritems():
    #     print "%10.2f %s" % (v,k)

def update_last_updated():
    filename = settings.dir + 'public_html/last_updated.txt'
    f = open(filename, 'w')
    f.write(str(date.today()))
    f.close()

def main():
    if len(sys.argv) < 3:
        log.msg("Args not valid, only %d args." % (len(sys.argv),), "ERROR")
        print
        print "Usage: %s tiliote_file verkkomaksut_file" % sys.argv[0]
        print
        sys.exit()

    tiliote_filename = sys.argv[1]
    verkkomaksut_filename = sys.argv[2]
    
    kirjaaja(tiliote_filename, verkkomaksut_filename)

if __name__ == '__main__':
    main()
