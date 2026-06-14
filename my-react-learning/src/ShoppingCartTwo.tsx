import { useReducer } from "react";

interface CartItem {
    id: number;
    name: string;
    price: number;
    qty: number;
}

interface CartState {
    items: CartItem[];
    total: number;
}

interface CartAction {
    type: "ADD_ITEM" | "REMOVE_ITEM" | "CLEAR_CART";
    payload?: {
        id: number;
        name: string;
        price: number;
    };
}

const initialState: CartState = { items: [], total: 0 };

function cartReducer(state: CartState, action: CartAction): CartState {
    switch (action.type) {
        case "ADD_ITEM": {
            const existing = state.items.find((i: CartItem) => i.id === action.payload!.id);
            const items = existing
                ? state.items.map((i: CartItem) =>
                    i.id === action.payload!.id
                        ? { ...i, qty: i.qty + 1 }
                        : i
                )
                : [...state.items, { ...action.payload!, qty: 1 }];
            return {
                items,
                total: state.total + action.payload!.price,
            };
        }
        case "REMOVE_ITEM": {
            const item = state.items.find((i: CartItem) => i.id === action.payload!.id);
            if (!item) {
                return state;
            }
            return {
                items: state.items.filter((i: CartItem) => i.id !== action.payload!.id),
                total: state.total - item.price * item.qty,
            };
        }
        case "CLEAR_CART":
            return initialState;
        default:
            return state;
    }
}

export default function Cart() {
    const [cart, dispatch] = useReducer(cartReducer, initialState);

    const products: CartItem[] = [
        { id: 1, name: "Keyboard", price: 79, qty: 0 },
        { id: 2, name: "Mouse", price: 49, qty: 0 },
    ];

    return (
        <div style={{ fontFamily: "sans-serif", padding: 20 }}>
            <h2>🛒 Cart (${cart.total})</h2>
            {products.map((p: CartItem) => (
                <button 
                key={p.id} 
                onClick={() => dispatch({ type: "ADD_ITEM", payload: p })}>
                    Add {p.name} (${p.price})
                </button>
            ))}
            <ul>
                {cart.items.map((i: CartItem) => (
                    <li key={i.id}>
                        {i.name} x{i.qty} — ${i.price * i.qty}
                        <button onClick={() => dispatch({ type: "REMOVE_ITEM", payload: i })}>
                            ✕
                        </button>
                    </li>
                ))}
            </ul>
            {cart.items.length > 0 && (
                <button onClick={() => dispatch({ type: "CLEAR_CART" })}>Clear Cart</button>
            )}
        </div>
    );
}