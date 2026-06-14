import {useReducer} from "react";

const initialState = false

type Action = "ON" | "OFF" | "TOGGLE"

const reducer = (state = initialState, action: Action) => {
    switch (action) {
        case "TOGGLE":
            return !state
        case "ON":
            return true
        case "OFF":
            return false
        default:
            return state
    }
}

export default function LightSwitch(){
const [isOn, dispatch] = useReducer(reducer, initialState)
    return (
        <div>
            <p>Light is: {isOn ? 'ON 💡' : 'OFF 🌑'}</p>
            <button onClick={() => dispatch('TOGGLE')}>Toggle Light</button>
            <button onClick={() => dispatch('ON')}>Turn On</button>
            <button onClick={() => dispatch('OFF')}>Turn Off</button>
        </div>
    )
}