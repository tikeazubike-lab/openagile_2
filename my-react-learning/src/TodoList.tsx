import { useReducer } from "react";

const initialState = {
    todos: [],
    filter: 'ALL'
}

function todoReducer(state, action){
    
}


export default function TodoList(){
    const [state, dispatch] = useReducer(todoReducer, initialState)
}