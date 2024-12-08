# Wilma kalenteriin

## Kuvaus

Wilma kalenteriin on python sovellus, joka hakee Wilmasta kotitehtävät ja lisää ne käyttäjän valitsemaan Todoist projektiin.

Päätoiminnallisuudet löytyvät **WilmaTask.py** tiedostosta.

### Tausta 

Halusin luoda sovelluksen, jolla voisin helposti lisätä Wilman kotitehtävät Todoistiin. Tämä helpottaa lasten kotitehtävien seuraamista. Todoist taas lisää tehtävät perheen yhteiseen Google kalenteriin. Koin tämän kaikista toimivammaksi ratkaisuksi.

## Asennus

Suosittelen luoda virtuaaliympäristön tätä sovellusta varten. Voit lukea lisää virtuaaliympäristöstä [täältä](https://www.geeksforgeeks.org/python-virtual-environment/) .Virtuaaliympäristön luominen onnistuu seuraavalla komennolla:

Asenna virtuaaliympäristö moduuli
```bash
pip install virtualenv
```

Navigoi projektin juureen ja luo virtuaaliympäristö komennolla

```bash
python3 -m venv .venv
```
tai 

```bash
python -m venv .venv
```

Aktivoi virtuaaliympäristö komennolla

Windows
```bash
.venv\Scripts\activate
```
Linux tai Mac tietokoneissa
```bash
source .venv/bin/activate
```

Tiedät, että virtuaaliympäristö on aktivoitu, kun näet (.venv) komentorivellä. Nyt voit asentaa riippuvuudet siihen.

## Riippuvuudet

Asenna tarvittavat kirjastot komennolla
    
```bash
pip install -r requirements.txt
```

# Käyttö ensimmäisellä kerralla

Kun ajat sovellusta ensimmäisen kerran tarkistetaan toimiiko Wilma. Luo virtuaaliympäristö ja asenna riippuvuudet yllä olevin ohjein. Muuta tiedostossa muuttujat.txt olevat muuttujat haluamiksesi ja nimeä tiedosto muuttujat.py-tiedostoksi. Katsoakseen toimiiko Wilma sinun täytyy määritellä ainostaan nämä:

```python
WILMA_URL="wilman soite yleensä .inschool.fi loppuinen"
WILMA_LOGIN="kayttajatunnus"
WILMA_PASSWORD="salasana"
WILMA_STUDENT="Etunimi Sukunimi"
WILMA_STUDENTS="Etunimi Sukunimi,Etunimi Sukunimi"
LOGIN_ROUTE = "/login"
COOKIE="Wilma2LoginID"
```

Älä muuta LOGIN_ROUTE ja COOKIE muuttujia. 

***Aja nyt WilmaTask.py-tiedosto. Jos saat status koodiksi 200 jne. niin olet valmis siirtämään MongoDB tietokantaan.***

Mikäli saat virheen kirjautuessaan niin tarkista siirry BeautifulSoup osioon ja tarkista LOGIN_ROUTE ja COOKIE.


### Tietokanta

Tietokantana on osassa MongoDB. Lisätietoa miten luoda MongoDB tietokanta [täältä](https://www.mongodb.com/docs/atlas/getting-started/).

Voit testata tietokantayhteyden ajamalla mongodbconnectiontest.py -tiedoston.


### Vuokaavio

![vuokaavio](/data/kuvat/Wilmakalenteri_flow.jpg)

### Funktiot

| **Funktion nimi**             | **Kuvaus**                                           | **Parametrit**                                                                                               | **Palauttaa**                          |
|-------------------------------|-----------------------------------------------------|------------------------------------------------------------------------------------------------------------|---------------------------------------|
| `wilma_signin()`              | Kirjautuu Wilmaan ja palauttaa kirjautumistiedot sekä sessionin. | Ei parametreja.                                                                                           | Tuple: `(login_req, session)`         |
| `wilma_student(login_req, session, wilma_student=WILMA_STUDENT)`             | Hakee oppilaan tiedot Wilmasta.                      | `login_req`: kirjautumistiedot, `session`: istunto, `wilma_student`: oppilaan nimi (str, oletus).         | Oppilaan URL tai None (str)            |
| `wilma_subject(session, oppilas_url)`             | Hakee oppilaan aineet Wilmasta.                      | `session`: istunto, `oppilas_url`: oppilaan sivun URL.                                                    | Lista tupleista: `[(url, teksti)]`     |
| `wilma_homeworks(session, link_url, linktext)`           | Hakee kotitehtävät annetulta sivulta.                | `session`: istunto, `link_url`: aineen URL, `linktext`: aineen nimi.                                      | Lista sanakirjoja: `[{...}]`           |
| `connect_mongodb(collection)`           | Yhdistää MongoDB-tietokantaan ja palauttaa kokoelman. | `collection`: kokoelman nimi (str).                                                                       | MongoDB-kokoelma                       |
| `add_homework_to_db(subject_text, homework, db)`        | Lisää kotitehtävän tietokantaan, jos se on uniikki.   | `subject_text`: oppiaine (str), `homework`: tehtävä (dict), `db`: MongoDB-kokoelma.                       |                |
| `add_unique_item_mongodb(homework, db)`   | Tallentaa uniikin dokumentin tietokantaan.           | `homework`: tehtävän tiedot (dict), `db`: MongoDB-kokoelma.                                               |                |
| `find_items_mongodb(collection, query={})`        | Hakee dokumentteja tietokannasta annetun kyselyn avulla. | `collection`: MongoDB-kokoelma, `query`: kysely (dict, oletus tyhjä).                                     | Lista löydetyistä dokumenteista.       |
| `add_item_to_project(access_token, command)`       | Lisää tehtävän Todoist-projektiin.                   | `access_token`: Todoist API-tunnus, `command`: tehtäväkomento (dict).                                     |                |


![funktiot](/data/kuvat/funktiot_wilma.png)

## BeautifulSoup

Tiedosto Wilma.py ja WilmaTask.py käyttää BeautifulSoup kirjastoa Wilman sivujen parsimiseen. Lisätietoa BeautifulSoupista löytyy [täältä](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

Sen käyttö saattaa vaatia Wilma -sivuston tarkempaa tutkimista.

### Kehittäjätyökalut (Developer Tools)

Seuraavat tarvitset kirjautuakseen Wilmaan. Mikäli sinulla on eri cookie ja /login -polku niin muuta ne myös muuttujat.py tiedostoon.

Navigoi Wilma -sivustolle ja avaa kehittäjätyökalut joko painamalla F12 tai oikealla hiiren näppäimellä ja valitse "Inspect". 

Navigoi kehittäjätyökaluissa "Network" välilehdelle. Täppää "Preserve log" ja yritä kirjautua (pelkkä "Kirjaudu sisään" ilman tunnuksia riittää).

Nyt kehittäjätyökaluissa pitäisi näkyä login POST pyyntö. Etsi login pyyntö. Headers välilehdeltä löytyy tarvitsemanne payload tiedot. Nämä ovat otsikomme.

![Headers](/data/kuvat/network_tab.JPG)

Lisäksi tarvitsemme session cookien. Nämä löytyvät "Cookies" välilehdeltä tai samalta paikasta, josta löysimme payload tiedot "Headers" välilehdeltä. Tarkista Set-Cookie cookien nimi.

![Cookies](/data/kuvat/setcookie.JPG)


## Skripti suotittamiseen

Olen ajoittanut WilmaTask.py -tiedoston ajettavaksi joka päivä klo 14:20, jotta joka päivä ehtisi tulla kaikki kotiläksyt.


```powershell

# Polku Python-suoritusohjelmaan virtuaaliympäristössä
$pythonExe = "C:POLKU_SOVELLUKSEEN.venv\Scripts\python.exe"

# Polku Python-skriptiin
$scriptPath = "C:POLKU_SOVELLUKSEEN\WilmaTask.py"

# Skriptin argumentti
$arguments = "$scriptPath"

# Tehtävän nimi
$taskName = "WilmaTaskScript"

# Tehtäväajastin
$action = New-ScheduledTaskAction -Execute $pythonExe -Argument $arguments

# Laukaisin, joka suoritetaan päivittäin tiettyyn aikaan, esim. 14:20
$trigger = New-ScheduledTaskTrigger -Daily -At 14:20

# Rekisteröidään tehtävä ajastimeen
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName $taskName -Description "Suorittaa WilmaTask.py-skriptin päivittäin"

```