# Tuodaan datetime kirjasto
from datetime import datetime
# Tuodaan Response luokka fastapi kirjastosta
from fastapi import FastAPI, Response
from pydantic import BaseModel
# Tuodaan pythonin mukana tuleva sqlite kirjasto projektiin
import sqlite3
from fastapi.middleware.cors import CORSMiddleware



# Avataan sqlite yhteys ja asetetaan se muuttujaan con
con = sqlite3.connect("todos.sqlite", check_same_thread=False)

# Sql kysely jolla luodaan todo tietokanta jos sellaista ei vielä ole (... IF NOT EXISTS ...)
# Luodaan seuraavat kolumnit kantaan: id, title, description, done, created_at
sql_create_todo_table = "CREATE TABLE IF NOT EXISTS todo(id INTEGER PRIMARY KEY, title VARCHAR, description VARCHAR, done INTEGER, created_at INTEGER)"

# Suoritetaan sql kysely tietokannan luomiseksi
with con:
    con.execute(sql_create_todo_table)

class TodoItem(BaseModel):
    id: int       
    title: str    
    done: bool
    # Lisätään TodoItem luokkaan description joka on str tyyppinen sekä created_at,
    # joka tulee olemaan epoch aikaleima sekunteina. 
    description: str 
    created_at: int 

# Tehdään NewTodoItem luokka jota käytetään uuden todon tekemisessä.
# Tämä tehdään siksi että id, created_at ja done asetetaan palvelimen toimesta 
# ja niitä on näin ollen turhaa pyytää clientilta
class NewTodoItem(BaseModel):
    title: str
    description: str

app = FastAPI()

# Lisätään CORS middleware FastAPI instanssille. 
# Asetetaan kehitysvaiheessa kaikki originit wildcardiksi *:llä
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Suljetaan tietokantatyhteys kun fastapi palvelin sammutetaan
@app.on_event("shutdown")
def database_disconnect():
    con.close()

@app.get('/todos')
def get_todos(response: Response, done: bool | None = None):
    try:
        with con:
            if done != None:
                # Jos query parametri done on asetettu, haetaan tietokannasta kaikki todot joilla done on False tai True.
                # SQL tietokannassa ei ole erikseen boolean arvoa vaan arvo on joko 0 tai 1, tätä varten done muutetaan kokonaisluvuksi (int(done),).
                # (int(done),) sulut ja pilkku muuttujan lopussa tarkoittaa että kyseessä on tuple jossa on yksi arvo.
                cur = con.execute("SELECT id, title, description, done, created_at FROM todo WHERE done = ?", (int(done),))
            else:
                # Jos query parametri done ei ole asetettu, haetaan kaikki todot kannasta.
                cur = con.execute("SELECT id, title, description, done, created_at FROM todo")

            # Alustetaan lista joka voi sisältää TodoItem tyyppisiä objekteja
            values: list[TodoItem] = []

            # Haetaan tietokannan kursorilla suoritetun kyselyn tulokset ja lisätään ne "values" listaan
            for item in cur.fetchall():
                # item on tässä tuple joka sisältää yhden rivin datan, puretaan se omiin muuttujiinsa.
                # Järjestys on sama mikä sql kyselyssä on määritetty
                id, title, description, done, created_at = item
                # Tehdään tietokannasta haetun datan pohjalta uusi TodoItem joka lisätään listaan "values"
                todo = TodoItem(id=id, title=title, description=description, done=done != 0, created_at=created_at)
                values.append(todo)
            
            # Palautetaan clientille todo lista. FastAPI muuttaa sen JSON formaattiin automaattisesti.
            return values
    except Exception as e:
        response.status_code = 500
        return {"err": str(e)}


@app.get('/todos/{id}')
def get_todo_by_id(id: int, response: Response):
    try:
        with con:
            # Sql kysely yksittäisen todon hakemiseksi id:n perusteella
            cur = con.execute(
                "SELECT id, title, description, done, created_at FROM todo WHERE id = ?", (id,))

            result = cur.fetchone()

            # Jos result on tyhjä, se tarkoittaa ettei tietokannasta
            # löytynyt path parametrina saadun id:n perusteella todo itemiä.
            # Palautetaan clientille tällöin virhe viesti ja asetetaan statuskoodiksi 404
            if result == None:
                response.status_code = 404
                return {"err": f"Todo item with id {id} does not exist."}

            # Puretaan result tuplen sisältö omiin muuttujiinsa, järjestys on sama kuin
            # sql kyselyssä.
            id, title, description, done, created_at = result

            # Tehdään uusi TodoItem objekti tietokannasta saadun datan perusteella
            # Muutetaan done muuttujan arvo boolean arvoksi.
            return TodoItem(
                id=id,
                title=title,
                description=description,
                done=bool(done),
                created_at=created_at
            )
    except Exception as e:
        response.status_code = 500
        return {"err": str(e)}


@app.post('/todos')
# Vaihdetaan TodoItem -> NewTodoItem
# Lisätään uusi parametri response jonka tietotyypiksi asetetaan Response luokka.
# response parametrin tietoja muokkaamalla voidaan lisätä responseen esimerkiksi räätälöityjä
# HTTP- headereita tai muuttaa responsen statuskoodia
def create_todo(todo_item: NewTodoItem, response: Response):

    # Tietokantakysely voi epäonnistua joten mahdollisen virheen tapahtuessa try-except
    # ottaa virheestä "kopin" jonka jälkeen voidaan palauttaa sopiva virheviesti 
    # clientille.
    try:
        # Otetaan tietokantayhteys käyttöön
        with con:
            # Luodaan aikaleima (Aikaleima on tässä kuluneet sekunnit vuodesta 1970 https://en.wikipedia.org/wiki/Unix_time).
            dt = datetime.now()
            ts = int(datetime.timestamp(dt))

            # Suoritetaan parametrisoitu tietokantakysely jolla luodaan uusi rivi todo kantaan.
            # Koska (todo_item.title, todo_item.description, int(False), ts,) on tyyppiä Tuple niin 
            # viimeinen pilkku ts:n jälkeen on tarpeellinen!
            # HUOM! Kun teet omia ratkaisuja koodiin niin katso että sql kyselyn 
            # parametrit menevät oikeille paikoille tuplessa!
            cur = con.execute("INSERT INTO todo(title, description, done, created_at) VALUES(?, ?, ?, ?)", (todo_item.title, todo_item.description, int(False), ts,))
            
            # Asetetaan responsen statuskoodiksi 201 eli created
            response.status_code = 201
        
            # Jotta ylimääräiseltä tietokantakyselyltä vältytytään niin voidaan palauttaa uusi TodoItem
            # tiedossa olevilla arvoilla jotka tiedetään nyt olevan samat myös tietokannassa.
            # cur.lastrowid sisältää luodun todo:n id:n tietokannasta.
            return TodoItem(id=cur.lastrowid, title=todo_item.title, done=False, description=todo_item.description, created_at=ts)
            
    except Exception as e:

        # Jos tietokantakysely epäonnistuu kerrotaan siitä tässä clientille asettamalla responselle 
        # sopiva statuskoodi, esim. 500 
        response.status_code = 500
        # Palautetaan virhe clientille
        return {"err": str(e)}
    
@app.put('/todos/{id}')
def update_todo(id: int, todo_item: TodoItem, response: Response):
    try:
        with con:
            # Vaikka todo_item sisältää myös id:n ja created_at aikaleiman, niitä ei kuitenkaan haluta clientin voivan muuttaa.
            # Ne voidaan kuitenkin pyytää clientilta requestissa ja tämä onkin suositeltavaa sillä 
            # toiminnallisuuksien toteuttaminen clientin päässä on tällöin myös helpompaa kun data säilyy käsiteltäessä yhdenmukaisena.
            # RETURNING * palauttaa päivitetyn todon tiedot sql kyselyssä.
            cur = con.execute(
                "UPDATE todo SET title = ?, description = ?, done = ? WHERE id = ? RETURNING *", (todo_item.title, todo_item.description, todo_item.done, id,))
            
            result = cur.fetchone()

            if result == None:
                response.status_code = 404
                return {"err": f"Todo item with id {id} does not exist."}

            id, title, description, done, created_at = result

            # Palautetaan päivitetty todo clientille
            return TodoItem(
                id=id,
                title=title,
                description=description,
                done=bool(done),
                created_at=created_at
            )

    except Exception as e:
        response.status_code = 500
        return {"err": str(e)}


# Otetaan uusi done status path parametrina
@app.patch('/todos/{id}/{done}')
# Path parametrit otetaan argumenttina vastaan funktiossa jossa niiden tietotyyppi määritetään
def update_todo_status(id: int, done: bool, response: Response):
    try:
        with con:
            # Päivitetään todon done status path parametrista saadun done arvon perusteella, joka voi olla joko True tai False.
            cur = con.execute("UPDATE todo SET done = ? WHERE id = ? RETURNING done", (int(done), id,))
            result = cur.fetchone()

            if result == None:
                response.status_code = 404
                return {"err": f"Todo item with id {id} does not exist."}
            
            # Palautetaan todon done status clientille esimerkiksi seuraavasti:
            return {"done": bool(result[0])}

    except Exception as e:
        response.status_code = 500
        return {"err": str(e)}


@app.delete('/todos/{id}')
def delete_todo(id:int, response: Response):
    try:
        with con:
            cur = con.execute("DELETE FROM todo WHERE id = ?", (id,))
            
            # Jos muuttuneiden rivien määrä on pienempi kuin yksi, 
            # tiedetään että path paramina saadulla id:llä ei ole löytynyt 
            # todo itemiä tietokannasta. 
            if cur.rowcount < 1:
                response.status_code = 404
                return {"err": f"Can't delete todo item, id {id} does not exist."}

            # Voidaan palauttaa clientille esim. teksti "ok", tämän voi tosin jättää myös tyhjäksi sillä
            # HTTP statuskoodin 200 perusteella tiedetään että poisto on onnistunut. 
            return "ok"

    except Exception as e:
        response.status_code = 500
        return {"err": str(e)}


