import './App.css'
import type { PopulationData } from './assets/population'
import { populationData } from './assets/population'
import WorldPopulation from './worldPopulation'


function App(){

  // DEBUGGING: Step 1 - Understanding the data structure
  console.log("=== DESTRUCTURING DEBUGGING START ===")
  console.log("1. populationData is an array with", populationData.length, "items")
  console.log("2. First item in populationData:", populationData[0])

  // DEBUGGING: Step 2 - Understanding the map function
  const populationItems = populationData.map((entry: PopulationData)=>{
    // This is where destructuring happens with the spread operator {...entry}
    // The spread operator takes all properties from 'entry' and spreads them
    // as individual props to the WorldPopulation component

    console.log("\n--- Processing entry ---")
    console.log("3. 'entry' is a single object:", entry)
    console.log("4. 'entry' has these properties:", Object.keys(entry))
    console.log("5. Example - entry.country:", entry.country)
    console.log("6. Example - entry.pop2023:", entry.pop2023)

    // The spread operator {...entry} is equivalent to writing:
    // <WorldPopulation
    //   place={entry.place}
    //   pop1980={entry.pop1980}
    //   pop2000={entry.pop2000}
    //   ... and so on for all 20 properties
    // />

    console.log("7. Using spread operator: {...entry}")
    console.log("   This spreads all", Object.keys(entry).length, "properties as individual props")

    return (
      <WorldPopulation {...entry} />
    )
  })

  console.log("\n=== AFTER MAP ===")
  console.log("8. populationItems is now an array of", populationItems.length, "React elements")
  console.log("=== DESTRUCTURING DEBUGGING END ===\n")

  return (
    <main>
    {populationItems}
    </main>
  )
}

export default App
