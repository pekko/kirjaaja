#!/usr/bin/python
# *-* encoding: utf-8 *-*

MODE = "prod" # test tai prod

class mysql:
	if MODE == "prod":
		host = "db.nodeta.fi"
		user = "speksi"
		passwd = ""
		db = "speksi"
		port = 3306
	else:
		# CREATE SSH TUNNEL
		# ssh -L localport:remotehost:remoteport ...
		# ssh -L 13306:db1.kapsi.fi:3306 pwc@kapsi.fi
		host = "127.0.0.1" # db1.kapsi.fi
		user = "pwc"
		passwd = "" # insert pw here
		db = "pwc"
		port = 13306

class psql:
	host = "pecko.dy.fi"
	user = "speksi-rahis"
	passwd = "kassa!masiina"

	if MODE == "prod":
		db = "speksi-rahis"
	else:
		db = "speksi-rahis-test"

# TODO tämä paremmin
# * yleisemmin: accounts.get('Muut tuotot') 
# * tai sit haetaan kannasta kaikki tähän luokkaan initissä
class accounts:
	muut_tuotot = 3900
	muut_kulut = 7500

	pankkitili = 1520
	siirtosaamiset = 1900
	lipunmyynti = 3000
	kiertuetuotot = 3050
	naaspeksi = 3400

	pankkikulut = 7250

dir="/rdata/www/speksi/var/script/kirjaaja/"
period_id = 1
year = 2013
