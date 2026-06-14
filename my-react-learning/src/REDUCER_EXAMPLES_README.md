# UseReducer Examples - Step-by-Step Learning Guide

This directory contains 4 examples to help you understand how to use `useReducer` in React.

## 📚 Examples Overview

### 1. [`CounterSimple.tsx`](src/CounterSimple.tsx) - **WORKED DEMO 1**
A simple counter that increments, decrements, and resets.

**What you'll learn:**
- Basic state shape with a single number
- Simple action types: INCREMENT, DECREMENT, RESET
- How to return new state from the reducer

**Try it:** Run `npm run dev` and open `CounterSimple.tsx`

---

### 2. [`ToggleExample.tsx`](src/ToggleExample.tsx) - **WORKED DEMO 2**
A toggle switch that turns on/off with visual feedback.

**What you'll learn:**
- Boolean state (`isOn`)
- Multiple action types: TOGGLE, TURN_ON, TURN_OFF
- Using state in JSX for conditional rendering

**Try it:** Run `npm run dev` and open `ToggleExample.tsx`

---

### 3. [`FavoriteColors.tsx`](src/FavoriteColors.tsx) - **WORKED DEMO 3**
A color picker that lets you add and remove favorite colors.

**What you'll learn:**
- Array state with objects
- Adding items to an array
- Filtering items from an array
- Conditional rendering based on array length

**Try it:** Run `npm run dev` and open `FavoriteColors.tsx`

---

### 4. [`TodoListTask.tsx`](src/TodoListTask.tsx) - **PRACTICE TASK**
A todo list app with filtering - **IMPLEMENT THIS YOURSELF!**

**What you need to do:**
1. Open [`TodoListTask.tsx`](src/TodoListTask.tsx)
2. Look at the `TODO` comments in the reducer
3. Implement the logic for each case:
   - `ADD_TODO`: Add a new todo to the array
   - `TOGGLE_TODO`: Toggle completed status
   - `DELETE_TODO`: Remove a todo from the array
   - `SET_FILTER`: Update the filter state

**Hints:**
- Use spread operator `[...state.todos]` to create new arrays
- Use `map()` to transform arrays
- Use `filter()` to remove items
- Use `!state.isOn` to toggle boolean values

**Try it:** Run `npm run dev` and open `TodoListTask.tsx`

---

## 🎯 How to Use These Examples

### Step 1: Study the Pattern
Each example follows the same 4-step pattern:

```typescript
// 1. Define the state shape
interface State {
    // ... properties
}

// 2. Define action types
type Action = 
    | { type: "ACTION_1" }
    | { type: "ACTION_2" };

// 3. Define the reducer function
function reducer(state: State, action: Action): State {
    switch (action.type) {
        case "ACTION_1":
            return { ...state }; // Return new state
        case "ACTION_2":
            return { ...state }; // Return new state
        default:
            return state;
    }
}

// 4. Create the component
function Component() {
    const [state, dispatch] = useReducer(reducer, initialState);
    // ... render JSX
}
```

### Step 2: Run the Examples
```bash
npm run dev
```

Then open each file in your browser:
- `http://localhost:5173/src/CounterSimple.tsx`
- `http://localhost:5173/src/ToggleExample.tsx`
- `http://localhost:5173/src/FavoriteColors.tsx`
- `http://localhost:5173/src/TodoListTask.tsx`

### Step 3: Practice the Task
Try implementing [`TodoListTask.tsx`](src/TodoListTask.tsx) yourself before looking at solutions!

---

## 📖 Key Concepts

### 1. State Shape
The state defines what your component needs to know:
```typescript
interface State {
    count: number;  // Single value
    isOn: boolean;  // Boolean
    todos: Todo[];  // Array of objects
}
```

### 2. Action Types
Actions tell the reducer what to do:
```typescript
type Action = 
    | { type: "INCREMENT" }
    | { type: "DECREMENT" }
    | { type: "RESET" };
```

### 3. The Reducer
The reducer is a pure function that returns new state:
```typescript
function reducer(state, action) {
    switch (action.type) {
        case "INCREMENT":
            return { count: state.count + 1 };
        default:
            return state;
    }
}
```

### 4. Dispatch
Dispatch sends actions to the reducer:
```typescript
dispatch({ type: "INCREMENT" });
```

### 5. Immutability
Always return new state objects:
```typescript
// ❌ Bad: Mutates state
state.count++;

// ✅ Good: Creates new state
return { count: state.count + 1 };
```

---

## 🚀 Common Patterns

### Adding to an Array
```typescript
case "ADD_ITEM":
    return { 
        items: [...state.items, newItem] 
    };
```

### Removing from an Array
```typescript
case "REMOVE_ITEM":
    return { 
        items: state.items.filter(item => item.id !== id) 
    };
```

### Updating an Item in an Array
```typescript
case "UPDATE_ITEM":
    return { 
        items: state.items.map(item =>
            item.id === id 
                ? { ...item, ...updates } 
                : item
        ) 
    };
```

### Toggling a Boolean
```typescript
case "TOGGLE":
    return { 
        isOn: !state.isOn 
    };
```

---

## 🎓 Learning Path

1. **Start with CounterSimple.tsx** - Understand the basic pattern
2. **Try ToggleExample.tsx** - Practice with boolean state
3. **Explore FavoriteColors.tsx** - Learn array operations
4. **Complete TodoListTask.tsx** - Apply what you've learned

---

## 💡 Tips

- Read the comments in each file - they explain the logic
- Try changing the code and see what happens
- Use the browser console to see dispatch calls
- Start simple, then build complexity

---

## 🐛 Common Mistakes to Avoid

1. **Mutating state directly**
   ```typescript
   // ❌ Don't do this
   state.items.push(newItem);
   return state;
   
   // ✅ Do this instead
   return { items: [...state.items, newItem] };
   ```

2. **Forgetting to return state in default case**
   ```typescript
   default:
       return state; // Always return state!
   ```

3. **Not using spread operator**
   ```typescript
   // ❌ Creates new array reference
   return { items: state.items };
   
   // ✅ Creates new array with new items
   return { items: [...state.items] };
   ```

---

Happy learning! 🎉
