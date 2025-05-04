# PortfolioFoorumi


* Käyttäjä pystyy luomaan sovellukseen tunnuksen sekä kirjautumaan sisään, että ulos.
* Käyttäjä pystyy tämän lisäksi myös lisäämään, muokkaamaan ja poistamaan tietokohteita sekä etsimään niitä foorumilta.
* Käyttäjät pystyvät keskustelemaan keskenään lankojen alla.
* Käyttäjillä on käyttäjäsivut, jotka kertovat sitä katsoville erilaisia tietoja käyttäjän toiminnasta sovelluksessa.
* Käyttäjät pystyvät äänestämään eri lankoja.
* Käyttäjät voivat lisätä omille langoilleen erilaisia tietokohteita esimerkiksiyrityksen kotimaa, pörssi yms.
* Käyttäjät voivat myös etsiä lankoja hakusanalla.
* Käyttäjät voivat kommentoida langoille.
* Käyttäjät voivat lisäämään kuvia lankoihinsa.

## sovelluksen asennus

Asenna "flask" -kirjasto:

$pip install flask

Luo tietokannan taulut sekä lisää alkutiedot tietokantaan:

$sqlite3 database.db < schema.sql
$sqlite3 database.db < init.sql

Käynnistä sovellus:

$flask run 
