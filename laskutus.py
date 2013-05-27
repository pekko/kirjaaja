#!/usr/bin/python
# *-* encoding: utf-8 *-*

import MySQLdb

import log
import settings

conn = MySQLdb.connect(host=settings.mysql.host, port=settings.mysql.port, user=settings.mysql.user, passwd=settings.mysql.passwd, db=settings.mysql.db, 
    use_unicode=True,
    )
cur = conn.cursor()

def get_payment_by_refnumber(refnumber):
    """
    Haetaan lasku viitenumeron perusteella
    """
    cur.execute("""
        SELECT id
        FROM laskutus_payments payments
        WHERE payments.refnumber = %s
        """,
        (refnumber,)
    )
    res = cur.fetchone()
    if not res:
        return 0

    return res[0]


def get_account(payment_id):
    """
    Haetaan laskun tili.
    """

    cur.execute("""
        SELECT projects.name, projects.tili, projects.year
        FROM laskutus_projects projects
        INNER JOIN laskutus_payments payments ON projects.id = payments.project_id
        WHERE payments.id = %s
        """,
        (payment_id,)
    )
    res = cur.fetchone()
    if not res:
        raise Exception("Tiliä ei löytynyt laskulle id %s" % (payment_id))
        return 0

    if res[2] < settings.year:
        return settings.accounts.siirtosaamiset
    return res[1]

def get_description(payment_id):
    """
    Haetaan laskun selite.
    """
    cur.execute("""
        SELECT projects.name, payments.name
        FROM laskutus_projects projects
        INNER JOIN laskutus_payments payments ON projects.id = payments.project_id
        WHERE payments.id = %s
        """,
        (payment_id,)
    )
    res = cur.fetchone()
    if not res:
        raise Exception("Selitettä ei löytynyt laskulle id %s" % payment_id)
        return ""

    return "%s, %s" % (res[0].encode('utf-8'), res[1].encode('utf-8'))

def get_amount(payment_id):
    """
    Haetaan laskun summa.
    """
    cur.execute("""
        SELECT payments.amount
        FROM laskutus_payments payments 
        WHERE payments.id = %s
        """,
        (payment_id,)
    )
    res = cur.fetchone()
    if not res:
        raise Exception("Summaa ei löytynyt laskulle id %s" % payment_id)
        return 0

    return res[0]


def mark_paid(payment_id, summa, paid_date):
    """
    Tarkistetaan, että manuaalisesti maksettu lasku on ok
    ja merkitään se maksetuksi.

    Palauttaa totuusarvon onnistumisesta.
    """

    if summa != get_amount(payment_id):
        # ISO PAHA VIRHE. KUOLE!
        log.msg("Maksun %d summa on virheellinen: %.2f eur, oikeasti %.2f eur" % (payment_id, summa, get_amount(payment_id)), "WARN")
        raise Exception("Maksun %d summa on virheellinen: %.2f eur, oikeasti %.2f eur" % (payment_id, summa, get_amount(payment_id)))
        return False

    # merkataan maksetuksi
    # TODO
    cur.execute("""
        SELECT status
        FROM laskutus_payments
        WHERE id = %s
        """, 
        (payment_id,)
    )
    status = cur.fetchone()[0]
    if status != 'manual_paid':
        log.msg("Marking payment_id %d as paid to laskutus" % (payment_id,))
        
        count = cur.execute("""
            UPDATE laskutus_payments
            SET status = 'manual_paid',
                paiddate = %s
            WHERE id = %s
            """,
            (paid_date, payment_id,)
        )
        if count == 1:
            cur.execute("""
                INSERT INTO laskutus_log_transaction
                    (payment_id, timestamp, message, ip)
                VALUES
                    (%s, NOW(), 'Kirjaaja merkitsee maksetuksi', '127.0.0.1'),
                    (%s, NOW(), 'Muutettu: status: """ + status +""" -> manual_paid', '127.0.0.1')
                """,
                (payment_id,
                payment_id)
            )
            conn.commit()   
        else:
            log.msg("FAILED Marking payment_id %d as paid to laskutus" % (payment_id,), "ERROR")

    return True

def main():
    print get_account(20004)
    print get_description(20004)

if __name__ == '__main__':
    main()
