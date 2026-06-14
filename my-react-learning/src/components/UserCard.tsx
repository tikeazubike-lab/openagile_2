import type { User } from "../assets/usersData"

export default function UserCard(props: User) {
  // Debug: Log props when component renders (remove in production)
  console.log('[UserCard] Props received for user:', props.id, props.firstName, props.lastName)

  return (
    <article className="user-card">
      <div className="user-header">
        <img src={props.image} alt={`${props.firstName} ${props.lastName}`} className="user-avatar" />
        <div className="user-info">
          <h2 className="user-name">{props.firstName} {props.lastName}</h2>
          <p className="user-role">{props.role}</p>
          <p className="user-username">@{props.username}</p>
        </div>
      </div>

      <div className="user-details">
        <div className="detail-section">
          <h3>Personal Information</h3>
          <div className="detail-grid">
            <div className="detail-item">
              <span className="detail-label">Age:</span>
              <span className="detail-value">{props.age}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Gender:</span>
              <span className="detail-value">{props.gender}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Birth Date:</span>
              <span className="detail-value">{props.birthDate}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Blood Group:</span>
              <span className="detail-value">{props.bloodGroup}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Height:</span>
              <span className="detail-value">{props.height} cm</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Weight:</span>
              <span className="detail-value">{props.weight} kg</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Eye Color:</span>
              <span className="detail-value">{props.eyeColor}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Hair:</span>
              <span className="detail-value">{props.hair.color} ({props.hair.type})</span>
            </div>
          </div>
        </div>

        <div className="detail-section">
          <h3>Contact Information</h3>
          <div className="detail-grid">
            <div className="detail-item full-width">
              <span className="detail-label">Email:</span>
              <span className="detail-value">{props.email}</span>
            </div>
            <div className="detail-item full-width">
              <span className="detail-label">Phone:</span>
              <span className="detail-value">{props.phone}</span>
            </div>
            <div className="detail-item full-width">
              <span className="detail-label">IP Address:</span>
              <span className="detail-value">{props.ip}</span>
            </div>
          </div>
        </div>

        <div className="detail-section">
          <h3>Address</h3>
          <div className="address-details">
            <p className="address-line">{props.address.address}</p>
            <p className="address-line">
              {props.address.city}, {props.address.state} {props.address.postalCode}
            </p>
            <p className="address-line">{props.address.country}</p>
            <p className="coordinates">
              Coordinates: {props.address.coordinates.lat}, {props.address.coordinates.lng}
            </p>
          </div>
        </div>

        <div className="detail-section">
          <h3>Education & Career</h3>
          <div className="detail-grid">
            <div className="detail-item full-width">
              <span className="detail-label">University:</span>
              <span className="detail-value">{props.university}</span>
            </div>
            <div className="detail-item full-width">
              <span className="detail-label">Company:</span>
              <span className="detail-value">{props.company.name}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Department:</span>
              <span className="detail-value">{props.company.department}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Title:</span>
              <span className="detail-value">{props.company.title}</span>
            </div>
          </div>
        </div>

        <div className="detail-section">
          <h3>Bank Information</h3>
          <div className="bank-details">
            <div className="bank-item">
              <span className="bank-label">Card Type:</span>
              <span className="bank-value">{props.bank.cardType}</span>
            </div>
            <div className="bank-item">
              <span className="bank-label">Card Number:</span>
              <span className="bank-value">**** **** **** {props.bank.cardNumber.slice(-4)}</span>
            </div>
            <div className="bank-item">
              <span className="bank-label">Expires:</span>
              <span className="bank-value">{props.bank.cardExpire}</span>
            </div>
            <div className="bank-item">
              <span className="bank-label">Currency:</span>
              <span className="bank-value">{props.bank.currency}</span>
            </div>
          </div>
        </div>

        <div className="detail-section">
          <h3>Cryptocurrency</h3>
          <div className="crypto-details">
            <div className="crypto-item">
              <span className="crypto-label">Coin:</span>
              <span className="crypto-value">{props.crypto.coin}</span>
            </div>
            <div className="crypto-item">
              <span className="crypto-label">Network:</span>
              <span className="crypto-value">{props.crypto.network}</span>
            </div>
            <div className="crypto-item full-width">
              <span className="crypto-label">Wallet:</span>
              <span className="crypto-value wallet">{props.crypto.wallet}</span>
            </div>
          </div>
        </div>
      </div>
    </article>
  )
}
