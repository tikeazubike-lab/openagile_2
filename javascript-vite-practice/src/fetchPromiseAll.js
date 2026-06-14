// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// PROMISE.ALL LEARNING GUIDE - Educational Comments
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
//
// BREAKPOINT LOCATIONS (🔍):
// 1. Line 18: After all fetch() calls - See 3 pending promises
// 2. Line 24: Inside .then() - See all responses array
// 3. Line 27: Inside forEach - See individual response objects
// 4. Line 32: Inside .catch() - See error handling (if any fetch fails)
//
// KEY CONCEPT: Promise.all() waits for ALL promises to resolve or ANY to reject
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

function myFetchPromiseAll(){
  // 🔍 BREAKPOINT 1 HERE (after line 18): Check all 3 fetchPromise variables
  // You'll see they're all Promise objects in "pending" state
  
  // CONCEPT: Multiple fetch() calls start simultaneously (in parallel)
  // Each returns a Promise immediately, but the actual network request happens async
  const fetchPromise1 = fetch(
    "https://mdn.github.io/learning-area/javascript/apis/fetching-data/can-store/products.json",
  );
  
  const fetchPromise2 = fetch(
    "https://mdn.github.io/learning-area/javascript/apis/fetching-data/can-store/not-found",
  );
  
  const fetchPromise3 = fetch(
    "https://mdn.github.io/learning-area/javascript/oojs/json/superheroes.json",
  );

  // 🔍 BREAKPOINT 2 HERE (line 24): Watch Promise.all() work
  // CONCEPT: Promise.all() takes an array of promises and returns a single promise
  // - If ALL promises resolve: returns array of results (in same order as input)
  // - If ANY promise rejects: immediately rejects with that error (fail-fast)
  
  Promise.all([fetchPromise1, fetchPromise2, fetchPromise3])
    .then((responses) => {
      // 🔍 BREAKPOINT 3 HERE (line 27): Check 'responses' array
      // You'll see an array of 3 Response objects
      // responses[0] = Response from fetchPromise1
      // responses[1] = Response from fetchPromise2 (might be 404!)
      // responses[2] = Response from fetchPromise3
      
      // CONCEPT: forEach() iterates through each response in the array
      // This runs synchronously once all promises are resolved
      responses.forEach(response => {
        // 🔍 BREAKPOINT 4 HERE (line 33): Check individual response object
        // See properties: response.url, response.status, response.ok
        
        console.log(`${response.url}: ${response.status}`);
        
        // CONCEPT: response.status tells you the HTTP status code
        // 200 = OK, 404 = Not Found, 500 = Server Error, etc.
        // response.ok is true for status 200-299, false otherwise
      })
    
    })
    .catch((error) => {
      // 🔍 BREAKPOINT 5 HERE (line 42): Error handling
      // This runs if ANY of the fetch() calls completely fails (network error, timeout)
      // Note: 404 errors do NOT trigger .catch() - they're still valid responses!
      
      console.error(`Failed to fetch: ${error}`);
    });
}

export default myFetchPromiseAll