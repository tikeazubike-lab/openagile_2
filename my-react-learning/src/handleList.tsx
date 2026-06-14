import { useState } from "react"

export default function HandleList(){
    
    
const [myFavoriteThings, setMyFavoriteThings] = useState<string[]>([])
  const allFavoriteThings: string[] = ["💦🌹", "😺", "💡🫖", "🔥🧤", "🟤🎁", 
  "🐴", "🍎🥧", "🚪🔔", "🛷🔔", "🥩🍝"]
  const thingsElements = myFavoriteThings.map(thing => <p key={thing}>{thing}</p>)

  function addFavoriteThing() {
    // We'll work on this next, nothing to do here yet.
    console.log(myFavoriteThings.length)
    setMyFavoriteThings(prev => [...prev, allFavoriteThings[prev.length]])
  }
  
  return (
    <main>
      <button onClick={addFavoriteThing}>Add item</button>
      <section aria-live="polite">
        {thingsElements}
      </section>
    </main>
  )

}