// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// PROMISES LEARNING GUIDE - Educational Comments
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// 
// HOW TO DEBUG THIS CODE:
// 1. Set breakpoints on lines marked with 🔍 BREAKPOINT HERE
// 2. Press F5 (Debug) and select "Launch Chrome against localhost"
// 3. Step through with F10 (Step Over) or F11 (Step Into)
// 4. Watch the "Debug Console" and "Variables" panel
// 
// The VSCode configuration will skip complex library code (node_modules, Vite internals)
// so you only see YOUR code, not the dark waters of fetch() implementation!
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

function fetchPromise(){
    // 🔍 BREAKPOINT HERE: Start of function execution
    
    // CONCEPT: fetch() returns a Promise object immediately
    // A Promise is a placeholder for a value that will be available in the future
    // It can be in one of 3 states: pending, fulfilled, or rejected
    const fetchPromise = fetch("https://mdn.github.io/learning-area/javascript/apis/fetching-data/can-store/products.json")
    
    // 🔍 BREAKPOINT HERE: Check fetchPromise in Variables panel
    // You'll see it's a Promise object with [[PromiseState]]: "pending"
    
    // CONCEPT: .then() registers a callback function that runs when the Promise fulfills
    // The .then() method returns a NEW Promise, allowing chaining
    fetchPromise
        .then(response => {
            // 🔍 BREAKPOINT HERE: This runs when fetch() completes successfully
            // 'response' is the Response object from the fetch API
            
            // CONCEPT: response.json() also returns a Promise!
            // It parses the response body as JSON asynchronously

            if(!response.ok) {
                throw new Error(`HTTP Status Error: ${response.status}`)
            }

            const jsonPromise = response.json()
            
            // 🔍 BREAKPOINT HERE: Check jsonPromise in Variables panel
            // You'll see it's another Promise in "pending" state
            
            // Return the Promise to the next .then() in the chain
            return jsonPromise
        })
        .then(data => {
            // 🔍 BREAKPOINT HERE: This runs when response.json() completes
            // 'data' now contains the parsed JavaScript object/array
            
            // CONCEPT: Access nested data using dot notation or bracket notation
            // data[0] gets the first item in the array
            // .name gets the 'name' property of that item
            const productName = data[0].name
            
            // 🔍 BREAKPOINT HERE: Check productName in Variables panel
            // You'll see the actual product name string
            
            console.log(productName)
        })
        .catch(error => {
            // CONCEPT: .catch() handles any errors in the promise chain
            // If ANY .then() fails, execution jumps here
            console.error("Something went wrong:", error)
        })
}

export default fetchPromise