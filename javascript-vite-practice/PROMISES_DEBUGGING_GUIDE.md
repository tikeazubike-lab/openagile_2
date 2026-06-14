# 🎯 Promises Debugging Guide

This guide will help you understand how promises work without getting lost in complex library code.

## 📋 Setup Instructions

### 1. Start the Development Server
```bash
npm run dev
```

### 2. Open VSCode Debugger
- Press `F5` or click the Debug icon (🐛) in the left sidebar
- Select **"Launch Chrome against localhost"**
- The browser will open automatically at `http://localhost:5173`

### 3. Set Breakpoints
In [`src/promises.js`](src/promises.js), click in the gutter (left margin) next to lines marked with:
- 🔍 Line 18: `const fetchPromise = fetch(...)`
- 🔍 Line 28: `const jsonPromise = response.json()`
- 🔍 Line 38: `const productName = data[0].name`

### 4. Debug Controls
- **F9**: Toggle breakpoint
- **F5**: Continue/Start debugging
- **F10**: Step over (execute current line, don't go into functions)
- **F11**: Step into (go into function calls)
- **Shift+F11**: Step out (exit current function)
- **Shift+F5**: Stop debugging

## 🎓 What You'll Learn

### Promise States
Watch the Variables panel to see promises change states:

1. **Pending** ⏳
   - Initial state when promise is created
   - Check: `fetchPromise` after line 18

2. **Fulfilled** ✅
   - When the async operation completes successfully
   - Check: `response` in first `.then()` callback

3. **Rejected** ❌
   - When something goes wrong
   - Triggers the `.catch()` handler

### Promise Chaining
```
fetch() → .then() → .then() → .catch()
   ↓         ↓         ↓
Promise   Promise   Promise
```

Each `.then()` returns a **new** promise, allowing you to chain them.

### Key Concepts to Observe

#### 1. Asynchronous Execution
```javascript
const fetchPromise = fetch(url) // Returns immediately!
console.log("This runs BEFORE fetch completes")
```

#### 2. Callback Execution Order
- Code inside `.then()` runs **after** the promise resolves
- Multiple `.then()` callbacks run in sequence

#### 3. Data Flow
```
Response object → .json() → Parsed data → Extract name → Log to console
```

## 🔍 Debugging Tips

### Watch These Variables
Add these to your Watch panel (right side of debugger):
- `fetchPromise` - See promise state changes
- `response` - Inspect the Response object
- `data` - See the parsed JSON data
- `productName` - Final extracted value

### Use the Debug Console
Type these expressions while paused:
```javascript
fetchPromise // Check promise state
response.status // HTTP status code
response.headers // Response headers
data.length // Number of items in array
data[0] // First item in array
```

### Common Questions

**Q: Why does the code skip to the end?**
A: Because it's asynchronous! The function returns immediately, but `.then()` callbacks run later when promises resolve.

**Q: How do I see what's in the promise?**
A: Pause execution at a breakpoint and check the Variables panel. Look for `[[PromiseResult]]` and `[[PromiseState]]`.

**Q: What if the request fails?**
A: The `.catch()` handler will execute. Try changing the URL to something invalid to see this in action.

## 🚀 Advanced Debugging

### Conditional Breakpoints
Right-click a breakpoint → "Edit Breakpoint" → Add condition:
```javascript
data && data.length > 0
```

### Log Points
Right-click a breakpoint → "Add Log Point" → Add message:
```
Promise resolved with {data.length} items
```

### Exception Breakpoints
In the Breakpoints panel, click the ⚙️ icon → Enable "Uncaught Exceptions"

## 📚 What VSCode Configuration Does

The [`.vscode/launch.json`](.vscode/launch.json) and [`.vscode/settings.json`](.vscode/settings.json) files configure VSCode to:

1. **Skip complex library code** - You won't step into `node_modules`, Vite internals, or browser APIs
2. **Focus on your code** - Only your source files appear in the call stack
3. **Enable source maps** - Debug original source, not compiled code
4. **Show inline values** - See variable values directly in the editor

This means you'll see:
```
✅ src/promises.js (your code)
❌ node_modules/vite/dist/client/client.mjs (skipped)
❌ <internal> browser internals (skipped)
```

## 🎯 Practice Exercises

1. **Add error handling**: Change the URL to be invalid and watch `.catch()` execute
2. **Extract more data**: Log `data[0].price` or iterate through all items
3. **Add another `.then()`**: Chain another operation after the final `.then()`
4. **Use `async/await`**: Rewrite the function using async/await syntax

## 📖 Additional Resources

- [MDN: Using Promises](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Using_promises)
- [MDN: Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
- [JavaScript.info: Promises](https://javascript.info/promise-basics)

---

**Happy Debugging! 🐛✨**
