# UserCard Component Integration Guide

## Files Created

1. **`src/assets/usersData.tsx`** - Contains all TypeScript interfaces and sample data
2. **`src/components/UserCard.tsx`** - React component that displays user information
3. **`src/Users.css`** - Styling for the UserCard component

## How to Integrate into App.tsx

### Step 1: Import the necessary files

Add these imports at the top of your `src/App.tsx`:

```tsx
import './Users.css'
import { usersData } from './assets/usersData'
import UserCard from './components/UserCard'
```

### Step 2: Map over the users array

Create a mapping function to generate UserCard components:

```tsx
const usersDataElement = usersData.users.map((user) => {
  // Debug: Log each user being passed to UserCard
  console.log('[App] Passing user to UserCard:', user.id, user.firstName, user.lastName)
  return (
    <UserCard {...user} />
  )
})
```

### Step 3: Add the users section to your JSX

Add the users section to your return statement:

```tsx
return (
  <main className="inventory-container">
    <h1>Product Inventory</h1>
    {InventoryDataElement}
    <h1>Shopping Carts</h1>
    {cartsDataElement}
    <h1>Users</h1>
    {usersDataElement}
  </main>
)
```

## Complete Example

Here's how your complete `App.tsx` should look after integration:

```tsx
import './App.css'
import './Inventory.css'
import './Users.css'
import { inventoryData } from './assets/inventory'
import NewInventory from './components/NewInventory'
import { cartsData } from './assets/cartsData'
import NewCart from './components/NewCart'
import { usersData } from './assets/usersData'
import UserCard from './components/UserCard'

function App(){
  console.log('[App] Rendering with', cartsData.carts.length, 'carts and', usersData.users.length, 'users')

  const InventoryDataElement = inventoryData.products.map((item)=>{
    return (
      <NewInventory {...item} />
    )
  })

  const cartsDataElement = cartsData.carts.map((cart) => {
    console.log('[App] Passing cart to NewCart:', cart.id, cart)
    return (
      <NewCart {...cart} />
    )
  })

  const usersDataElement = usersData.users.map((user) => {
    console.log('[App] Passing user to UserCard:', user.id, user.firstName, user.lastName)
    return (
      <UserCard {...user} />
    )
  })

  return (
    <main className="inventory-container">
      <h1>Product Inventory</h1>
      {InventoryDataElement}
      <h1>Shopping Carts</h1>
      {cartsDataElement}
      <h1>Users</h1>
      {usersDataElement}
    </main>
  )
}

export default App
```

## TypeScript Interfaces Available

The following interfaces are exported from `src/assets/usersData.tsx`:

- **`Root`** - The main data structure containing users array and metadata
- **`User`** - Individual user object with all properties
- **`Hair`** - Hair color and type
- **`Address`** - User's home address
- **`Coordinates`** - Geographic coordinates
- **`Bank`** - Banking information
- **`Company`** - Company details
- **`Address2`** - Company address
- **`Coordinates2`** - Company coordinates
- **`Crypto`** - Cryptocurrency information

## Data Structure

The `usersData` object has the following structure:

```tsx
{
  users: User[],      // Array of user objects
  total: number,      // Total number of users
  skip: number,       // Number of users skipped
  limit: number       // Limit of users returned
}
```

## Debugging

Both `UserCard.tsx` and the integration code include console.log statements for debugging:

- **UserCard component**: Logs when it receives props
- **App.tsx integration**: Logs when passing each user to UserCard

You can view these logs in the browser's developer console or use the VS Code debugger (see `DEBUGGING_PROPS_FLOW_GUIDE.md`).

## Styling

The UserCard component uses:
- Gradient purple background
- Responsive grid layout
- Hover effects with smooth transitions
- Mobile-friendly design
- Glassmorphism effects for detail sections

## Key Features of UserCard Component

1. **Header Section**: Displays user avatar, name, role, and username
2. **Personal Information**: Age, gender, birth date, blood group, height, weight, eye color, and hair
3. **Contact Information**: Email, phone, and IP address
4. **Address**: Full address with coordinates
5. **Education & Career**: University, company, department, and title
6. **Bank Information**: Card type, masked card number, expiry, and currency
7. **Cryptocurrency**: Coin type, network, and wallet address

## Tips

- The component uses the spread operator `{...user}` to pass all user properties as props
- Each user card is fully responsive and works on mobile devices
- The component includes debug logging that can be removed in production
- All data is type-safe with TypeScript interfaces
