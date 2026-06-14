import type { Cart } from "../assets/cartsData"

export default function NewCart(props: Cart){
  // Debug: Log props when component renders (remove in production)
  console.log('[NewCart] Props received:', props)
  console.log('[NewCart] Cart ID:', props.id, 'Products:', props.totalProducts)

  return (
    <article className="cart-card">
      <div className="cart-header">
        <h2 className="cart-title">Cart #{props.id}</h2>
        <span className="cart-user">User ID: {props.userId}</span>
      </div>
      
      <div className="cart-products">
        <h3>Products ({props.totalProducts})</h3>
        {props.products.map((product) => (
          <div key={product.id} className="cart-product-item">
            <img src={product.thumbnail} alt={product.title} className="cart-product-thumbnail" />
            <div className="cart-product-info">
              <h4 className="cart-product-title">{product.title}</h4>
              <div className="cart-product-details">
                <span className="cart-product-price">${product.price.toFixed(2)}</span>
                <span className="cart-product-quantity">× {product.quantity}</span>
                <span className="cart-product-total">${product.total.toFixed(2)}</span>
              </div>
              <div className="cart-product-discount">
                <span className="discount-badge">{product.discountPercentage}% off</span>
                <span className="discounted-price">Sale: ${product.discountedTotal.toFixed(2)}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      <div className="cart-summary">
        <div className="summary-item">
          <span className="summary-label">Total Products:</span>
          <span className="summary-value">{props.totalProducts}</span>
        </div>
        <div className="summary-item">
          <span className="summary-label">Total Quantity:</span>
          <span className="summary-value">{props.totalQuantity}</span>
        </div>
        <div className="summary-item subtotal">
          <span className="summary-label">Subtotal:</span>
          <span className="summary-value">${props.total.toFixed(2)}</span>
        </div>
        <div className="summary-item total">
          <span className="summary-label">Discounted Total:</span>
          <span className="summary-value">${props.discountedTotal.toFixed(2)}</span>
        </div>
        <div className="summary-item savings">
          <span className="summary-label">You Save:</span>
          <span className="summary-value">${(props.total - props.discountedTotal).toFixed(2)}</span>
        </div>
      </div>
    </article>
  )
}
