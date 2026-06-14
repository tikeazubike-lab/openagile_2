import { useReducer } from "react";

// 1. Define the state shape
interface CounterState {
    count: number;
}

// 2. Define action types
type CounterAction = 
    | { type: "INCREMENT" }
    | { type: "DECREMENT" }
    | { type: "RESET" };



// 3. Define the reducer function
function counterReducer(state: CounterState, action: CounterAction): CounterState {
    switch (action.type) {
        case "INCREMENT":
            return { count: state.count + 1 };
        case "DECREMENT":
            return { count: state.count - 1 };
        case "RESET":
            return { count: 0 };
        default:
            return state;
    }
}

// 4. Create the component
export default function CounterSimple() {
    const [state, dispatch] = useReducer(counterReducer, { count: 0 });

    return (
        <div style={{ padding: 20, fontFamily: "sans-serif" }}>
            <h2>Simple Counter</h2>
            <p>Count: {state.count}</p>
            <button onClick={() => dispatch({ type: "INCREMENT" })}>+1</button>
            <button onClick={() => dispatch({ type: "DECREMENT" })}>-1</button>
            <button onClick={() => dispatch({ type: "RESET" })}>Reset</button>
        </div>
    );
}
