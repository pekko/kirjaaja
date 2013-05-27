import psycopg2
import sys

import settings
import laskutus

def main():
	for i in xrange(20200, 20250):
		#print unicode(laskutus.get_description(i), 'iso-8859-1').encode('utf8')
		print laskutus.get_description(i)
	print "DO NOT USE ANYMORE. Exiting."
	sys.exit(1)
	
	conn = psycopg2.connect(host=settings.psql.host, user=settings.psql.user, password=settings.psql.passwd, database=settings.psql.db)
	conn.set_client_encoding('UTF8')
	cur = conn.cursor()

	try:
		cur.execute("SELECT id,description FROM entry")
		res = cur.fetchall()
		for r in res:
			(id,desc) = r
			desc = desc.decode('utf-8')
			print desc
			cur.execute("UPDATE entry SET description = %s WHERE id = %s", (desc, id))

	except psycopg2.DatabaseError, e:
		if conn:
		    conn.rollback()

		print 'Error %s' % e
		sys.exit(1)

	finally:
		if conn:    
			conn.commit()
			print "Commit!"

if __name__ == '__main__':
	main()