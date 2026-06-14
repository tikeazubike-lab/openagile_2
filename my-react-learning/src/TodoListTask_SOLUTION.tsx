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

// 3. Define the reducer function (IMPLEMENTED)
function todoListReducer(
    state: TodoListState, 
    action: TodoListAction
): TodoListState {
    switch (action.type) {
        case "ADD_TODO": {
            // Create new todo with unique id
            const newTodo: Todo = {
                id: Date.now(), // Generate unique ID
                text: action.payload,
                completed: false
            };
            return { 
                todos: [...state.todos, newTodo],
                filter: state.filter 
            };
        }
        
        case "TOGGLE_TODO": {
            // Find the todo and toggle its completed status
            return { 
                todos: state.todos.map(todo =>
                    todo.id === action.payload
                        ? { ...todo, completed: !todo.completed }
                        : todo
                ),
                filter: state.filter 
            };
        }
        
        case "DELETE_TODO": {
            // Remove the todo with the given id
            return { 
                todos: state.todos.filter(todo => todo.id !== action.payload),
                filter: state.filter 
            };
        }
        
        case "SET_FILTER": {
            // Update the filter
            return { 
                todos: state.todos,
                filter: action.payload 
            };
        }
        
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

    // Filter todos based on current filter
    const filteredTodos = state.todos.filter(todo => {
        if (state.filter === "active") return !todo.completed;
        if (state.filter === "completed") return todo.completed;
        return true;
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
                        {filteredTodos.map(todo => (
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
