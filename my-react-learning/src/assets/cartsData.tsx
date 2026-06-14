export interface Transaction {
  carts: Cart[]
  total: number
  skip: number
  limit: number
}

export interface Cart {
  id: number
  products: Product[]
  total: number
  discountedTotal: number
  userId: number
  totalProducts: number
  totalQuantity: number
}

export interface Product {
  id: number
  title: string
  price: number
  quantity: number
  total: number
  discountPercentage: number
  discountedTotal: number
  thumbnail: string
}

export const cartsData: Transaction = {
  carts: [
    {
      id: 1,
      products: [
        {
          id: 1,
          title: "Premium Wireless Headphones",
          price: 299.99,
          quantity: 1,
          total: 299.99,
          discountPercentage: 15,
          discountedTotal: 254.99,
          thumbnail: "https://example.com/images/headphones-thumb.jpg"
        },
        {
          id: 2,
          title: "Smart Fitness Watch",
          price: 199.99,
          quantity: 2,
          total: 399.98,
          discountPercentage: 20,
          discountedTotal: 319.98,
          thumbnail: "https://example.com/images/watch-thumb.jpg"
        }
      ],
      total: 699.97,
      discountedTotal: 574.97,
      userId: 101,
      totalProducts: 2,
      totalQuantity: 3
    },
    {
      id: 2,
      products: [
        {
          id: 3,
          title: "Ergonomic Office Chair",
          price: 449.99,
          quantity: 1,
          total: 449.99,
          discountPercentage: 10,
          discountedTotal: 404.99,
          thumbnail: "https://example.com/images/chair-thumb.jpg"
        },
        {
          id: 4,
          title: "Stainless Steel Water Bottle",
          price: 34.99,
          quantity: 3,
          total: 104.97,
          discountPercentage: 5,
          discountedTotal: 99.72,
          thumbnail: "https://example.com/images/bottle-thumb.jpg"
        }
      ],
      total: 554.96,
      discountedTotal: 504.71,
      userId: 102,
      totalProducts: 2,
      totalQuantity: 4
    },
    {
      id: 3,
      products: [
        {
          id: 5,
          title: "Mechanical Gaming Keyboard",
          price: 149.99,
          quantity: 1,
          total: 149.99,
          discountPercentage: 12,
          discountedTotal: 131.99,
          thumbnail: "https://example.com/images/keyboard-thumb.jpg"
        },
        {
          id: 6,
          title: "Organic Cotton T-Shirt",
          price: 29.99,
          quantity: 5,
          total: 149.95,
          discountPercentage: 25,
          discountedTotal: 112.46,
          thumbnail: "https://example.com/images/tshirt-thumb.jpg"
        },
        {
          id: 1,
          title: "Premium Wireless Headphones",
          price: 299.99,
          quantity: 1,
          total: 299.99,
          discountPercentage: 15,
          discountedTotal: 254.99,
          thumbnail: "https://example.com/images/headphones-thumb.jpg"
        }
      ],
      total: 599.93,
      discountedTotal: 499.44,
      userId: 103,
      totalProducts: 3,
      totalQuantity: 7
    },
    {
      id: 4,
      products: [
        {
          id: 2,
          title: "Smart Fitness Watch",
          price: 199.99,
          quantity: 1,
          total: 199.99,
          discountPercentage: 20,
          discountedTotal: 159.99,
          thumbnail: "https://example.com/images/watch-thumb.jpg"
        },
        {
          id: 4,
          title: "Stainless Steel Water Bottle",
          price: 34.99,
          quantity: 2,
          total: 69.98,
          discountPercentage: 5,
          discountedTotal: 66.48,
          thumbnail: "https://example.com/images/bottle-thumb.jpg"
        }
      ],
      total: 269.97,
      discountedTotal: 226.47,
      userId: 104,
      totalProducts: 2,
      totalQuantity: 3
    },
    {
      id: 5,
      products: [
        {
          id: 3,
          title: "Ergonomic Office Chair",
          price: 449.99,
          quantity: 2,
          total: 899.98,
          discountPercentage: 10,
          discountedTotal: 809.98,
          thumbnail: "https://example.com/images/chair-thumb.jpg"
        }
      ],
      total: 899.98,
      discountedTotal: 809.98,
      userId: 105,
      totalProducts: 1,
      totalQuantity: 2
    },
    {
      id: 6,
      products: [
        {
          id: 5,
          title: "Mechanical Gaming Keyboard",
          price: 149.99,
          quantity: 2,
          total: 299.98,
          discountPercentage: 12,
          discountedTotal: 263.98,
          thumbnail: "https://example.com/images/keyboard-thumb.jpg"
        },
        {
          id: 6,
          title: "Organic Cotton T-Shirt",
          price: 29.99,
          quantity: 3,
          total: 89.97,
          discountPercentage: 25,
          discountedTotal: 67.48,
          thumbnail: "https://example.com/images/tshirt-thumb.jpg"
        },
        {
          id: 4,
          title: "Stainless Steel Water Bottle",
          price: 34.99,
          quantity: 1,
          total: 34.99,
          discountPercentage: 5,
          discountedTotal: 33.24,
          thumbnail: "https://example.com/images/bottle-thumb.jpg"
        }
      ],
      total: 424.94,
      discountedTotal: 364.70,
      userId: 106,
      totalProducts: 3,
      totalQuantity: 6
    }
  ],
  total: 6,
  skip: 0,
  limit: 6
}
