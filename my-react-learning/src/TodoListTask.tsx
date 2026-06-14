import { useReducer } from "react";

// 1. Define the state shape
interface Todo {
    id: number;
    text: string;
    completed: boolean;
}

interface TodoListState {
    todos: Todo[];
    filter: "all" | "active" | "completed";
}

// 2. Define action types (pseudocode provided - implement this)
type TodoListAction = 
    | { type: "ADD_TODO"; payload: string }
    | { type: "TOGGLE_TODO"; payload: number }
    | { type: "DELETE_TODO"; payload: number }
    | { type: "SET_FILTER"; payload: "all" | "active" | "completed" };

// 3. Define the reducer function (implement this)
function todoListReducer(
    state: TodoListState, 
    action: TodoListAction
): TodoListState {
    switch (action.type) {
        case "ADD_TODO":
            // TODO: Add new todo to the list
            // Hint: Create a new todo object with id, text, and completed: false
            // Hint: Use spread operator to add to existing todos array
            return { ...state };

        case "TOGGLE_TODO":
            // TODO: Toggle the completed status of a todo
            // Hint: Find the todo by id
            // Hint: Toggle completed: !todo.completed
            // Hint: Use map to create new array with updated todo
            return { ...state };

        case "DELETE_TODO":
            // TODO: Remove a todo from the list
            // Hint: Filter out the todo with the given id
            return { ...state };

        case "SET_FILTER":
            // TODO: Update the filter
            return { ...state, filter: action.payload };

        default:
            return state;
    }
}

// 4. Create the component
export default function TodoListTask() {
    const [state, dispatch] = useReducer(todoListReducer, {
        todos: [],
        filter: "all"
    });

    return (
        <div style={{ padding: 20, fontFamily: "sans-serif", maxWidth: 500 }}>
            <h2>📝 Todo List Task</h2>
            
            {/* Add todo input */}
            <div style={{ display: "flex", gap: 10, marginBottom: 20 }}>
                <input
                    type="text"
                    placeholder="Add a new todo..."
                    style={{ flex: 1, padding: 10, border: "1px solid #ddd", borderRadius: "5px" }}
                    onKeyDown={(e) => {
                        if (e.key === "Enter" && e.currentTarget.value.trim()) {
                            dispatch({ 
                                type: "ADD_TODO", 
                                payload: e.currentTarget.value.trim() 
                            });
                            e.currentTarget.value = "";
                        }
                    }}
                />
                <button
                    onClick={() => {
                        const input = document.querySelector('input[type="text"]') as HTMLInputElement;
                        if (input && input.value.trim()) {
                            dispatch({ type: "ADD_TODO", payload: input.value.trim() });
                            input.value = "";
                        }
                    }}
                    style={{ padding: "10px 20px", backgroundColor: "#4CAF50", color: "white", border: "none", borderRadius: "5px", cursor: "pointer" }}
                >
                    Add
                </button>
            </div>

            {/* Filter buttons */}
            <div style={{ display: "flex", gap: 10, marginBottom: 20 }}>
                <button
                    onClick={() => dispatch({ type: "SET_FILTER", payload: "all" })}
                    style={{ padding: "5px 10px", border: "1px solid #ddd", backgroundColor: state.filter === "all" ? "#2196F3" : "white", borderRadius: "5px", cursor: "pointer" }}
                >
                    All
                </button>
                <button
                    onClick={() => dispatch({ type: "SET_FILTER", payload: "active" })}
                    style={{ padding: "5px 10px", border: "1px solid #ddd", backgroundColor: state.filter === "active" ? "#2196F3" : "white", borderRadius: "5px", cursor: "pointer" }}
                >
                    Active
                </button>
                <button
                    onClick={() => dispatch({ type: "SET_FILTER", payload: "completed" })}
                    style={{ padding: "5px 10px", border: "1px solid #ddd", backgroundColor: state.filter === "completed" ? "#2196F3" : "white", borderRadius: "5px", cursor: "pointer" }}
                >
                    Completed
                </button>
            </div>

            {/* Todo list */}
            <div>
                <h3>Todos ({state.todos.length}):</h3>
                {state.todos.length === 0 ? (
                    <p>No todos yet!</p>
                ) : (
                    <ul style={{ listStyle: "none", padding: 0 }}>
                        {state.todos.map(todo => (
                            <li
                                key={todo.id}
                                style={{ 
                                    padding: 10, 
                                    marginBottom: 5, 
                                    border: "1px solid #ddd", 
                                    borderRadius: "5px",
                                    display: "flex",
                                    alignItems: "center",
                                    gap: 10
                                }}
                            >
                                <input
                                    type="checkbox"
                                    checked={todo.completed}
                                    onChange={() => dispatch({ type: "TOGGLE_TODO", payload: todo.id })}
                                    style={{ cursor: "pointer" }}
                                />
                                <span style={{ flex: 1, textDecoration: todo.completed ? "line-through" : "none" }}>
                                    {todo.text}
                                </span>
                                <button
                                    onClick={() => dispatch({ type: "DELETE_TODO", payload: todo.id })}
                                    style={{ 
                                        background: "none", 
                                        border: "none", 
                                        color: "#f44336", 
                                        cursor: "pointer",
                                        fontSize: "18px"
                                    }}
                                >
                                    ✕
                                </button>
                            </li>
                        ))}
                    </ul>
                )}
            </div>
        </div>
    );
}
