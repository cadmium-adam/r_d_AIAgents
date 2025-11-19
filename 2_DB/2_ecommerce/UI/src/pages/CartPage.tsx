import {
  Avatar,
  Badge,
  Button,
  Card,
  CardHeader,
  Spinner,
  Text,
} from "@fluentui/react-components";
import {
  Cart24Regular,
  Delete24Regular,
  Star24Filled,
  Star24Regular,
} from "@fluentui/react-icons";
import React, { useEffect, useState } from "react";
import { useApp } from "../components/AppProvider";
import { mongoService } from "../services/api";
import type { Cart, Review } from "../types";

const CartPage: React.FC = () => {
  const { state, setLoading, setError, setCart } = useApp();
  const [cart, setLocalCart] = useState<Cart | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [selectedProductReviews, setSelectedProductReviews] = useState<
    number | null
  >(null);

  useEffect(() => {
    if (state.currentUser) {
      loadCart();
    }
  }, [state.currentUser]);

  const loadCart = async () => {
    if (!state.currentUser) return;

    setLoading(true);
    try {
      const cartData = await mongoService.getCart(state.currentUser.id);
      console.log("Loaded cart data:", cartData);
      setLocalCart(cartData);
      setCart(cartData);
    } catch (error) {
      console.error("Failed to load cart:", error);
      setError("Failed to load cart");
    } finally {
      setLoading(false);
    }
  };

  const loadProductReviews = async (productId: number) => {
    try {
      const reviewsData = await mongoService.getProductReviews(productId, 1, 5);
      setReviews(reviewsData);
      setSelectedProductReviews(productId);
    } catch (error) {
      console.error("Failed to load reviews:", error);
    }
  };

  const removeFromCart = async (productId: number) => {
    if (!state.currentUser) return;

    try {
      await mongoService.removeFromCart(state.currentUser.id, productId);
      await loadCart(); // Reload cart
    } catch (error) {
      console.error("Failed to remove from cart:", error);
      setError("Failed to remove item from cart");
    }
  };

  const renderStars = (rating: number) => {
    const stars = [];
    for (let i = 1; i <= 5; i++) {
      stars.push(
        i <= rating ? (
          <Star24Filled
            key={i}
            style={{ color: "#ffb900", fontSize: "16px" }}
          />
        ) : (
          <Star24Regular
            key={i}
            style={{ color: "#d1d1d1", fontSize: "16px" }}
          />
        )
      );
    }
    return stars;
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(price);
  };

  return (
    <div>
      {/* Page Header */}
      <div style={{ marginBottom: "32px" }}>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "12px",
            marginBottom: "16px",
          }}
        >
          <Cart24Regular style={{ fontSize: "32px", color: "#47a248" }} />
          <div>
            <Text as="h1" size={800} weight="semibold">
              Shopping Cart & Reviews
            </Text>
            <Text size={400} style={{ color: "#605e5c" }}>
              Powered by MongoDB - Demonstrating flexible schemas, real-time
              updates, and rich document structures
            </Text>
          </div>
        </div>

        <div className="database-section">
          <div className="database-title">
            <Cart24Regular />
            MongoDB Features Demonstrated
          </div>
          <div className="database-description">
            This page showcases MongoDB's flexibility with complex nested
            documents and real-time data management.
          </div>
          <ul className="feature-list">
            <li>Flexible document schemas for cart items and reviews</li>
            <li>Nested objects for detailed review metadata</li>
            <li>Dynamic cart updates and session tracking</li>
            <li>Rich review data with pros, cons, and engagement</li>
            <li>Dynamic arrays for product images and tags</li>
            <li>Complex review documents with sentiment analysis</li>
          </ul>
        </div>
      </div>

      {state.loading ? (
        <div className="loading-container">
          <Spinner size="large" label="Loading cart..." />
        </div>
      ) : state.error ? (
        <div className="error-container">
          <Text size={500} style={{ color: "#d13438" }}>
            {state.error}
          </Text>
        </div>
      ) : !state.currentUser ? (
        <Card>
          <div style={{ padding: "32px", textAlign: "center" }}>
            <Text size={500}>Please sign in to view your cart</Text>
          </div>
        </Card>
      ) : !cart || cart.items.length === 0 ? (
        <Card>
          <div style={{ padding: "32px", textAlign: "center" }}>
            <Cart24Regular
              style={{
                fontSize: "48px",
                color: "#605e5c",
                marginBottom: "16px",
              }}
            />
            <Text size={500} style={{ marginBottom: "16px", display: "block" }}>
              Your cart is empty
            </Text>
            <Text
              size={400}
              style={{
                color: "#605e5c",
                marginBottom: "24px",
                display: "block",
              }}
            >
              Add some products to see MongoDB's flexible document structure in
              action
            </Text>
            <Button appearance="primary">Browse Products</Button>
          </div>
        </Card>
      ) : (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 300px",
            gap: "24px",
          }}
        >
          {/* Cart Items */}
          <div>
            <Card>
              <CardHeader
                header={
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                    }}
                  >
                    <Text size={600} weight="semibold">
                      Cart Items ({cart.items.length} {cart.items.length === 1 ? 'product' : 'products'}, {cart.total_items} {cart.total_items === 1 ? 'item' : 'items'} total)
                    </Text>
                    <Badge appearance="tint" color="brand">
                      MongoDB Document Store
                    </Badge>
                  </div>
                }
              />
              <div style={{ padding: "0 16px 16px" }}>
                {cart.items.map((item) => (
                  <div
                    key={item.product_id}
                    style={{
                      display: "flex",
                      gap: "16px",
                      padding: "16px",
                      border: "1px solid #e1e1e1",
                      borderRadius: "8px",
                      marginBottom: "12px",
                    }}
                  >
                    <div
                      style={{
                        width: "80px",
                        height: "80px",
                        backgroundColor: "#f3f2f1",
                        borderRadius: "8px",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        overflow: "hidden",
                      }}
                    >
                      {item.product_image ? (
                        <img
                          src={item.product_image}
                          alt={item.product_name}
                          style={{
                            width: "100%",
                            height: "100%",
                            objectFit: "cover",
                          }}
                          onError={(e) => {
                            // Fallback to placeholder if image fails to load
                            e.currentTarget.style.display = "none";
                            e.currentTarget.parentElement!.innerHTML =
                              '<div style="color: #605e5c; font-size: 24px;">📦</div>';
                          }}
                        />
                      ) : (
                        <Cart24Regular style={{ color: "#605e5c" }} />
                      )}
                    </div>

                    <div style={{ flex: 1 }}>
                      <Text
                        size={500}
                        weight="semibold"
                        style={{ marginBottom: "4px", display: "block" }}
                      >
                        {item.product_name}
                      </Text>
                      <Text
                        size={400}
                        style={{
                          color: "#0078d4",
                          marginBottom: "8px",
                          display: "block",
                        }}
                      >
                        {formatPrice(item.unit_price)}
                      </Text>
                      <div
                        style={{
                          display: "flex",
                          gap: "12px",
                          alignItems: "center",
                        }}
                      >
                        <Text size={300} style={{ color: "#605e5c" }}>
                          Quantity: {item.quantity}
                        </Text>
                        <Text size={300} style={{ color: "#605e5c" }}>
                          Total: {formatPrice(item.total_price)}
                        </Text>
                      </div>
                    </div>

                    <div
                      style={{
                        display: "flex",
                        flexDirection: "column",
                        gap: "8px",
                      }}
                    >
                      <Button
                        appearance="secondary"
                        size="small"
                        onClick={() => loadProductReviews(item.product_id)}
                      >
                        View Reviews
                      </Button>
                      <Button
                        appearance="secondary"
                        size="small"
                        icon={<Delete24Regular />}
                        onClick={() => removeFromCart(item.product_id)}
                      >
                        Remove
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            {/* Product Reviews */}
            {selectedProductReviews && reviews.length > 0 && (
              <Card style={{ marginTop: "24px" }}>
                <CardHeader
                  header={
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                      }}
                    >
                      <Text size={600} weight="semibold">
                        Product Reviews
                      </Text>
                      <Badge appearance="tint" color="success">
                        Rich MongoDB Documents
                      </Badge>
                    </div>
                  }
                />
                <div style={{ padding: "0 16px 16px" }}>
                  {reviews.map((review) => (
                    <div key={review.id} className="review-card">
                      <div className="review-header">
                        <div
                          style={{
                            display: "flex",
                            alignItems: "center",
                            gap: "12px",
                          }}
                        >
                          <Avatar name={review.user_name} size={32} />
                          <div>
                            <Text className="review-author">
                              {review.user_name}
                            </Text>
                            <div
                              style={{
                                display: "flex",
                                alignItems: "center",
                                gap: "8px",
                              }}
                            >
                              <div style={{ display: "flex" }}>
                                {renderStars(review.rating)}
                              </div>
                              <Text size={300} style={{ color: "#605e5c" }}>
                                {review.rating}/5
                              </Text>
                              {review.verified_purchase && (
                                <Badge
                                  appearance="tint"
                                  color="success"
                                  size="small"
                                >
                                  Verified Purchase
                                </Badge>
                              )}
                            </div>
                          </div>
                        </div>
                        <Text className="review-date">
                          {new Date(review.created_at).toLocaleDateString()}
                        </Text>
                      </div>

                      <Text className="review-title">{review.title}</Text>
                      <Text className="review-content">{review.comment}</Text>

                      {review.pros.length > 0 && (
                        <div style={{ marginBottom: "8px" }}>
                          <Text
                            size={300}
                            weight="semibold"
                            style={{
                              color: "#107c10",
                              marginBottom: "4px",
                              display: "block",
                            }}
                          >
                            Pros:
                          </Text>
                          <ul style={{ margin: 0, paddingLeft: "16px" }}>
                            {review.pros.map((pro, index) => (
                              <li key={index}>
                                <Text size={300}>{pro}</Text>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {review.cons.length > 0 && (
                        <div style={{ marginBottom: "8px" }}>
                          <Text
                            size={300}
                            weight="semibold"
                            style={{
                              color: "#d13438",
                              marginBottom: "4px",
                              display: "block",
                            }}
                          >
                            Cons:
                          </Text>
                          <ul style={{ margin: 0, paddingLeft: "16px" }}>
                            {review.cons.map((con, index) => (
                              <li key={index}>
                                <Text size={300}>{con}</Text>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      <div className="review-actions">
                        <Badge appearance="tint" size="small">
                          {review.helpful_votes} helpful
                        </Badge>
                        <Badge appearance="tint" size="small">
                          Sentiment: {(review.sentiment_score * 100).toFixed(0)}
                          %
                        </Badge>
                        <Badge appearance="tint" size="small">
                          {review.device_used}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            )}
          </div>

          {/* Cart Summary */}
          <div>
            <Card>
              <CardHeader
                header={
                  <Text size={600} weight="semibold">
                    Order Summary
                  </Text>
                }
              />
              <div style={{ padding: "0 16px 16px" }}>
                <div style={{ marginBottom: "16px" }}>
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      marginBottom: "8px",
                    }}
                  >
                    <Text size={400}>Subtotal:</Text>
                    <Text size={400}>{formatPrice(cart.subtotal)}</Text>
                  </div>
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      marginBottom: "8px",
                    }}
                  >
                    <Text size={400}>Tax (estimated):</Text>
                    <Text size={400}>
                      {formatPrice(cart.estimated_total - cart.subtotal)}
                    </Text>
                  </div>
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      marginBottom: "16px",
                      paddingTop: "8px",
                      borderTop: "1px solid #e1e1e1",
                    }}
                  >
                    <Text size={500} weight="semibold">
                      Total:
                    </Text>
                    <Text
                      size={500}
                      weight="semibold"
                      style={{ color: "#0078d4" }}
                    >
                      {formatPrice(cart.estimated_total)}
                    </Text>
                  </div>
                </div>

                <Button
                  appearance="primary"
                  style={{ width: "100%", marginBottom: "12px" }}
                >
                  Proceed to Checkout
                </Button>
                <Button appearance="secondary" style={{ width: "100%" }}>
                  Continue Shopping
                </Button>
              </div>
            </Card>

            {/* MongoDB Features */}
            <Card style={{ marginTop: "16px" }}>
              <CardHeader
                header={
                  <Text size={500} weight="semibold">
                    MongoDB Features
                  </Text>
                }
              />
              <div style={{ padding: "0 16px 16px" }}>
                <Text
                  size={300}
                  style={{
                    color: "#605e5c",
                    marginBottom: "12px",
                    display: "block",
                  }}
                >
                  This cart demonstrates:
                </Text>
                <ul
                  style={{
                    margin: 0,
                    paddingLeft: "16px",
                    fontSize: "12px",
                    color: "#605e5c",
                  }}
                >
                  <li>Flexible cart item schemas</li>
                  <li>Nested review documents</li>
                  <li>Dynamic pricing calculations</li>
                  <li>Real-time updates</li>
                  <li>Rich metadata storage</li>
                </ul>
              </div>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
};

export default CartPage;
