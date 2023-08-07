import { useEffect, useState } from "react"
import { AppTitle } from "./components/AppTitle"
import { TodoButtons } from "./components/TodoButtons"
import { CreateButton } from "./components/CreateButton"
import { CreateTodo } from "./components/CreateTodo"
import { TodoList } from "./components/TodoList"
import { getTodoById, getTodos } from "./services/http"
import { TodoView } from "./components/TodoView"


function App() {
  const buttonData = [
    {
        name: "Kaikki",
        active: "ALL"
    },
    {
        name: "Tekemättä",
        active: "NOT_DONE"
    },
    {
        name: "Tehdyt",
        active: "DONE"
    },
];

  const [showCreate, setShowCreate] = useState(false);
  const [todos, setTodos] = useState([]);
  const [activeKey, setActiveKey] = useState(buttonData[1].active);
  const [selectedTodo, setSelectedTodo] = useState();

  const buttons = buttonData.map((button, id) => {
    return (
      <button
        key={id}
        onClick={() => setActiveKey(button.active)}
        style={{ backgroundColor: button.active === activeKey && "aqua" }}
      >
        {button.name}
      </button>
    );
  });

  const selectTodo = (id) => {
    getTodoById(id).then((todo) => {
      setSelectedTodo(todo);
    });
  };

  useEffect(() => {
     const params = {};

    if(activeKey !== "ALL") {
      params.done = activeKey === "DONE";
    }

   getTodos(params).then((todos)=> {
    setTodos(todos);
   });
  }, [showCreate, activeKey, selectedTodo])
 
  return (
    <>
      <AppTitle></AppTitle>
      <TodoButtons buttons={buttons}></TodoButtons>
      <TodoList todos={todos} setSelectedId={selectTodo}></TodoList>
      <CreateButton onClicked={()=> setShowCreate(!showCreate)}></CreateButton>
      {showCreate && <CreateTodo setShowCreate={setShowCreate}></CreateTodo>}
      {selectedTodo && <TodoView setShowCreate={()=> setSelectedTodo(null)} initialTodo={selectedTodo}></TodoView>}
    </>
  );
}


export default App
