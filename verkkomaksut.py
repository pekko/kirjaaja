#!/usr/bin/python
# *-* encoding: utf-8 *-*

from datetime import date
import MySQLdb

import laskutus
import log
import settings
import tickets

conn = MySQLdb.connect(host=settings.mysql.host, port=settings.mysql.port, user=settings.mysql.user, passwd=settings.mysql.passwd, db=settings.mysql.db)
cur = conn.cursor()

BATCH_REPORT_DIR = settings.dir + "public_html/batch_reports"

def get_payments(filename):
    """
    Parsitaan verkkomaksujen kirjanpitoraportista maksut oikeesti
    """
    batches = []
    f = open(filename)

    skipping = True
    for r in f:
        # hypätään header-rivin yli
        if skipping:
            skipping = False
            continue

        try:
            (rowtype, 
            date, 
            reference, 
            order_id, 
            name, 
            batch_amount, 
            batch_amount_ex_vat, 
            vat, 
            amount, 
            provision, 
            transaction,
            payment_amount, _) = r.replace('"', '').replace('=', '').split(";")

        except ValueError:
            (rowtype, 
            date, 
            reference, 
            order_id, 
            name, 
            batch_amount, 
            batch_amount_ex_vat) = r.rstrip().replace('"', '').replace('=', '').split(";")

        if rowtype == "TILITYS":
            (d, m, y) = date.split(".")
            batch_date = "%d-%02d-%02d" % (int(y),int(m),int(d))

            batches.append({
                'reference' : reference,
                'date' : batch_date,
                'batch' : []
            })
        
        elif rowtype == "MAKSU":
            if tickets.is_ticket(order_id):
                account = tickets.account(order_id)
                description = tickets.description(order_id)
                # print "%d" % (int(amount[:-3]))

            else:
                account = laskutus.get_account(order_id)
                if not account:
                    raise Exception("Could not get account for payment %s" % (order_id))
                    continue

                description = laskutus.get_description(order_id)

            batches[-1]['batch'].append({
                'account' : account,
                'amount' : float(payment_amount.replace(",",".")),
                'description' : description
            })
        else:
            raise Exception("ei osunut")
            continue

    # for b in batches:
    #     generate_batch_report(b)

    return batches

def generate_batch_report(batch, document_number):
#    f = open('public_html/batch_reports/'+str(document_number)+'.htm', 'w')
    f = open("%s/%s.htm" % (BATCH_REPORT_DIR,date.today()), 'a')    
    # TODO mikä tämä oli? konek? pvm_str = "%s.%s.20%s" % (batch['meta']['date'][4:6], batch['meta']['date'][2:4], batch['meta']['date'][:2])
    pvm_str = batch['meta']['date']

    f.write("""
<div class="tositenro">%(document_number)d</div>
<h1>Tilitysraportti</h1>

<table class="meta">
    <tr>
        <td>Viitenumero</td>
        <td>%(reference)d</td>
    </tr>
    <tr>
        <td>Maksupaiva</td>
        <td>%(date)s</td>
    </tr>
</table>

<table class="maksut">
    <tbody>
""" % {'document_number' : document_number, 'reference' : batch['meta']['reference'], 'date' : pvm_str})

    total = 0
    for p in batch['payments']:
        if p['debit']:
            continue
        total += p['amount']

        if p['account'] == settings.accounts.siirtosaamiset:
            siirtosaaminen = "SIIRTOSAAMINEN"
        else:
            siirtosaaminen = ""

        f.write("<tr><td>%s %s</td><td>%.2f eur</td></tr>\n" % (siirtosaaminen, p['description'], p['amount']))

    f.write("</tbody><tfoot><tr><td>YHTEENSA</td><td>%.2f eur</td></tr></tfoot></table>\n" % (total))

    f.close()
    
def main():
    get_payments('data/accounting-2012k.csv')

if __name__ == '__main__':
    main()
