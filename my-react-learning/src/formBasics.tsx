export default function FormBasics() {

  function signUp(formData: FormData){
    const objectForm = Object.fromEntries(formData)
    const dietaryRestrictions = formData.getAll("dietaryRestrictions")
    const allForm = {
      ...objectForm,
      dietaryRestrictions
    }
    console.log(allForm)
    // console.log(employmentStatus)

  }
  return (
    <section id="main-section">
      <h1>Signup form</h1>
      <form action={signUp}>
        <label htmlFor="email">Email:</label>
        <input id="email" type="email" name="email"  defaultValue={"bob@dogo.net"}/>
        <br />
        <label htmlFor="password">Password</label>
        <input type="password" id="password" name="password" defaultValue={"password"}/>
        
        <fieldset className="radio-fieldset">
          <legend>Employment Status</legend>
          <label><input type="radio" name="employmentStatus" value={"Unemployed"} /> Unemployed</label>
          <label><input type="radio" name="employmentStatus" value={"Part-Time"} /> Part-Time</label>
          <label><input type="radio" name="employmentStatus" value="Full-Time" /> Full-Time</label>
        </fieldset>
        <fieldset>
          <legend>Dietary Restrictions</legend>
          <label>
            <input type="checkbox" value="kosher" name="dietaryRestrictions"/> Kosher
          </label>
        
         <label>
            <input type="checkbox" value={"vegan"} defaultChecked name="dietaryRestrictions"/> Vegan
          </label>
           <label>
            <input type="checkbox" value={"gluten-free"} name="dietaryRestrictions"/> Gluten-Free
          </label>
          </fieldset>
        <button type="submit">submit</button>
      </form>
    </section>
  )
}

