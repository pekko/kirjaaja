#!/usr/bin/python
# *-* encoding: utf-8 *-*

from datetime import date

import payment

class Tiliote(object):
    def __init__(self, filename):
        self.f = open(filename)
    def parse(self):
        pass

class Konek(Tiliote):
    def __init__(self, filename):
        super(Konek, self).__init__(filename)

    def _read_raha(self, input, size=18):
        """ TODO: pitäisikö palauttaa str vai float? """

        etumerkki = 1
        if input.read(1) == '-':
            etumerkki = -1

        summa = int(input.read(size))
        return etumerkki * (summa/100.0)

    def parse(self):
        """ Parsitaan konekielinen tiliote. """
        data = []
        f = self.f # lyhyempi

        while True:
            aineistotunnus = f.read(1)
            if aineistotunnus == '':
                break
            if aineistotunnus != 'T':
                print 'aineistotunnus: -' + aineistotunnus + '-'
                print f.read(32)
                raise ValueError('Aineistotunnus on virheellinen!')
            tietuetunnus = f.read(2)

            #print 'Tietuetunnus %s' % tietuetunnus
            size = int(f.read(3)) - (1+2+3)

            if tietuetunnus == '00':
                """
                4.4 Tiliotteen perustietue (00) 
                """

                versio = f.read(3)
                
                tilinumero = f.read(14)
                
                tiliote_nro = f.read(3)
                tiliote_alkupvm = f.read(6)
                tiliote_loppupvm = f.read(6)

                tiliote_muodostettu_pvm = f.read(6)
                tiliote_muodostettu_klo = f.read(4)

                asiakastunnus = f.read(17)

                alkusaldo_pvm = f.read(6)
                alkusaldo = self._read_raha(f)

                tiliote_tietue_lkm = f.read(6)
                valuutta = f.read(3)
                tili_nimi = f.read(30)
                tili_limitti = f.read(18)
                tili_omistaja = f.read(35)
                
                pankki = f.read(40)
                konttori = f.read(40)
                konsernitili = f.read(30)
                iban = f.read(30)

            elif tietuetunnus == '10':
                """
                4.5 Tapahtuman perustietue (10, 80)
                """

                p = payment.Payment()

                p.tapahtuma = f.read(6)
                p.arkistointitunnus = f.read(18)
                p.kirjauspvm = f.read(6)
                p.arvopvm = f.read(6)
                p.maksupvm = f.read(6)

                p.tapahtumatunnus = f.read(1)
                p.kirjausselite_koodi = f.read(3)
                p.kirjausselite_teksti = f.read(35)

                p.summa = self._read_raha(f)

                p.kuittikoodi = f.read(1)
                p.valitystapa = f.read(1)

                p.vastapuoli = f.read(35)
                p.vastapuoli_nimi_lahde = f.read(1)

                p.vastatili_nro = f.read(14)
                p.vastatili_muuttunut = f.read(1)

                p.viite = f.read(20)
                p.lomakenro = f.read(8)
                p.tasotunnus = f.read(1)

                p.organize()
                
                data.append(p)

            elif tietuetunnus == '11':
                """
                4.6 Tapahtuman lisätietue (11, 81)
                Lisätietueita käytetään viestien välitykseen. ...
                """

                tyyppi = f.read(2)
                size -= 2
                
                if tyyppi == '00':
                    """ 
                    vapaa viesti
                    """
                    if not data[-1].viesti:
                        data[-1].viesti = ''
                    data[-1].viesti += f.read(size)

                elif tyyppi == '03':
                    """
                    Korttitapahtuman tiedot, lisätiedon tyyppi = 03 
                    """
                    f.read(size)

                elif tyyppi == '06':
                    """
                    Toimeksiantajan tiedot, lisätiedon tyyppi = 06 
                    """
                    f.read(size)

                elif tyyppi == '09':
                    """
                    Nimitarkenteen tiedot, lisätiedon tyyppi = 09 
                    """
                    f.read(size)

                elif tyyppi == '11':
                    """
                    Euromaksualueen tilisiirron lisätyyppi, lisätiedon tyyppi = 11 
                    """
                    f.read(size)

                else:
                    print "Tuntematon lisätietueen tyyppi %s" % tyyppi
                    f.read(size)

            elif tietuetunnus == '40':
                """
                4.7 Saldotietue (40) 
                Saldotietueita on päivätiliotteella vain yksi. 
                Kausitiliotteella on jokaista tapahtumallista kirjauspäivää kohden saldotietue. Käytettävissä oleva saldo 
                on nollaa muilla kuin viimeisen tapahtumallisen päivän saldotietueella. Viimeisellä saldotietueella on 
                käytettävissä oleva saldo kyseiseltä päivältä.  
                """

                f.read(size)

            elif tietuetunnus == '50':
                """
                4.8 Kumulatiivinen perustietue (50) 
                Kumulatiivisella perustietueella kerrotaan tiliotteella olevien panojen ja ottojen kappale- ja rahamäärät.
                """

                f.read(size)

            else:
                print "Tuntematon tietuetunnus %s" % tietuetunnus
                f.read(size)

            f.read(2) # \r\n

        return data

class TabSeperated(Tiliote):
    def __init__(self, filename):
        super(TabSeperated, self).__init__(filename)

    def _read_pvm(self, pvm):
        (d,m,y) = pvm.split(".")
        return "%04d-%02d-%02d" % (int(y), int(m), int(d))

    def parse(self):
        payments = []
        for r in self.f:
            if r.strip():
                data = r.strip().split('\t')
                try:
                    p = payment.Payment()
                    p.kirjauspvm = self._read_pvm(data[0])
                    p.arvopvm = self._read_pvm(data[1])
                    p.maksupvm = self._read_pvm(data[2])
                    p.summa = float(data[3].replace(',','.'))
                    p.vastapuoli = data[4] # or data[7] ?
                    p.vastatili_nro = data[5]
                    p.viite = data[8]
                    # Viesti on tai ei ole, muut on
                    if len(data) > 10:
                        p.viesti = data[10]

                    p.organize()

                    payments.append(p)
                    
                except IndexError:
                    pass
                except ValueError:
                    pass
        return payments
