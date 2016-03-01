#!/usr/bin/python
# *-* encoding: utf-8 *-*

import cgi
import cgitb
import datetime
import os
import psycopg2
import sys

sys.path.append('/home/users/speksi/scripts/kirjaaja/')

from kirjaaja import settings

cgitb.enable()
if settings.MODE == 'prod':
	UPLOAD_PATH = settings.dir + 'upload'
else:
	UPLOAD_PATH = '/rdata/www/speksi/var/script/kirjaaja/upload/test'

def upload(f):
	"""
	Parametrit:
		f 	file-instanssi formilta

	Palauttaa:
		uploadatun tiedoston polun
	"""
	if not f.filename:
		raise Exception("No filename")

	fn = os.path.basename(f.filename)
	open(UPLOAD_PATH+'/'+fn, 'w').write(f.file.read())

	return UPLOAD_PATH+'/'+fn	

def last_run():
	#return datetime.datetime.now()
	conn = psycopg2.connect(host=settings.psql.host, user=settings.psql.user, password=settings.psql.passwd, database=settings.psql.db)
	conn.set_client_encoding('UTF8')
	cur = conn.cursor()

	cur.execute("SELECT MAX(date) FROM document WHERE number < 1000") # TODO perkele. vituiksi meni. yli tonnin kirjaukset (toinen tili) tehdaan manuaalisesti.
	last_run = cur.fetchone()[0]
	return last_run

def run_kirjaaja(tiliote_fn, tilitysraportti_fn):
	from kirjaaja import kirjaaja

	kirjaaja(tiliote_fn, tilitysraportti_fn)
	logfile = settings.dir + "log/%s.log" % (datetime.date.today())

	print """Content-type: text/html

<!doctype html>
<html>
<head>
	<meta charset="utf-8">
        <title>Kirjaaja - Loki</title>
        <style type="text/css">
        	date {
                        font-weight: bold;
                }
        </style>
</head>

<body>
<pre>
Kirjaaja-ajo OK
===============

Ajo on onnistunut.

Alla on logitiedosto tältä päivältä. Varmista, että merkinnät ovat oikein.
Korjaa tarvittaessa käsin Kirjaaja-ohjelmaan.

------------------------------------------------------------------------------

"""

	print open(logfile).read()
	print """
</pre>
</body>
</html>
"""
	sys.exit(0)

def main():
	form = cgi.FieldStorage()

	run_kirjaaja_instructions = """
		<input type="button" value="Aja" disabled> Siirrä tiedostot ensin...
	"""

	if 'tiliote' in form and 'tilitysraportti' in form:
		tiliote_fn = upload(form['tiliote'])
		tilitysraportti_fn = upload(form['tilitysraportti'])

		run_kirjaaja_instructions = """
			<input type="hidden" name="tiliote_fn" value="%(tiliote_fn)s">
			<input type="hidden" name="tilitysraportti_fn" value="%(tilitysraportti_fn)s">
			<input type="submit" value="Aja">
		""" % {
			'tiliote_fn' : tiliote_fn,
			'tilitysraportti_fn' : tilitysraportti_fn,
		}

	elif 'tiliote_fn' in form and 'tilitysraportti_fn' in form:
		run_kirjaaja(form['tiliote_fn'].value, form['tilitysraportti_fn'].value)

	today = datetime.date.today()
	previous_run = last_run()
	start_date = previous_run + datetime.timedelta(days=1)
	stop_date = today - datetime.timedelta(days=5)

	print """Content-type: text/html

	<!doctype html>
	<html>
	<head>
		<meta charset="utf-8">
		<title>Kirjaaja</title>
		<style type="text/css">
		date {
			font-weight: bold;
		}
		</style>
	</head>

	<body>
		<form enctype="multipart/form-data" action="" method="post">
		<h1>Kirjaaja: Eräajo</h1>
		<p>
			Tänään on <date>%(today)s</date>, eli voidaan hakea tapahtumat <date>%(stop_date)s</date> asti.<br>
			Kirjanpidon viimeisin merkintä on <date>%(previous_run)s</date>.<br>
			Käytössä <b>%(environment)sympäristö</b>.
		</p>
		
		<h2>Toimintaohjeet</h2>

		<h3>1. Hae tiliotetiedosto</h3>
		<ol>
			<li>Kirjaudu Nordean verkkopankkiin henkilökohtaisilla tunnuksillasi.</li>
			<li>Valitse Speksin käyttötili (FI47 1112 3000 3582 80) -> Tapahtumaluettelo</li>
			<li>Varmista, että Tili-valikossa todella on valittu oikea tili</li>
			<li>Hae tulosteet ajalta <date>%(start_date)s</date> - <date>%(stop_date)s</date></li>
			<li>Valitse tästä äsken hakemasi tiedosto:
				<input type="file" name="tiliote">
			</li>
		</ol>

		<h3>2. Hae tilitysraportti</h3>
		<ol>
			<li>Kirjaudu <a href="https://ssl.verkkomaksut.fi/kauppiaspaneeli/" target="_blank">Verkkomaksujen kauppiaspaneeliin</a> (tunnukset jostain)</li>
			<li>Valitse Tilitykset -> Kirjanpitoraportti (<a href="https://ssl.verkkomaksut.fi/kauppiaspaneeli/batch/accounting" target="_blank">pikalinkki</a>)</li>
			<li>Syötä aikaväliksi <date>%(start_date)s</date> - <date>%(stop_date)s</date> ja valitse "Hae"</li>
			<li>Valitse "Lataa kirjanpitoraportti CSV-tiedostona" ja tallenna kyseinen tiedosto</li>
			<li>Vaitse tästä äsken hakemasi tiedosto:
				<input type="file" name="tilitysraportti">
			</li>
		</ol>

		<h3>3. Siirrä tiedostot palvelimelle</h3>
		<ol>
			<li>Klikkaa tästä: <input type="submit" value="Upload"></li>
		</ol>
		</form>

		<form method="post" action="">
		<h3>4. Aja Kirjaaja</h3>
		<ol>
			<li>%(run_kirjaaja)s</li>
			<li>Jos ok, tarkista vielä käsin.</li>
			<li>Jos ei onnistu, selvitä virheiden syy ja palauta tarvittaessa backup (tähän tarvitset apua).</li>
		</ol>
		</form>

		<h2>Ongelmatilanteissa</h2>
		<ul>
			<li>Koodi: <pre>nodeta:~/var/script/kirjaaja/</pre></li>
			<li>Tallennettu svn:ään, käytä sitä oikein!</li>
			<li>Saa häiritä: Pekko Lipsanen / pekko.lipsanen a iki.fi / 040 861 0631</li>
		</ul>
	</body>
	</html>

	""" % {
		'environment' : ["testi", "tuotanto"][settings.MODE == 'prod'],
		'previous_run' : previous_run.strftime('%d.%m.%Y'),
		'run_kirjaaja' : run_kirjaaja_instructions,
		'start_date' : start_date.strftime('%d.%m.%Y'),
		'stop_date' : stop_date.strftime('%d.%m.%Y'),
		'today' : today.strftime('%d.%m.%Y'),
	}

if __name__ == '__main__':
	main()
