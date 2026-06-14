import { useReducer } from 'react'

const initialState = 0

// const reducer = (state, action)=>{
//   // Return new state
// }
// export default function CounterWithReducer(){
//  const[state, dispatch] =  useReducer(reducer, initialState);
//   return (
//     <div>
//       <button>Increment</button>
//       <button>Decrement</button>
//       <button>Reset</button>
//     </div>
//   )
// }
// const [state, dispatch] = useReducer(reducer, initialState)

interface Action {
    type: string,
    payload: object
}

function reducer(state: number, action: Action){
    switch(action.type){
        case "INCREMENT":
            return state + 1
        case "DECREMENT":
            return state - 1
        case "RESET":
            return 0
        default:
            return state
    }
}


export default function SimpleCounterWithReducer(){
    const [count, dispatch] = useReducer(reducer, initialState)
    return (
        <div>
            <p>Count: {count}</p>
            <button onClick={() => dispatch('INCREMENT')}>+</button>
            <button onClick={() => dispatch('DECREMENT')}>-</button>
            <button onClick={() => dispatch('RESET')}>Reset</button>
        </div>
    )
}