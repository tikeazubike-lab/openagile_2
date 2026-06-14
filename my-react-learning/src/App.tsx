// import './App.css'
// import './Inventory.css'
// import { inventoryData } from './assets/inventory'
// import NewInventory from './components/NewInventory'
// import { cartsData } from './assets/cartsData'
// import NewCart from './components/NewCart'
// import './Users.css'
// import UserCard from './components/UserCard'
// import { usersData } from './assets/usersData'
// import './lion.css'
// import './eventwithreact.css'
// import EventAndInteractWithReact from "./EventAndInteractWithReact"
// import UseStateTest from "./useStateTest"
// import GoingOutTonight from "./goingOutTonight"
// import HandleList from "./handleList"
// import UpdateObjectState from "./updateObjectState"
// import './updateObjectState.css'
// import './radio.css'
// import FormBasics from "./formBasics"
import Cart from "./ShoppingCartTwo.tsx";

function App(){
  // Debug: Log data when App renders (remove in production)
  // console.log('[App] Rendering with', cartsData.carts.length, 'carts')

  // const InventoryDataElement = inventoryData.products.map((item)=>{
  //   return (
  //     <NewInventory {...item} />
  //   )
  // })

  // const UserDataElement = usersData.users.map((item)=>{
  //   return (
  //     <UserCard {...item} />
  //   )
  // })

  // const cartsDataElement = cartsData.carts.map((cart) => {
  //   // Debug: Log each cart being passed to NewCart (remove in production)
  //   console.log('[App] Passing cart to NewCart:', cart.id, cart)
  //   return (
  //     <NewCart {...cart} />
  //   )
  // })

  return (
    <main className="inventory-container">
      {/* <h1>Product Inventory</h1>
      {InventoryDataElement}
      <h1>Shopping Carts</h1>
      {cartsDataElement}
      <h1>Users</h1>
      {UserDataElement} */}
      {/* <EventAndInteractWithReact /> */}
      {/* <UseStateTest /> */}
      {/* <GoingOutTonight /> */}
      {/* <HandleList /> */}
      {/* <UpdateObjectState /> */}
      {/*<FormBasics />*/}
        <Cart />
    </main>

  )
}

export default App
