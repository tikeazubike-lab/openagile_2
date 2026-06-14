import type { Product } from "../assets/inventory"

export default function NewInventory(props: Product){
  return (
    <article className="product-card">
      <div className="product-header">
        <img src={props.thumbnail} alt={props.title} className="product-thumbnail" />
        <div className="product-basic-info">
          <h2 className="product-title">{props.title}</h2>
          <p className="product-brand">{props.brand}</p>
          <span className="product-category">{props.category}</span>
        </div>
      </div>
      
      <div className="product-description">
        <p>{props.description}</p>
      </div>
      
      <div className="product-pricing">
        <span className="product-price">${props.price.toFixed(2)}</span>
        <span className="product-discount">{props.discountPercentage}% off</span>
        <div className="product-rating">
          <span>★</span>
          <span>{props.rating}</span>
        </div>
      </div>
      
      <div className="product-details">
        <div className="detail-item">
          <span className="detail-label">SKU:</span>
          <span className="detail-value">{props.sku}</span>
        </div>
        <div className="detail-item">
          <span className="detail-label">Stock:</span>
          <span className="detail-value">{props.stock}</span>
        </div>
        <div className="detail-item">
          <span className="detail-label">Weight:</span>
          <span className="detail-value">{props.weight} kg</span>
        </div>
        <div className="detail-item">
          <span className="detail-label">Dimensions:</span>
          <span className="detail-value">{props.dimensions.width} × {props.dimensions.height} × {props.dimensions.depth} cm</span>
        </div>
        <div className="detail-item">
          <span className="detail-label">Min Order:</span>
          <span className="detail-value">{props.minimumOrderQuantity}</span>
        </div>
        <div className="detail-item">
          <span className="detail-label">Availability:</span>
          <span className={`detail-value status-${props.availabilityStatus.toLowerCase().replace(' ', '-')}`}>{props.availabilityStatus}</span>
        </div>
      </div>
      
      <div className="product-tags">
        {props.tags.map((tag, index) => (
          <span key={index} className="tag">{tag}</span>
        ))}
      </div>
      
      <div className="product-policies">
        <div className="policy-item">
          <span className="policy-label">Warranty:</span>
          <span className="policy-value">{props.warrantyInformation}</span>
        </div>
        <div className="policy-item">
          <span className="policy-label">Shipping:</span>
          <span className="policy-value">{props.shippingInformation}</span>
        </div>
        <div className="policy-item">
          <span className="policy-label">Return Policy:</span>
          <span className="policy-value">{props.returnPolicy}</span>
        </div>
      </div>
      
      <div className="product-reviews">
        <h3>Reviews ({props.reviews.length})</h3>
        {props.reviews.map((review, index) => (
          <div key={index} className="review-item">
            <div className="review-header">
              <span className="reviewer-name">{review.reviewerName}</span>
              <span className="review-rating">★ {review.rating}</span>
              <span className="review-date">{review.date}</span>
            </div>
            <p className="review-comment">{review.comment}</p>
            <span className="reviewer-email">{review.reviewerEmail}</span>
          </div>
        ))}
      </div>
      
      <div className="product-images">
        <h3>Product Images</h3>
        <div className="images-grid">
          {props.images.map((image, index) => (
            <img key={index} src={image} alt={`${props.title} - Image ${index + 1}`} className="product-image" />
          ))}
        </div>
      </div>
      
      <div className="product-meta">
        <div className="meta-item">
          <span className="meta-label">Created:</span>
          <span className="meta-value">{new Date(props.meta.createdAt).toLocaleDateString()}</span>
        </div>
        <div className="meta-item">
          <span className="meta-label">Updated:</span>
          <span className="meta-value">{new Date(props.meta.updatedAt).toLocaleDateString()}</span>
        </div>
        <div className="meta-item">
          <span className="meta-label">Barcode:</span>
          <span className="meta-value">{props.meta.barcode}</span>
        </div>
        <div className="meta-item">
          <span className="meta-label">QR Code:</span>
          <a href={props.meta.qrCode} className="qr-link" target="_blank" rel="noopener noreferrer">View QR Code</a>
        </div>
      </div>
    </article>
  )
}