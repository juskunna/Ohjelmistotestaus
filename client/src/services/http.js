const TODO_API_BASE_URL = "http://127.0.0.1:8000"


// Yleiskäyttöinen rajapintafunktio ToDo-API:lle.
// Mahdollistaa yleisten rajapintaan liittyvien asetusten asettamisen 
// kaikille kyselyille jotka tehdään nimenomaiseen rajapintaan.
// Esimerkkinä tietyt headerit jotka rajapinta voisi vaatia kaikilta requesteilta.
async function todoApi(endpoint, options = {}) {

    const response = await fetch(TODO_API_BASE_URL + endpoint, options)

    // response.ok on true jos http-statuskoodi on pienempi kuin 300, muutoin se on false.
    if (!response.ok) throw new Error("Request failed with statuscode: " + response.status)

    const data = await response.json()

    return data
}

// Tehdään funktiot kaikille rajapinnan avainominaisuuksille. 
// Tämän tarkoituksena on pitää rajapintaan liittyvät toiminnallisuudet 
// erillään käyttöliittymäkomponenteista. Asynkronisten operaatioiden virheiden 
// käsittely toteutetaan muualla koodissa.


// Muuttaa yksinkertaisen javaScript objektin query-stringiksi.
// Palauttaa tyhjän stringin jos params on undefined tai tyhjä objekti {}
function createQueryParams(params) {

    if(!params) return ""

    return "?" + new URLSearchParams(Object.entries(params)).toString()
}

// Vaatimusmäärittelyn tehtävään 1 (1p/3p) ja tehtävään 2 (3p/4p).
// Toteuta funktioon koodi joka hakee todoApi funktiota 
// käyttämällä rajapinnasta listan todo-tehtäviä. 
// Funktio ottaa parametrina objektin joka sisältää datan jolla rakennetaan URL:iin query-parametrit.
// params muuttuja voi olla tyhjä objekti {}, {done:true} tai {done:false}.
export async function getTodos(params) {
  // Voit hyödyntää tässä createQueryParams funktiota
  const todos = await todoApi("/todos" + createQueryParams(params))
  // Funktio palauttaa listan todo-tehtäviä
  return todos
}

// Vaatimusmäärittelyn tehtävään 3 (2p/3p).
// Toteuta funktioon koodi joka luo uuden todo-tehtävän käyttämällä todoApi funktiota.
export async function createTodo(newTodo) {
    
  const todo = await todoApi("/todos", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(newTodo),
    })

    return todo
  // Funktio palauttaa luodun todo-tehtävän, paluuarvoa ei välttämättä käytetä muualla koodissa.
}

// Vaatimusmäärittelyn tehtävään 4. (2p/3p)
// Toteuta funktioon koodi joka poistaa todo-tehtävän id:n perusteella 
// rajapinnasta käyttämällä todoApi funktiota.
export async function removeTodoById(id) {
  await todoApi(`/todos/${id}`, {
    method: "DELETE"
  })
}

// Vaatimusmäärittelyn tehtävään 5 (1p/4p).
// Toteuta funktioon koodi joka hakee todoApi funktiota 
// käyttämällä rajapinnasta yksittäisen todo-tehtävän tiedot.
// Todo-tehtävän muokkaamista varten tarvitaan ajantasainen tieto siitä että
// mikä data kyseisellä id:llä olevalla todo-tehtävällä on ennen sen muokkaamista.
export async function getTodoById(id) {
  const todo = await todoApi(`/todos/${id}`)
  // Palauttaa todo-tehtävän annetulla id:llä
  return todo
}

// Vaatimusmäärittelyn tehtävään 5. (2p/4p)
// Toteuta funktioon koodi joka muokkaa olemassa olevaa todo-tehtävää 
// rajapinnassa käyttämällä todoApi funktiota.
// Tässä tapauksessa rajapinta haluaa id:n myös path parametrina.
// (Voit halutessasi muokata python koodia niin että path parametria ei tarvita vaan id katsotaan
// itse todo-tehtävän datasta.)
export async function updateTodoWithId(id, editedTodo) {
  const updatedTodo = await todoApi(`/todos/${id}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(editedTodo)
  })
  return updatedTodo
  // Palauttaa rajapinnassa muokatun todo-tehtävän
}

// Vaatimusmäärittelyn tehtävään 6. (2p/3p)
// Toteuta funktioon koodi joka päivittää rajapinnassa id:n perusteella yksittäisen
// todo-tehtävän done-statuksen. Done voi olla joko true tai false
export async function toggleDoneWithId(id, currentDone) {
  // Palauttaa objektin { done: true } tai { done: false }
  const toggle = await todoApi(`/todos/${id}/${currentDone}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    
  });
  return toggle
}
