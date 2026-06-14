import { useReducer } from 'react'

// Initial state: empty cart
const initialState = {
  items: [],
  total: 0
}

// Reducer handles all cart operations
function cartReducer(state, action) {
  switch (action.type) {
    case 'ADD_ITEM': {
      const newItem = {
        id: Date.now(),
        name: action.payload.name,
        price: action.payload.price
      }
      return {
        ...state,
        items: [...state.items, newItem],
        total: state.total + action.payload.price
      }
    }
    
    case 'REMOVE_ITEM': {
      const itemToRemove = state.items.find(item => item.id === action.payload)
      return {
        ...state,
        items: state.items.filter(item => item.id !== action.payload),
        total: state.total - (itemToRemove?.price || 0)
      }
    }
    
    case 'CLEAR_CART':
      return initialState
    
    default:
      return state
  }
}

export default function ShoppingCart() {
  const [cart, dispatch] = useReducer(cartReducer, initialState)
  
  return (
    <div>
      <h2>Shopping Cart</h2>
      <p>Total: ${cart.total.toFixed(2)}</p>
      
      {/* Add items */}
      <button onClick={() => dispatch({ 
        type: 'ADD_ITEM', 
        payload: { name: 'Apple', price: 1.99 } 
      })}>
        Add Apple ($1.99)
      </button>
      
      <button onClick={() => dispatch({ 
        type: 'ADD_ITEM', 
        payload: { name: 'Bread', price: 2.50 } 
      })}>
        Add Bread ($2.50)
      </button>
      
      {/* Remove items */}
      {cart.items.map(item => (
        <div key={item.id}>
          <span>{item.name} - ${item.price.toFixed(2)}</span>
          <button onClick={() => dispatch({ 
            type: 'REMOVE_ITEM', 
            payload: item.id 
          })}>
            Remove
          </button>
        </div>
      ))}
      
      <button onClick={() => dispatch({ type: 'CLEAR_CART' })}>
        Clear Cart
      </button>
    </div>
  )
}
