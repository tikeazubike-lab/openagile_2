# Debugging Props Flow in VS Code

This guide will help you debug how props flow between your React components (App.tsx, NewCart.tsx, etc.) using VS Code's built-in debugger.

## Setup Complete ✅

The following configurations have been added to your workspace:

### 1. `.vscode/launch.json`
- **Launch Chrome**: Automatically opens Chrome and connects to your dev server
- **Attach to Chrome**: Connects to an already running Chrome instance
- Both configurations skip `node_modules` and internal files

### 2. `.vscode/settings.json`
- Preserved your Copilot disabled setting ✅
- Preserved your Emmet settings ✅
- Added JavaScript debugging configurations
- Configured to skip node_modules during debugging

## How to Debug Props Flow

### Step 1: Start Your Dev Server
```bash
npm run dev
```

### Step 2: Set Breakpoints in Your Components

Open your component files and set breakpoints where you want to inspect props:

#### In `src/App.tsx`:
```tsx
const cartsDataElement = cartsData.carts.map((cart) => {
  // Set breakpoint here to see each cart object before passing it
  return (
    <NewCart {...cart} />
  )
})
```

#### In `src/components/NewCart.tsx`:
```tsx
function NewCart(props: Cart) {
  // Set breakpoint here to see props received
  console.log('NewCart props:', props) // Also helps with debugging
  
  return (
    <div className="cart">
      {/* Your cart JSX */}
    </div>
  )
}
```

### Step 3: Start Debugging

**Option A: Launch New Chrome Instance**
1. Press `F5` or go to **Run and Debug** panel
2. Select **"Launch Chrome against localhost"**
3. Chrome will open automatically at `http://localhost:5173`
4. The debugger will pause at your breakpoints

**Option B: Attach to Running Chrome**
1. Start Chrome with remote debugging:
   ```bash
   # Linux/Mac
   google-chrome --remote-debugging-port=9222

   # Windows
   chrome.exe --remote-debugging-port=9222
   ```
2. Navigate to `http://localhost:5173`
3. Press `F5` and select **"Attach to Chrome"**

## Debugging Features

### 1. Inspect Props at Breakpoints
When the debugger pauses at a breakpoint:
- Hover over variables to see their values
- Check the **Variables** panel in the Debug sidebar
- Look at the **Watch** panel to add expressions to monitor

### 2. Step Through Code
- **F5**: Continue to next breakpoint
- **F10**: Step over (execute current line, don't go into functions)
- **F11**: Step into (go into function calls)
- **Shift+F11**: Step out (exit current function)

### 3. Debug Console
Use the Debug Console to evaluate expressions:
```javascript
// Check props structure
props

// Check specific property
props.products

// Check array length
props.products.length

// Inspect nested object
props.products[0]
```

## Key Settings Explanation

### `skipFiles` Configuration
```json
"skipFiles": [
  "${workspaceFolder}/node_modules/**",
  "<node_internals>/**",
  "webpack:///**/node_modules/**",
  "webpack:///node_modules/**"
]
```
This ensures the debugger **only** steps through your source code files and skips:
- All files in `node_modules/`
- Node.js internal files
- Webpack-bundled node_modules

### `sourceMapPathOverrides`
```json
"sourceMapPathOverrides": {
  "webpack:///src/*": "${webRoot}/src/*",
  "webpack:///./src/*": "${webRoot}/src/*"
}
```
This maps webpack's internal paths back to your actual source files, allowing you to set breakpoints in your `.tsx` files and have them work correctly.

## Debugging Specific Scenarios

### Scenario 1: Debugging Props from App to NewCart

1. Open `src/App.tsx`
2. Set breakpoint on line with `cartsData.carts.map((cart) => {`
3. Start debugging
4. When paused, inspect the `cart` variable in the Variables panel
5. Press F10 to step through the mapping
6. The debugger will automatically pause in `NewCart.tsx` when the component renders

### Scenario 2: Debugging Nested Props (Products in Cart)

1. Open `src/components/NewCart.tsx`
2. Set breakpoint where you access `props.products`
3. Start debugging
4. Inspect `props.products` in the Variables panel
5. Expand the array to see individual product objects
6. Use the Debug Console to run: `props.products.map(p => p.title)`

### Scenario 3: Debugging Type Errors

If you see TypeScript errors about missing properties:
1. Set breakpoint where the error occurs
2. Inspect the actual object being passed
3. Compare with the expected type interface
4. Use the Debug Console to check: `Object.keys(props)`

## Tips for Effective Debugging

1. **Use Conditional Breakpoints**: Right-click a breakpoint and add a condition
   ```javascript
   cart.id === 1  // Only break for cart with id 1
   ```

2. **Log Points**: Right-click a breakpoint and select "Add Log Point"
   ```javascript
   Cart {cart.id} has {cart.products.length} products
   ```

3. **Watch Expressions**: Add variables to the Watch panel to monitor them continuously
   - `props.id`
   - `props.products.length`
   - `props.total`

4. **Call Stack**: Use the Call Stack panel to see the component hierarchy
   - Shows which component rendered which
   - Helps trace prop flow up the tree

## Common Issues and Solutions

### Issue: Breakpoints not hitting
- **Solution**: Make sure source maps are enabled in `vite.config.js`
- **Solution**: Try refreshing the browser while debugging
- **Solution**: Check that your breakpoints are in the `.tsx` source files, not in the debugger's mapped files

### Issue: Debugger steps into node_modules
- **Solution**: Verify `skipFiles` is correctly configured in both `launch.json` and `settings.json`
- **Solution**: Restart VS Code after changing settings

### Issue: Props showing as undefined
- **Solution**: Check the component's prop interface matches the data structure
- **Solution**: Use `console.log(props)` at the top of your component
- **Solution**: Inspect the parent component to verify what's being passed

## Example: Debugging Your Current Setup

### Debug Flow for cartsData:

1. **In `src/App.tsx`**:
   ```tsx
   const cartsDataElement = cartsData.carts.map((cart) => {  // ← Breakpoint here
     return (
       <NewCart {...cart} />
     )
   })
   ```
   - Inspect `cart` object
   - Check: `cart.id`, `cart.products`, `cart.total`

2. **In `src/components/NewCart.tsx`**:
   ```tsx
   function NewCart(props: Cart) {  // ← Breakpoint here
     return (
       <div className="cart">
         {/* Inspect props here */}
       </div>
     )
   }
   ```
   - Verify all props match the `Cart` interface
   - Check: `props.id`, `props.products`, `props.total`, etc.

## Keyboard Shortcuts

- **F5**: Start/Continue debugging
- **F9**: Toggle breakpoint
- **F10**: Step over
- **F11**: Step into
- **Shift+F11**: Step out
- **Shift+F5**: Stop debugging

## Additional Resources

- [VS Code JavaScript Debugging](https://code.visualstudio.com/docs/nodejs/nodejs-debugging)
- [React Debugging Guide](https://react.dev/learn/react-developer-tools)
- [TypeScript Debugging](https://code.visualstudio.com/docs/typescript/typescript-debugging)
