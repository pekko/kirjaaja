# *-* encoding: utf-8 *-*

import sys, re

import log
import settings

DB_DIR = settings.dir+"/data/grouping"

class Sort:
    """
    Lajittelee laskut erinäisten sääntöjen perusteella oikeille tileille.

    TODO: nimeä tää jotenkin paremmin.. Tulevaisuudessa vain ostolaskuille? 
    """

    def __init__(self):
        for f in dir(Sort):
            if f[0:4] == 'init':
                getattr(Sort, f)(self)

    def sort(self, payment):
        """
        Varsinainen sort.
        """
        grouped = {}

        for f in dir(Sort):
            if f[0:4] == 'sort' and len(f) > 4:
                group = getattr(Sort, f)(self, payment)

                if group is not None:
                    return group
                    
        log.msg("Maksulle ei löytynyt tiliä. Maksun vastapuoli: %s, viesti: %s" % (payment.vastapuoli.strip(), payment.viesti.strip()), "WARN")
        return None

    def init_firstword(self):
        fw_db_file = open(DB_DIR+'/first_word_db.txt')
        self.fw_db = {}
        for r in fw_db_file:
            fields = r.split()
            self.fw_db[fields[1]] = fields[0]

    def sort_firstword(self, payment):
        """ Haetaan viestin ekan sanan perusteella """
        # get db
        search = payment.viesti.split(' ')[0].lower()

        if not search:
            return None
        
        if search in self.fw_db:
            payment.viesti = ' '.join(payment.viesti.split()[1:])
            return self.fw_db[search]
        
        return None

    def pois_init_regexp(self):
        db_file = open(DB_DIR+'/re_db.txt')
        self.re_db = {}
        for r in db_file:
            fields = r.split(None, 2)
            if fields[0] not in self.re_db:
                self.re_db[fields[0]] = []
            self.re_db[fields[0]].append(re.compile(fields[1], re.IGNORECASE))

    def pois_sort_regexp(self, payment):
        """ Regexp-haku """
        for (tili, re_list) in self.re_db.iteritems():
            for re in re_list:
                if re.search(payment.viesti):
                    return tili

        return None

    def init_opp(self):
        db_file = open(DB_DIR+'/opp_db.txt')
        self.opp_db = {}
        for r in db_file:
            fields = r.split(None, 1)
            if fields[0] not in self.opp_db:
                self.opp_db[fields[0]] = []
            self.opp_db[fields[0]].append(fields[1].strip().lower())

    def sort_opp(self, payment):
        """ Haetaan vastapuolen perusteella """
        for (tili, search_list) in self.opp_db.iteritems():
            for search in search_list:
                # if payment.vastapuoli:
                #   print "Searching %s in %s" % (search.lower())
                if search in payment.vastapuoli.lower():
                    return tili

        return None

    def sort_complex_rules(self, payment):
        """ Koodissa olevat säännöt. """
        if "SUOMEN VERKKOMAKSUT" in payment.vastapuoli and payment.summa < 0:
            return settings.accounts.pankkikulut
        return None
