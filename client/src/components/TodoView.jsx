import { useState } from "react"
import "./CreateTodo.css"
import { removeTodoById, updateTodoWithId } from "../services/http"
import { Overlay } from "./Overlay";

export function TodoView({setShowCreate, initialTodo }) {

    const [title, setTitle] = useState(initialTodo.title);
    const [description, setDescription] = useState(initialTodo.description);
    const [isEditing, setIsEditing] = useState(false);

    const close = () => {
        setShowCreate(false);
    };

    const onSave = () => {
        if(!title) {
            return;
        }

        const editedTodo = { ...initialTodo, title, description };

        updateTodoWithId(initialTodo.id, editedTodo).then(() => {
            close();
        });
    };

    const onDelete = () => {
        removeTodoById(initialTodo.id).then(() => {
            close();
        });
    
    };


    return (
        <Overlay close={close} headerTitle={isEditing ? 'Muokkaa' : 'Tehtävä'}>
          {isEditing ? (
            <>
              <label htmlFor="title">Otsikko</label>
              <input
                value={title}
                onInput={(e) => setTitle(e.target.value)}
                id="title"
                type="text"
              />
    
              <label htmlFor="description">Kuvaus</label>
              <textarea
                value={description}
                onInput={(e) => setDescription(e.target.value)}
                id="description"
                name=""
                cols="30"
                rows="5"
              ></textarea>
    
              <button onClick={onSave}>Tallenna</button>
              <button onClick={() => setIsEditing(false)}>Takaisin</button>
            </>
          ) : (
            <>
              <p>Otsikko: {initialTodo.title}</p>
              <p>Kuvaus: {initialTodo.description}</p>
              <p>
                Status:
                {initialTodo.done
                  ? 'Tehtävä on suoritettu'
                  : 'Tehtävä on tekemättä'}
              </p>
              <p>
                Luotu:
                {new Date(initialTodo.created_at * 1000).toLocaleString('FI')}
              </p>
    
              <button onClick={() => setIsEditing(true)}> Muokkaa </button>
              <button onClick={onDelete}>Poista</button>
            </>
          )}
        </Overlay>
    );
}