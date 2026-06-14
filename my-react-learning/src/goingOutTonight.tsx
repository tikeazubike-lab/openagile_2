import { useState } from "react"

export default function GoingOutTonight(){
    const [isGoingOut, setIsGoingOut] = useState(true)
    
  function setMyState(){
    // return isGoingOut ? setIsGoingOut(false): setIsGoingOut(true)
    setIsGoingOut(prev => !prev)
  }

    return (
        <>
        <h1 className="title">Do I feel like going out tonight? </h1>
        <button onClick={setMyState}>{isGoingOut == true ? 'yes': 'No'}</button>
        </>
    )
}