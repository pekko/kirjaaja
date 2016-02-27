#!/usr/bin/python
# *-* encoding: latin-1 *-*

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

	print "Content-type: text/plain\n\n"
	kirjaaja(tiliote_fn, tilitysraportti_fn)
	logfile = settings.dir + "log/%s.log" % (datetime.date.today())
	print """
Kirjaaja-ajo OK
===============

Ajo on onnistunut.

Alla on logitiedosto t�lt� p�iv�lt�. Varmista, ett� merkinn�t ovat oikein.
Korjaa tarvittaessa k�sin Kirjaaja-ohjelmaan.

------------------------------------------------------------------------------

"""

	print open(logfile).read()
	sys.exit(0)

def main():
	form = cgi.FieldStorage()

	run_kirjaaja_instructions = """
		<input type="button" value="Aja" disabled> Siirr� tiedostot ensin...
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
		<style type="text/css">
		date {
			font-weight: bold;
		}
		</style>
	</head>

	<body>
		<form enctype="multipart/form-data" action="" method="post">
		<h1>Kirjaaja: Er�ajo</h1>
		<p>
			T�n��n on <date>%(today)s</date>, eli voidaan hakea tapahtumat <date>%(stop_date)s</date> asti.<br>
			Kirjanpidon viimeisin merkint� on <date>%(previous_run)s</date>.<br>
			K�yt�ss� <b>%(environment)symp�rist�</b>.
		</p>
		
		<h2>Toimintaohjeet</h2>

		<h3>1. Hae tiliotetiedosto</h3>
		<ol>
			<li>Kirjaudu Nordean verkkopankkiin henkil�kohtaisilla tunnuksillasi.</li>
			<li>Valitse Speksin k�ytt�tili (FI47 1112 3000 3582 80) -> Tapahtumaluettelo</li>
			<li>Varmista, ett� Tili-valikossa todella on valittu oikea tili</li>
			<li>Hae tulosteet ajalta <date>%(start_date)s</date> - <date>%(stop_date)s</date></li>
			<li>Valitse t�st� �sken hakemasi tiedosto:
				<input type="file" name="tiliote">
			</li>
		</ol>

		<h3>2. Hae tilitysraportti</h3>
		<ol>
			<li>Kirjaudu <a href="https://ssl.verkkomaksut.fi/kauppiaspaneeli/" target="_blank">Verkkomaksujen kauppiaspaneeliin</a> (tunnukset jostain)</li>
			<li>Valitse Tilitykset -> Kirjanpitoraportti (<a href="https://ssl.verkkomaksut.fi/kauppiaspaneeli/batch/accounting" target="_blank">pikalinkki</a>)</li>
			<li>Sy�t� aikav�liksi <date>%(start_date)s</date> - <date>%(stop_date)s</date> ja valitse "Hae"</li>
			<li>Valitse "Lataa kirjanpitoraportti CSV-tiedostona" ja tallenna kyseinen tiedosto</li>
			<li>Vaitse t�st� �sken hakemasi tiedosto:
				<input type="file" name="tilitysraportti">
			</li>
		</ol>

		<h3>3. Siirr� tiedostot palvelimelle</h3>
		<ol>
			<li>Klikkaa t�st�: <input type="submit" value="Upload"></li>
		</ol>
		</form>

		<form method="post" action="">
		<h3>4. Aja Kirjaaja</h3>
		<ol>
			<li>%(run_kirjaaja)s</li>
			<li>Jos ok, tarkista viel� k�sin.</li>
			<li>Jos ei onnistu, selvit� virheiden syy ja palauta tarvittaessa backup (t�h�n tarvitset apua).</li>
		</ol>
		</form>

		<h2>Ongelmatilanteissa</h2>
		<ul>
			<li>Koodi: <pre>nodeta:~/var/script/kirjaaja/</pre></li>
			<li>Tallennettu svn:��n, k�yt� sit� oikein!</li>
			<li>Saa h�irit�: Pekko Lipsanen / pekko.lipsanen a iki.fi / 040 861 0631</li>
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
