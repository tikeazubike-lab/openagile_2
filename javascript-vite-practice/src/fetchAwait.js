async function fetchAsyncAwait(){
  try {
    const response = await fetch("https://mdn.github.io/learning-area/javascript/apis/fetching-data/can-store/products.json",)

    if(!response.ok){
      throw new Error(`Error status: ${response.status}`)
    }
  } catch (error) {
    console.error(`The established error: ${error}`)    
  }
}

fetchAsyncAwait()