import { useReducer } from "react";

// 1. Define the state shape
interface ToggleState {
    isOn: boolean;
}

// 2. Define action types
type ToggleAction = 
    | { type: "TOGGLE" }
    | { type: "TURN_ON" }
    | { type: "TURN_OFF" };

// 3. Define the reducer function
function toggleReducer(state: ToggleState, action: ToggleAction): ToggleState {
    switch (action.type) {
        case "TOGGLE":
            return { isOn: !state.isOn };
        case "TURN_ON":
            return { isOn: true };
        case "TURN_OFF":
            return { isOn: false };
        default:
            return state;
    }
}

// 4. Create the component
export default function ToggleExample() {
    const [state, dispatch] = useReducer(toggleReducer, { isOn: false });

    return (
        <div style={{ padding: 20, fontFamily: "sans-serif" }}>
            <h2>Toggle Switch</h2>
            <p>Is On: {state.isOn ? "Yes" : "No"}</p>
            <button 
                onClick={() => dispatch({ type: "TOGGLE" })}
                style={{ 
                    backgroundColor: state.isOn ? "#4CAF50" : "#f44336",
                    color: "white",
                    border: "none",
                    padding: "10px 20px",
                    borderRadius: "5px",
                    cursor: "pointer"
                }}
            >
                {state.isOn ? "Turn Off" : "Turn On"}
            </button>
        </div>
    );
}
