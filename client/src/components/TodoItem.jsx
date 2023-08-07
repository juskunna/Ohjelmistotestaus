import { useState } from "react"
import { toggleDoneWithId } from "../services/http";

export function TodoItem({ todo, setSelectedId }) {
  const [done, setDone] = useState(todo.done);

  const toggle = () => {
    
    const newDoneValue = !done;

    setDone(newDoneValue);
    toggleDoneWithId(todo.id, newDoneValue).then(() => {
      
    });
  };

  return (
    <div onClick={()=> setSelectedId(todo.id)} className="todo-item">
    <p>{todo.title}</p>
    <input
      checked={done}
      value={done}
      onChange={toggle}
      onClick={(e) => e.stopPropagation()}
      type="checkbox"/>
    </div>
  );
}