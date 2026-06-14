import { useState } from "react"

export default function UseStateTest(){
    const [age, setAge] = useState(0)

    function increaseCount(){
        setAge(age => age < 100 ? age + 1 : 100)
    }
    
    function decreaseCount(){
        setAge(age => age > 0 ? age - 1 : 0)
    }

    function resetAge(){
        setAge(0)
    }
    
    return (
        <main id="set-card">
        <p>{age}</p>
        <button type="button" onClick={increaseCount}>increase count</button>
        <button type="button" onClick={resetAge}>Reset Age</button>
        <button type="button" onClick={decreaseCount}>decrease count</button>
        </main>
    )
}