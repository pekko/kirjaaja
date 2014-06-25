#!/usr/bin/python

import psycopg2
import simplejson
import sys

import log
import payment
import settings
import verkkomaksut

def html(data):
	print_counteraccounts = True

	for payment in data:
		print "<tr class='spacer'><td colspan='3'></td></tr>"
		for row in payment['payments']:
			if print_counteraccounts or row['account'] != settings.accounts.pankkitili:
				print "<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (row['account'], row['amount'], row['description'])

def json(data):
	print simplejson.dumps(data)

def tilitin(data):
	conn = None
	insert_payment = """
		INSERT INTO document 
			(id, number, period_id, date) 
		VALUES 
			(nextval('document_id_seq'), %s, %s, %s)
		RETURNING id
		""" 

	insert_row = """
		INSERT INTO entry 
			(id, document_id, account_id, debit, amount, description, row_number, flags) 
		VALUES 
			(nextval('entry_id_seq'), %s, (SELECT id FROM account WHERE number = %s), %s, %s, %s, %s, %s)
		"""

	try:
		conn = psycopg2.connect(host=settings.psql.host, user=settings.psql.user, password=settings.psql.passwd, database=settings.psql.db)
		conn.set_client_encoding('UTF8')
		cur = conn.cursor()

		cur.execute("SELECT MAX(number) FROM document WHERE period_id = %s" % (settings.period_id,) )
		document_number = cur.fetchone()
		if document_number[0] is None:
			document_number = 1
		else:
			document_number = document_number[0] + 1

		log.msg("Starting with document_number %d" % (document_number,))

		for p in data:
			cur.execute(insert_payment, (document_number, settings.period_id, p['meta']['date']))
			document_id = cur.fetchone()[0]

			log.msg("Inserted payment with document_id %d" % (document_id,))

			row_number = 1
			for row in p['payments']:
				if not row['account']:
					row['account'] = settings.accounts.muut_kulut
				cur.execute(insert_row, (document_id, str(row['account']), row['debit'], row['amount'], row['description'][:100], row_number, 0))
				row_number += 1

			log.msg("Inserted %d rows" % (row_number-1))

			if p['meta']['type'] == 'verkkomaksut':
				verkkomaksut.generate_batch_report(p, document_number)

			document_number += 1

	except psycopg2.DatabaseError, e:
		if conn:
		    conn.rollback()

		print 'Error %s' % e
		sys.exit(1)

	finally:
		if conn:    
			conn.commit()
