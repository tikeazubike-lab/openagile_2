export interface InventoryType {
  products: Product[]
  total: number
  skip: number
  limit: number
}

export interface Product {
  id: number
  title: string
  description: string
  category: string
  price: number
  discountPercentage: number
  rating: number
  stock: number
  tags: string[]
  brand: string
  sku: string
  weight: number
  dimensions: Dimensions
  warrantyInformation: string
  shippingInformation: string
  availabilityStatus: string
  reviews: Review[]
  returnPolicy: string
  minimumOrderQuantity: number
  meta: Meta
  images: string[]
  thumbnail: string
}

export interface Dimensions {
  width: number
  height: number
  depth: number
}

export interface Review {
  rating: number
  comment: string
  date: string
  reviewerName: string
  reviewerEmail: string
}

export interface Meta {
  createdAt: string
  updatedAt: string
  barcode: string
  qrCode: string
}

export const inventoryData: InventoryType = {
  products: [
    {
      id: 1,
      title: "Premium Wireless Headphones",
      description: "High-quality wireless headphones with active noise cancellation, 30-hour battery life, and premium sound quality for immersive audio experience.",
      category: "Electronics",
      price: 299.99,
      discountPercentage: 15,
      rating: 4.7,
      stock: 45,
      tags: ["wireless", "noise-cancelling", "bluetooth", "audio"],
      brand: "SoundMax",
      sku: "SM-WH-001",
      weight: 0.25,
      dimensions: {
        width: 18,
        height: 20,
        depth: 8
      },
      warrantyInformation: "2 years warranty",
      shippingInformation: "Free shipping on orders over $50",
      availabilityStatus: "In Stock",
      reviews: [
        {
          rating: 5,
          comment: "Amazing sound quality and the noise cancellation is top-notch!",
          date: "2024-01-15",
          reviewerName: "John Smith",
          reviewerEmail: "john.smith@example.com"
        },
        {
          rating: 4,
          comment: "Great headphones, battery life is impressive.",
          date: "2024-01-10",
          reviewerName: "Sarah Johnson",
          reviewerEmail: "sarah.j@example.com"
        }
      ],
      returnPolicy: "30 days return policy",
      minimumOrderQuantity: 1,
      meta: {
        createdAt: "2023-06-15T08:00:00.000Z",
        updatedAt: "2024-01-20T10:30:00.000Z",
        barcode: "8901234567890",
        qrCode: "https://example.com/qr/SM-WH-001"
      },
      images: [
        "https://example.com/images/headphones1.jpg",
        "https://example.com/images/headphones2.jpg",
        "https://example.com/images/headphones3.jpg"
      ],
      thumbnail: "https://example.com/images/headphones-thumb.jpg"
    },
    {
      id: 2,
      title: "Ergonomic Office Chair",
      description: "Premium ergonomic office chair with lumbar support, adjustable armrests, and breathable mesh back for all-day comfort.",
      category: "Furniture",
      price: 449.99,
      discountPercentage: 10,
      rating: 4.5,
      stock: 28,
      tags: ["ergonomic", "office", "adjustable", "comfort"],
      brand: "ComfortSeating",
      sku: "CS-OC-002",
      weight: 18,
      dimensions: {
        width: 65,
        height: 120,
        depth: 65
      },
      warrantyInformation: "5 years warranty",
      shippingInformation: "Assembly required. Free shipping.",
      availabilityStatus: "In Stock",
      reviews: [
        {
          rating: 5,
          comment: "Best office chair I've ever owned. My back pain is gone!",
          date: "2024-01-18",
          reviewerName: "Michael Brown",
          reviewerEmail: "m.brown@example.com"
        },
        {
          rating: 4,
          comment: "Very comfortable and easy to assemble.",
          date: "2024-01-12",
          reviewerName: "Emily Davis",
          reviewerEmail: "emily.d@example.com"
        }
      ],
      returnPolicy: "30 days return policy",
      minimumOrderQuantity: 1,
      meta: {
        createdAt: "2023-07-20T09:00:00.000Z",
        updatedAt: "2024-01-18T14:20:00.000Z",
        barcode: "8901234567891",
        qrCode: "https://example.com/qr/CS-OC-002"
      },
      images: [
        "https://example.com/images/chair1.jpg",
        "https://example.com/images/chair2.jpg",
        "https://example.com/images/chair3.jpg"
      ],
      thumbnail: "https://example.com/images/chair-thumb.jpg"
    },
    {
      id: 3,
      title: "Smart Fitness Watch",
      description: "Advanced fitness tracker with heart rate monitoring, GPS, sleep tracking, and 7-day battery life for health enthusiasts.",
      category: "Wearables",
      price: 199.99,
      discountPercentage: 20,
      rating: 4.6,
      stock: 62,
      tags: ["fitness", "smartwatch", "health", "gps"],
      brand: "FitTech",
      sku: "FT-SW-003",
      weight: 0.05,
      dimensions: {
        width: 4.5,
        height: 5.5,
        depth: 1.2
      },
      warrantyInformation: "1 year warranty",
      shippingInformation: "Free shipping",
      availabilityStatus: "In Stock",
      reviews: [
        {
          rating: 5,
          comment: "Perfect for tracking my workouts. The GPS is very accurate!",
          date: "2024-01-20",
          reviewerName: "David Wilson",
          reviewerEmail: "d.wilson@example.com"
        },
        {
          rating: 4,
          comment: "Great features, battery life could be better.",
          date: "2024-01-14",
          reviewerName: "Lisa Anderson",
          reviewerEmail: "lisa.a@example.com"
        }
      ],
      returnPolicy: "30 days return policy",
      minimumOrderQuantity: 1,
      meta: {
        createdAt: "2023-08-10T10:00:00.000Z",
        updatedAt: "2024-01-20T11:45:00.000Z",
        barcode: "8901234567892",
        qrCode: "https://example.com/qr/FT-SW-003"
      },
      images: [
        "https://example.com/images/watch1.jpg",
        "https://example.com/images/watch2.jpg",
        "https://example.com/images/watch3.jpg"
      ],
      thumbnail: "https://example.com/images/watch-thumb.jpg"
    },
    {
      id: 4,
      title: "Stainless Steel Water Bottle",
      description: "Eco-friendly insulated water bottle that keeps drinks cold for 24 hours or hot for 12 hours. BPA-free and leak-proof.",
      category: "Kitchen",
      price: 34.99,
      discountPercentage: 5,
      rating: 4.8,
      stock: 150,
      tags: ["eco-friendly", "insulated", "bpa-free", "portable"],
      brand: "EcoHydrate",
      sku: "EH-WB-004",
      weight: 0.35,
      dimensions: {
        width: 8,
        height: 26,
        depth: 8
      },
      warrantyInformation: "Lifetime warranty",
      shippingInformation: "Free shipping",
      availabilityStatus: "In Stock",
      reviews: [
        {
          rating: 5,
          comment: "Keeps my water ice cold all day! Love the design.",
          date: "2024-01-19",
          reviewerName: "Jennifer Martinez",
          reviewerEmail: "j.martinez@example.com"
        },
        {
          rating: 5,
          comment: "Best water bottle I've ever owned. No leaks!",
          date: "2024-01-16",
          reviewerName: "Robert Taylor",
          reviewerEmail: "r.taylor@example.com"
        }
      ],
      returnPolicy: "30 days return policy",
      minimumOrderQuantity: 1,
      meta: {
        createdAt: "2023-09-05T11:00:00.000Z",
        updatedAt: "2024-01-19T09:15:00.000Z",
        barcode: "8901234567893",
        qrCode: "https://example.com/qr/EH-WB-004"
      },
      images: [
        "https://example.com/images/bottle1.jpg",
        "https://example.com/images/bottle2.jpg",
        "https://example.com/images/bottle3.jpg"
      ],
      thumbnail: "https://example.com/images/bottle-thumb.jpg"
    },
    {
      id: 5,
      title: "Mechanical Gaming Keyboard",
      description: "RGB backlit mechanical keyboard with customizable keys, programmable macros, and Cherry MX switches for gaming enthusiasts.",
      category: "Electronics",
      price: 149.99,
      discountPercentage: 12,
      rating: 4.7,
      stock: 38,
      tags: ["gaming", "mechanical", "rgb", "programmable"],
      brand: "GameGear",
      sku: "GG-MK-005",
      weight: 1.2,
      dimensions: {
        width: 44,
        height: 4,
        depth: 14
      },
      warrantyInformation: "2 years warranty",
      shippingInformation: "Free shipping",
      availabilityStatus: "In Stock",
      reviews: [
        {
          rating: 5,
          comment: "The tactile feel is amazing. RGB lighting is stunning!",
          date: "2024-01-17",
          reviewerName: "Chris Lee",
          reviewerEmail: "chris.lee@example.com"
        },
        {
          rating: 4,
          comment: "Great keyboard for gaming and typing.",
          date: "2024-01-13",
          reviewerName: "Amanda White",
          reviewerEmail: "a.white@example.com"
        }
      ],
      returnPolicy: "30 days return policy",
      minimumOrderQuantity: 1,
      meta: {
        createdAt: "2023-10-01T12:00:00.000Z",
        updatedAt: "2024-01-17T16:30:00.000Z",
        barcode: "8901234567894",
        qrCode: "https://example.com/qr/GG-MK-005"
      },
      images: [
        "https://example.com/images/keyboard1.jpg",
        "https://example.com/images/keyboard2.jpg",
        "https://example.com/images/keyboard3.jpg"
      ],
      thumbnail: "https://example.com/images/keyboard-thumb.jpg"
    },
    {
      id: 6,
      title: "Organic Cotton T-Shirt",
      description: "Soft, breathable 100% organic cotton t-shirt in classic fit. Sustainable production with eco-friendly dyes.",
      category: "Clothing",
      price: 29.99,
      discountPercentage: 25,
      rating: 4.4,
      stock: 200,
      tags: ["organic", "cotton", "sustainable", "comfortable"],
      brand: "EcoWear",
      sku: "EW-TS-006",
      weight: 0.2,
      dimensions: {
        width: 50,
        height: 70,
        depth: 1
      },
      warrantyInformation: "Quality guarantee",
      shippingInformation: "Free shipping on orders over $30",
      availabilityStatus: "In Stock",
      reviews: [
        {
          rating: 4,
          comment: "Very comfortable and soft material. Love that it's organic!",
          date: "2024-01-21",
          reviewerName: "Nicole Brown",
          reviewerEmail: "nicole.b@example.com"
        },
        {
          rating: 5,
          comment: "Great quality for the price. Will buy more colors.",
          date: "2024-01-15",
          reviewerName: "Kevin Garcia",
          reviewerEmail: "k.garcia@example.com"
        }
      ],
      returnPolicy: "30 days return policy",
      minimumOrderQuantity: 1,
      meta: {
        createdAt: "2023-11-15T13:00:00.000Z",
        updatedAt: "2024-01-21T08:00:00.000Z",
        barcode: "8901234567895",
        qrCode: "https://example.com/qr/EW-TS-006"
      },
      images: [
        "https://example.com/images/tshirt1.jpg",
        "https://example.com/images/tshirt2.jpg",
        "https://example.com/images/tshirt3.jpg"
      ],
      thumbnail: "https://example.com/images/tshirt-thumb.jpg"
    }
  ],
  total: 6,
  skip: 0,
  limit: 6
}
