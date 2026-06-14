import { useReducer } from "react";

// 1. Define the state shape
interface Color {
    id: number;
    name: string;
    hex: string;
}

interface FavoriteColorsState {
    favorites: Color[];
}

// 2. Define action types
type FavoriteColorsAction = 
    | { type: "ADD_COLOR"; payload: Color }
    | { type: "REMOVE_COLOR"; payload: number }
    | { type: "CLEAR_FAVORITES" };

// 3. Define the reducer function
function favoriteColorsReducer(
    state: FavoriteColorsState, 
    action: FavoriteColorsAction
): FavoriteColorsState {
    switch (action.type) {
        case "ADD_COLOR":
            return { 
                favorites: [...state.favorites, action.payload] 
            };
        case "REMOVE_COLOR":
            return { 
                favorites: state.favorites.filter(color => color.id !== action.payload) 
            };
        case "CLEAR_FAVORITES":
            return { 
                favorites: [] 
            };
        default:
            return state;
    }
}

// 4. Create the component
export default function FavoriteColors() {
    const [state, dispatch] = useReducer(favoriteColorsReducer, { favorites: [] });

    const availableColors: Color[] = [
        { id: 1, name: "Red", hex: "#FF0000" },
        { id: 2, name: "Blue", hex: "#0000FF" },
        { id: 3, name: "Green", hex: "#00FF00" },
        { id: 4, name: "Yellow", hex: "#FFFF00" },
        { id: 5, name: "Purple", hex: "#800080" },
    ];

    return (
        <div style={{ padding: 20, fontFamily: "sans-serif" }}>
            <h2>🎨 Favorite Colors</h2>
            
            {/* Available colors to add */}
            <div style={{ marginBottom: 20 }}>
                <h3>Available Colors:</h3>
                <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
                    {availableColors.map(color => (
                        <button
                            key={color.id}
                            onClick={() => dispatch({ type: "ADD_COLOR", payload: color })}
                            style={{ 
                                width: 50, 
                                height: 50, 
                                backgroundColor: color.hex,
                                border: "2px solid #ddd",
                                borderRadius: "50%",
                                cursor: "pointer"
                            }}
                            title={color.name}
                        />
                    ))}
                </div>
            </div>

            {/* Added favorites */}
            <div>
                <h3>Your Favorites ({state.favorites.length}):</h3>
                {state.favorites.length === 0 ? (
                    <p>No colors added yet!</p>
                ) : (
                    <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
                        {state.favorites.map(color => (
                            <div
                                key={color.id}
                                style={{ 
                                    padding: 10, 
                                    backgroundColor: color.hex,
                                    borderRadius: "5px",
                                    display: "flex",
                                    alignItems: "center",
                                    gap: 10
                                }}
                            >
                                <span>{color.name}</span>
                                <button
                                    onClick={() => dispatch({ type: "REMOVE_COLOR", payload: color.id })}
                                    style={{ 
                                        background: "none", 
                                        border: "none", 
                                        color: "#000",
                                        fontWeight: "bold",
                                        cursor: "pointer",
                                        fontSize: "18px"
                                    }}
                                >
                                    ✕
                                </button>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Clear button */}
            {state.favorites.length > 0 && (
                <button
                    onClick={() => dispatch({ type: "CLEAR_FAVORITES" })}
                    style={{ 
                        marginTop: 20, 
                        padding: "10px 20px", 
                        backgroundColor: "#f44336",
                        color: "white",
                        border: "none",
                        borderRadius: "5px",
                        cursor: "pointer"
                    }}
                >
                    Clear All
                </button>
            )}
        </div>
    );
}
