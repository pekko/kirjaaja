#!/usr/bin/python
# *-* encoding: utf-8 *-*

import string

import group
import laskutus
import settings
import verkkomaksut

s = group.Sort()
vm = False

def init_verkkomaksut(vm_filename):
    global vm
    vm = verkkomaksut.get_payments(vm_filename)

class Payment(object):
    """
    Yläluokka maksuille, käytännössä abstrakti, oikeastikin jos jaksaisin tehdä sellaisen.. 
    (Miten tää meni pythonissa?)
    """

    def __init__(self):
        self.viesti = ''
        self.counteraccount = settings.accounts.pankkitili
        
    def __str__(self):
        return "%10.2f %35s %s" % (self.summa, self.vastapuoli, self.viesti)

    def organize(self):
        if self.is_verkkomaksut():
            self.__class__ = VerkkomaksutPayment
        elif self.is_myynti():
            self.__class__ = MyyntiPayment
        elif self.is_osto():
            self.__class__ = OstoPayment

        self.summa = abs(self.summa)
        self.hoax_init()

    def is_verkkomaksut(self):
        vasta = self.vastapuoli.lower()
        return ("verkkomaksut" in vasta or "paytrail" in vasta) and self.summa > 0

    def is_myynti(self):
        return self.summa > 0

    def is_osto(self):
        return self.summa < 0

    def hoax_init(self):
        # Just an abstract method
        raise Exception('I should not be called. Payment::hoax_init')
    def accounting(self):
        raise Exception('I should not be called. Payment::accounting')


class VerkkomaksutPayment(Payment):
    """
    Lasku, joka on maksettu Suomen Verkkomaksujen kautta pankkipainikkeella/vast.
    Laskutusjärjestelmä on jo varmistanut, että tämä on ok, ei tehdä enempää tarkistuksia.
    """

    def __init__(self):
        return self.hoax_init()
    
    def hoax_init(self):
        if not vm:
            raise Exception("Verkkomaksut-file puuttuu. En tee.")

        for v in vm:
            if int(v['reference']) == int(self.viite):
                self.batch = v['batch']
                return
        
        raise Exception("En löytänyt verkkomaksutilitystä viitteellä %d. En tee." % (int(self.viite)))

    def __str__(self):
        result = ""
        
        if not self.batch:
            return "VM :("

        for p in self.batch:
            result += "VM %-15s %10.2f %s\n" % (p['account'], p['amount'], p['description'])
        return result

    def accounting(self):
        if not self.batch:
            return None

        result = []
        total = 0.0

        # puretaan batch riveiksi
        for p in self.batch:
            result.append({
                'amount' : p['amount'],
                'account' : p['account'],
                'debit' : False,
                'description' : p['description']
            })
            total += p['amount']

        # vastatilille
        result.append({
            'amount' : total,
            'account' : self.counteraccount,
            'debit' : True,
            'description' : 'Tilitys Suomen Verkkomaksuilta'
        })
        return {
            'meta': {
                'date': self.kirjauspvm, 
                'type':'verkkomaksut',
                'reference' : int(self.viite),
            }, 
            'payments': result
        }

class MyyntiPayment(Payment):
    """
    Myyntilasku, joka on maksettu käsin (pdf-lasku tjsp).
    Tarkistettava käsin, että on ok - summa!
    """

    def __init__(self):
        return self.hoax_init()

    def hoax_init(self):
        if self.viite.strip():
            self.viite = int(self.viite)

        payment_id = laskutus.get_payment_by_refnumber(self.viite)
    
        if payment_id == 0:
            self.description = ""
            self.account = settings.accounts.muut_kulut
        else:
            self.description = laskutus.get_description(payment_id)
            self.account = laskutus.get_account(payment_id)
            if not self.is_verkkomaksut():
                laskutus.mark_paid(payment_id, self.summa, self.kirjauspvm)

    def __str__(self):
        return "MY %-15s %s" % (self.account, super(MyyntiPayment, self).__str__())

    def accounting(self):
        return {
        'meta':
            {
                'date' : self.kirjauspvm,
                'type': 'myynti'
            },
        'payments': 
            [
                {
                    'amount' : self.summa,
                    'account' : self.account,
                    'debit' : False,
                    'description' : self.description
                },
                {
                    'amount' : self.summa,
                    'account' : self.counteraccount,
                    'debit' : True,
                    'description' : self.description
                }
            ]
        }

class OstoPayment(Payment):
    def __init__(self):
        return self.hoax_init()
    
    def hoax_init(self):
        self.summa = "%.2f" % self.summa # TODO vitun floatit

    def __str__(self):
        return "OS %-15s %s %s" % (self.group, super(OstoPayment, self).__str__(), self.viesti)

    def accounting(self):
        self.group = s.sort(self)
        if self.group is None:
            self.group = settings.accounts.muut_kulut

        self.account = self.group # TODO etsipä paremmin
        self.description = "%s, %s" % (string.capwords(self.vastapuoli.strip()), self.viesti.strip())
        self.description = self.description[:100]

        return {
        'meta':
            {
                'date' : self.kirjauspvm,
                'type' : 'osto',
            },
        'payments': 
            [
                {
                    'amount' : self.summa,
                    'account' : self.account,
                    'debit' : True,
                    'description' : self.description
                },
                {
                    'amount' : self.summa,
                    'account' : self.counteraccount,
                    'debit' : False,
                    'description' : self.description
                }
            ]
        }
