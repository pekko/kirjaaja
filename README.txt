KIRJAAJA
========

Pekon (pekko.lipsanen@iki.fi, pecko@irc) tekemä viritys. Yhdistää rahadataa eri 
lähteistä ja muodostaa siitä kirjanpitodataa.

Riippuvuudet
------------
* Laskutusjärjestelmä
* Kirjanpito: Tilitin-softa 
    * joka käyttää postgresql:ää
* Python 2.6 (todo tarkista versio)


Komponentit
-------------

                  +-----------------+
    +---------+   | Verkkomaksujen  |
    | Tiliote |   | tilitysraportti |
    +---------+   +-----------------+
            |       |
        tsv |       | csv
            v       v
          +----------+                    +------------------+
          | KIRJAAJA |  <-------------->  | Laskutus (MySQL) |
          +----------+                    +------------------+
                |
                |
                v
          +------------+                  +---------+
          | PostgreSQL | <------------->  | Tilitin |
          +------------+                  +---------+
                |
                | XML
                v
          +-------------+
          | Google Docs |
          +-------------+


Data flow
---------

                   +--------+ 
                   | Pankki |
                   +--------+
                        |
                        v
                   +---------+ 
                   | Tiliote |
                   +---------+
                        |
                        v
                  +------------+
                  | Tapahtumat |
                  +------------+
                        |
                        v
+---------+        +=========+       +------+                
| Verkko- |  <---  | Tyyppi? | --->  | Osto |
| maksut  |        +=========+       +------+
+---------+             |               |
    |                   |               |
    v                   v               v
+----------+       +---------+     +--------------+
| Tilitys- |       |  Myynti |     | Viestikenttä |
| raportti |       +---------+     +--------------+
+----------+        /                /         
          \        /                /  
           \      /                /  
            v    v                /
          +----------+           /
          | Laskutus |          /
          +----------+         /
                    \         / 
                     \       / 
                      v     v
                    +---------+         +-------------+
                    | Tilitin | ------> | Google Docs |
                    +---------+         +-------------+