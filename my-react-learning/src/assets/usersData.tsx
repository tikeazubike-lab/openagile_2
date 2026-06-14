export interface Root {
  users: User[]
  total: number
  skip: number
  limit: number
}

export interface User {
  id: number
  firstName: string
  lastName: string
  maidenName: string
  age: number
  gender: string
  email: string
  phone: string
  username: string
  password: string
  birthDate: string
  image: string
  bloodGroup: string
  height: number
  weight: number
  eyeColor: string
  hair: Hair
  ip: string
  address: Address
  macAddress: string
  university: string
  bank: Bank
  company: Company
  ein: string
  ssn: string
  userAgent: string
  crypto: Crypto
  role: string
}

export interface Hair {
  color: string
  type: string
}

export interface Address {
  address: string
  city: string
  state: string
  stateCode: string
  postalCode: string
  coordinates: Coordinates
  country: string
}

export interface Coordinates {
  lat: number
  lng: number
}

export interface Bank {
  cardExpire: string
  cardNumber: string
  cardType: string
  currency: string
  iban: string
}

export interface Company {
  department: string
  name: string
  title: string
  address: Address2
}

export interface Address2 {
  address: string
  city: string
  state: string
  stateCode: string
  postalCode: string
  coordinates: Coordinates2
  country: string
}

export interface Coordinates2 {
  lat: number
  lng: number
}

export interface Crypto {
  coin: string
  wallet: string
  network: string
}

export const usersData: Root = {
  users: [
    {
      id: 1,
      firstName: "Terry",
      lastName: "Medhurst",
      maidenName: "Smitham",
      age: 50,
      gender: "male",
      email: "atuny0@sohu.com",
      phone: "+63 791 675 8914",
      username: "atuny0",
      password: "9uQFF1Lh",
      birthDate: "2000-12-25",
      image: "https://i.pravatar.cc/150?u=1",
      bloodGroup: "A+",
      height: 189,
      weight: 75.4,
      eyeColor: "Green",
      hair: {
        color: "Black",
        type: "Strands"
      },
      ip: "117.29.86.254",
      address: {
        address: "1745 T Street Southeast",
        city: "Washington",
        state: "DC",
        stateCode: "DC",
        postalCode: "20020",
        coordinates: {
          lat: 38.867033,
          lng: -76.979235
        },
        country: "United States"
      },
      macAddress: "13:69:BA:28:A3:5A",
      university: "Capitol University",
      bank: {
        cardExpire: "06/22",
        cardNumber: "50380955204220685",
        cardType: "maestro",
        currency: "Peso",
        iban: "NO17 0695 2754 967"
      },
      company: {
        department: "Marketing",
        name: "Blanda-O'Keefe",
        title: "Help Desk Operator",
        address: {
          address: "3251 University Street",
          city: "Boulder",
          state: "Colorado",
          stateCode: "CO",
          postalCode: "80305",
          coordinates: {
            lat: 40.009425,
            lng: -105.242788
          },
          country: "United States"
        }
      },
      ein: "20-9487066",
      ssn: "661-64-2976",
      userAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
      crypto: {
        coin: "Bitcoin",
        wallet: "0xb9fc2fe63b2a6c003f1c324c3bfa53259162181a",
        network: "Ethereum (ERC20)"
      },
      role: "admin"
    },
    {
      id: 2,
      firstName: "Sheldon",
      lastName: "Quigley",
      maidenName: "Cole",
      age: 28,
      gender: "male",
      email: "hbingley1@plala.or.jp",
      phone: "+7 813 117 7139",
      username: "hbingley1",
      password: "CQutx25i8r",
      birthDate: "1992-03-20",
      image: "https://i.pravatar.cc/150?u=2",
      bloodGroup: "O+",
      height: 187,
      weight: 74,
      eyeColor: "Brown",
      hair: {
        color: "Blond",
        type: "Very curly"
      },
      ip: "48.135.142.197",
      address: {
        address: "6007 Applegate Lane",
        city: "Louisville",
        state: "Kentucky",
        stateCode: "KY",
        postalCode: "40219",
        coordinates: {
          lat: 38.1343013,
          lng: -85.6498512
        },
        country: "United States"
      },
      macAddress: "F8:04:9E:3C:C7:2E",
      university: "Stavropol State Technical University",
      bank: {
        cardExpire: "10/23",
        cardNumber: "5355920631952404",
        cardType: "mastercard",
        currency: "Ruble",
        iban: "MD63 L6YC 8Y4U 4JEQ 95XV KFQZ D"
      },
      company: {
        department: "Sales",
        name: "Aufderhar-Cronin",
        title: "Senior Sales Associate",
        address: {
          address: "560 Penelope Lane",
          city: "Manchester",
          state: "New Hampshire",
          stateCode: "NH",
          postalCode: "03103",
          coordinates: {
            lat: 42.9589183,
            lng: -71.4489836
          },
          country: "United States"
        }
      },
      ein: "52-5262907",
      ssn: "419-72-3107",
      userAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
      crypto: {
        coin: "Bitcoin",
        wallet: "0x0716581636Ad6eAa368219511a87b64A6410F359",
        network: "Ethereum (ERC20)"
      },
      role: "user"
    },
    {
      id: 3,
      firstName: "Terrill",
      lastName: "Hills",
      maidenName: "Hoeger",
      age: 38,
      gender: "male",
      email: "sshaffer6@yolasite.com",
      phone: "+54 735 332 5868",
      username: "sshaffer6",
      password: "SRsx1mLq$",
      birthDate: "1984-04-15",
      image: "https://i.pravatar.cc/150?u=3",
      bloodGroup: "AB-",
      height: 200,
      weight: 105.3,
      eyeColor: "Gray",
      hair: {
        color: "Blond",
        type: "Straight"
      },
      ip: "189.55.39.137",
      address: {
        address: "5601 West 83rd Street",
        city: "Shawnee",
        state: "Kansas",
        stateCode: "KS",
        postalCode: "66218",
        coordinates: {
          lat: 38.961911,
          lng: -94.806322
        },
        country: "United States"
      },
      macAddress: "5C:EA:F6:4A:0E:EB",
      university: "University of Cuenca",
      bank: {
        cardExpire: "07/24",
        cardNumber: "3586082013396926",
        cardType: "jcb",
        currency: "Cordoba",
        iban: "GT82 VYQW F0YV M9TJ V5GP QIGG G"
      },
      company: {
        department: "Services",
        name: "Bahringer, Auer and Wehner",
        title: "Financial Analyst",
        address: {
          address: "6423 Bartlett Avenue",
          city: "Anchorage",
          state: "Alaska",
          stateCode: "AK",
          postalCode: "99501",
          coordinates: {
            lat: 61.208632,
            lng: -149.868565
          },
          country: "United States"
        }
      },
      ein: "71-3644335",
      ssn: "732-46-6015",
      userAgent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
      crypto: {
        coin: "Bitcoin",
        wallet: "0x4D7F4899837595F91579A13E1Ff4D3F3F3F3F3F3",
        network: "Ethereum (ERC20)"
      },
      role: "user"
    }
  ],
  total: 3,
  skip: 0,
  limit: 3
}
