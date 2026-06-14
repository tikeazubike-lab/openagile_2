import Lion from './assets/lion.jpg'
import React, { useState } from 'react'

export default function EventAndInteractWithReact(){
    let i = 0
    function HandleEvent(){
        console.log(`mouse hovering ${++i}`)
    }

    const [ingredients,  addIngredients] = useState(["tomatoes", "oregano", "chicken"])
    const IngredientsElements = ingredients.map((ingredient)=>{
        return <li key={ingredient}>{ingredient}</li>
    })

    function submitForm(formData: FormData){
        const newIngredient = formData.get("key")
        
        if (typeof newIngredient === "string") {
            addIngredients(prev => [...prev, newIngredient])
            
        }

       
    }

 

    
    
    
    return (
        <article>
            <p>Pic of a Lion</p>
            <hr />
            <img 
            src={Lion} 
            alt="pic of a Lion" 
            onMouseOver={HandleEvent}
            onMouseEnter={()=>{console.log("Mouse Enter")}}
            onMouseLeave={()=>{console.log("Mouse Leave")}}
            />
            <ul>
                {IngredientsElements}
            </ul>
            
            <form action={submitForm}  className='form-on-submit'>
                <input type="text" name="key" id="ingredient" placeholder='Type your ingredients'/>
                <button type="submit">submit</button>
            </form>
        </article>
    )
}