// ============================================
// DEMO: Understanding await vs .then()
// ============================================

console.log("=== DEMO 1: Using .then() (No await) ===\n");

// Approach 1: Using .then() - The traditional way
function fetchProductsWithThen() {
  return fetch("https://mdn.github.io/learning-area/javascript/apis/fetching-data/can-store/products.json")
    .then((response) => {
      console.log("1. Response received:", response.ok);
      if (!response.ok) {
        throw new Error(`HTTP error: ${response.status}`);
      }
      // response.json() returns a PROMISE
      const jsonPromise = response.json();
      console.log("2. jsonPromise type:", jsonPromise instanceof Promise);
      
      // We need .then() to get the data from this promise
      return jsonPromise.then((data) => {
        console.log("3. Data received inside nested .then():", data[0].name);
        return data;
      });
    });
}

fetchProductsWithThen()
  .then((data) => {
    console.log("4. Final data in outer .then():", data[0].name);
    console.log("\n" + "=".repeat(50) + "\n");
    
    // Now let's see the await version
    demo2();
  })
  .catch((error) => {
    console.error("Error:", error);
  });

// ============================================
function demo2() {
  console.log("=== DEMO 2: Using await (Cleaner) ===\n");

  async function fetchProductsWithAwait() {
    const response = await fetch("https://mdn.github.io/learning-area/javascript/apis/fetching-data/can-store/products.json");
    console.log("1. Response received:", response.ok);
    
    if (!response.ok) {
      throw new Error(`HTTP error: ${response.status}`);
    }
    
    // response.json() STILL returns a promise
    const jsonPromise = response.json();
    console.log("2. jsonPromise type:", jsonPromise instanceof Promise);
    
    // BUT await automatically unwraps it for us!
    const data = await jsonPromise;
    console.log("3. Data received after await:", data[0].name);
    
    return data;
  }

  fetchProductsWithAwait()
    .then((data) => {
      console.log("4. Final data in .then():", data[0].name);
      console.log("\n" + "=".repeat(50) + "\n");
      
      demo3();
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

// ============================================
function demo3() {
  console.log("=== DEMO 3: Side-by-side comparison ===\n");

  // VERSION A: With .then() (nested callbacks)
  console.log("VERSION A - Using .then():");
  function versionA() {
    return fetch("https://mdn.github.io/learning-area/javascript/apis/fetching-data/can-store/products.json")
      .then((response) => {
        return response.json().then((data) => {
          return data[0].name;  // Nested .then() - harder to read
        });
      });
  }

  // VERSION B: With await (flat code)
  console.log("VERSION B - Using await:");
  async function versionB() {
    const response = await fetch("https://mdn.github.io/learning-area/javascript/apis/fetching-data/can-store/products.json");
    const data = await response.json();  // Flat code - easier to read
    return data[0].name;
  }

  // Test both
  versionA().then((nameA) => {
    console.log("Result from versionA:", nameA);
    return versionB();
  }).then((nameB) => {
    console.log("Result from versionB:", nameB);
    console.log("\n" + "=".repeat(50) + "\n");
    
    demo4();
  });
}

// ============================================
function demo4() {
  console.log("=== DEMO 4: What await actually does ===\n");

  console.log("Think of await as a 'promise unwrapper':\n");
  
  console.log("When you write:");
  console.log("  const data = await response.json();\n");
  
  console.log("It's like JavaScript does this internally:");
  console.log("  const data = await new Promise((resolve) => {");
  console.log("    response.json().then(resolve);");
  console.log("  });\n");
  
  console.log("So await:");
  console.log("  1. Takes the promise from response.json()");
  console.log("  2. Waits for it to resolve");
  console.log("  3. Extracts the resolved value");
  console.log("  4. Assigns it to 'data'\n");
  
  console.log("WITHOUT await, you would need:");
  console.log("  response.json().then((data) => {");
  console.log("    // Now you can use data");
  console.log("  });\n");
  
  console.log("WITH await, you can just:");
  console.log("  const data = await response.json();");
  console.log("  // Now you can use data directly\n");
  
  console.log("\n" + "=".repeat(50) + "\n");
  
  demo5();
}

// ============================================
function demo5() {
  console.log("=== DEMO 5: The key insight ===\n");

  console.log("IMPORTANT: response.json() ALWAYS returns a promise!\n");
  
  async function showPromiseTypes() {
    const response = await fetch("https://mdn.github.io/learning-area/javascript/apis/fetching-data/can-store/products.json");
    
    const jsonPromise = response.json();
    console.log("Type of response.json():", jsonPromise instanceof Promise);
    console.log("This IS a promise, but we're about to await it...\n");
    
    const data = await jsonPromise;
    console.log("Type after await:", data instanceof Promise);
    console.log("After await, it's just data (not a promise)!\n");
    console.log("First product name:", data[0].name);
    
    return data;
  }

  showPromiseTypes()
    .then((data) => {
      console.log("\n" + "=".repeat(50));
      console.log("=== SUMMARY ===");
      console.log("=".repeat(50) + "\n");
      
      console.log("✓ response.json() returns a Promise");
      console.log("✓ await automatically unwraps that Promise");
      console.log("✓ After await, you get the actual data");
      console.log("✓ No need for .then() inside async functions");
      console.log("✓ .then() is only needed when calling the async function\n");
      
      console.log("That's why your code works:");
      console.log("  const data = await response.json();  // await unwraps it");
      console.log("  return data;                         // return the data");
      console.log("\nInstead of:");
      console.log("  response.json().then((data) => {     // nested .then()");
      console.log("    return data;");
      console.log("  });");
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}
