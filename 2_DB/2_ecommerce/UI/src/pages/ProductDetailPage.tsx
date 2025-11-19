import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Text,
  Button,
  Card,
  CardHeader,
  Badge,
  Spinner,
} from '@fluentui/react-components';
import {
  ArrowLeft24Regular,
  Star24Filled,
  Star24Regular,
  Cart24Regular,
  Database24Regular,
  Target24Regular,
  Brain24Regular,
} from '@fluentui/react-icons';
import { mssqlService, mongoService, qdrantService } from '../services/api';
import { useApp } from '../components/AppProvider';
import type { Product, Review, SimilarProductsResponse } from '../types';

const ProductDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { state, setLoading, setError } = useApp();
  const [product, setProduct] = useState<Product | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loadingReviews, setLoadingReviews] = useState(false);
  const [similarProducts, setSimilarProducts] = useState<SimilarProductsResponse | null>(null);
  const [loadingSimilar, setLoadingSimilar] = useState(false);

  useEffect(() => {
    if (id) {
      loadProduct(parseInt(id));
      loadReviews(parseInt(id));
      loadSimilarProducts(parseInt(id));
    }
  }, [id]);

  const loadProduct = async (productId: number) => {
    setLoading(true);
    setError(null);
    
    try {
      const productData = await mssqlService.getProduct(productId);
      setProduct(productData);
    } catch (error) {
      console.error('Failed to load product:', error);
      setError('Failed to load product details');
    } finally {
      setLoading(false);
    }
  };

  const loadReviews = async (productId: number) => {
    setLoadingReviews(true);
    
    try {
      const reviewsData = await mongoService.getProductReviews(productId, 1, 5);
      setReviews(reviewsData);
    } catch (error) {
      console.error('Failed to load reviews:', error);
    } finally {
      setLoadingReviews(false);
    }
  };

  const loadSimilarProducts = async (productId: number) => {
    setLoadingSimilar(true);
    
    try {
      const similarData = await qdrantService.getSimilarProducts(productId, {
        limit: 6,
      });
      setSimilarProducts(similarData);
    } catch (error) {
      console.error('Failed to load similar products:', error);
      // Don't set global error for similar products failure
    } finally {
      setLoadingSimilar(false);
    }
  };

  const renderStars = (rating: number) => {
    const stars = [];
    for (let i = 1; i <= 5; i++) {
      stars.push(
        i <= rating ? (
          <Star24Filled key={i} style={{ color: '#ffb900', fontSize: '16px' }} />
        ) : (
          <Star24Regular key={i} style={{ color: '#d1d1d1', fontSize: '16px' }} />
        )
      );
    }
    return stars;
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(price);
  };

  const addToCart = async () => {
    if (!state.currentUser || !product) return;

    try {
      await mongoService.addToCart(state.currentUser.id, {
        product_id: product.id,
        quantity: 1,
      });
      // You could show a success message here or refresh cart state
      alert('Product added to cart!');
    } catch (error) {
      console.error('Failed to add to cart:', error);
      setError('Failed to add product to cart');
    }
  };

  if (state.loading) {
    return (
      <div className="loading-container">
        <Spinner size="large" label="Loading product..." />
      </div>
    );
  }

  if (state.error) {
    return (
      <div className="error-container">
        <Text size={500} style={{ color: '#d13438' }}>{state.error}</Text>
      </div>
    );
  }

  if (!product) {
    return (
      <div>
        <Text size={500}>Product not found</Text>
      </div>
    );
  }

  return (
    <div>
      {/* Back Button */}
      <div style={{ marginBottom: '24px' }}>
        <Link to="/products" style={{ textDecoration: 'none' }}>
          <Button
            appearance="secondary"
            icon={<ArrowLeft24Regular />}
            iconPosition="before"
          >
            Back to Products
          </Button>
        </Link>
      </div>

      {/* Product Details */}
      <div style={{ display: 'grid', gridTemplateColumns: '400px 1fr', gap: '32px', marginBottom: '32px' }}>
        {/* Product Image */}
        <Card>
          <div 
            style={{
              width: '100%',
              height: '400px',
              backgroundImage: product.main_image_url ? `url(${product.main_image_url})` : 'none',
              backgroundSize: 'cover',
              backgroundPosition: 'center',
              backgroundRepeat: 'no-repeat',
              backgroundColor: '#f3f2f1',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              borderRadius: '8px'
            }}
          >
            {!product.main_image_url && <Cart24Regular style={{ fontSize: '64px', color: '#605e5c' }} />}
          </div>
        </Card>

        {/* Product Info */}
        <div>
          <div style={{ marginBottom: '16px' }}>
            <Badge appearance="tint" color="brand" style={{ marginBottom: '8px' }}>
              {product.category}
            </Badge>
            <Text as="h1" size={900} weight="semibold" style={{ margin: '0 0 8px 0' }}>
              {product.name}
            </Text>
            <Text size={400} style={{ color: '#605e5c' }}>
              By {product.brand}
            </Text>
          </div>

          <div style={{ marginBottom: '24px' }}>
            <Text size={800} weight="bold" style={{ color: '#0078d4', marginBottom: '8px', display: 'block' }}>
              {formatPrice(product.price)}
            </Text>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
              <div style={{ display: 'flex' }}>
                {renderStars(Math.round(product.rating))}
              </div>
              <Text size={400}>
                {product.rating.toFixed(1)} ({product.review_count} reviews)
              </Text>
            </div>

            <Badge 
              appearance="tint" 
              color={product.stock_quantity > 0 ? 'success' : 'danger'}
              size="large"
            >
              {product.stock_quantity > 0 ? `${product.stock_quantity} in stock` : 'Out of stock'}
            </Badge>
          </div>

          <div style={{ marginBottom: '24px' }}>
            <Text size={500} weight="semibold" style={{ marginBottom: '8px', display: 'block' }}>
              Description
            </Text>
            <Text size={400} style={{ lineHeight: '1.5' }}>
              {product.description}
            </Text>
          </div>

          <div style={{ display: 'flex', gap: '12px' }}>
            <Button 
              appearance="primary" 
              size="large"
              icon={<Cart24Regular />}
              disabled={product.stock_quantity === 0 || !state.currentUser}
              onClick={addToCart}
            >
              Add to Cart
            </Button>
            {!state.currentUser && (
              <Text size={300} style={{ color: '#605e5c', alignSelf: 'center' }}>
                Sign in to add to cart
              </Text>
            )}
          </div>
        </div>
      </div>

      {/* Database Info Section */}
      <div className="database-section" style={{ marginBottom: '32px' }}>
        <div className="database-title">
          <Database24Regular />
          MSSQL Product Data
        </div>
        <div className="database-description">
          This product information is stored in Microsoft SQL Server, demonstrating relational data structures and referential integrity.
        </div>
        <ul className="feature-list">
          <li>Product catalog with consistent schema</li>
          <li>Inventory tracking with stock levels</li>
          <li>Pricing and financial data integrity</li>
          <li>Category relationships and constraints</li>
        </ul>
      </div>

      {/* Reviews Section */}
      <Card>
        <CardHeader
          header={
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <Text size={600} weight="semibold">Customer Reviews</Text>
              <Badge appearance="tint" color="success">MongoDB Documents</Badge>
            </div>
          }
        />
        <div style={{ padding: '0 16px 16px' }}>
          {loadingReviews ? (
            <div style={{ textAlign: 'center', padding: '20px' }}>
              <Spinner label="Loading reviews..." />
            </div>
          ) : reviews.length === 0 ? (
            <Text style={{ color: '#605e5c' }}>No reviews yet</Text>
          ) : (
            reviews.map((review) => (
              <div key={review.id} className="review-card">
                <div className="review-header">
                  <div>
                    <Text className="review-author">{review.user_name}</Text>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <div style={{ display: 'flex' }}>
                        {renderStars(review.rating)}
                      </div>
                      <Text size={300}>
                        {review.rating}/5
                      </Text>
                      {review.verified_purchase && (
                        <Badge appearance="tint" color="success" size="small">
                          Verified Purchase
                        </Badge>
                      )}
                    </div>
                  </div>
                  <Text className="review-date">
                    {new Date(review.created_at).toLocaleDateString()}
                  </Text>
                </div>
                
                <Text className="review-title">{review.title}</Text>
                <Text className="review-content">{review.comment}</Text>
                
                {review.pros.length > 0 && (
                  <div style={{ marginBottom: '8px' }}>
                    <Text size={300} weight="semibold" style={{ color: '#107c10', marginBottom: '4px', display: 'block' }}>
                      Pros:
                    </Text>
                    <ul style={{ margin: 0, paddingLeft: '16px' }}>
                      {review.pros.map((pro, index) => (
                        <li key={index}>
                          <Text size={300}>{pro}</Text>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {review.cons.length > 0 && (
                  <div style={{ marginBottom: '8px' }}>
                    <Text size={300} weight="semibold" style={{ color: '#d13438', marginBottom: '4px', display: 'block' }}>
                      Cons:
                    </Text>
                    <ul style={{ margin: 0, paddingLeft: '16px' }}>
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
                    Sentiment: {(review.sentiment_score * 100).toFixed(0)}%
                  </Badge>
                  <Badge appearance="tint" size="small">
                    {review.device_used}
                  </Badge>
                </div>
              </div>
            ))
          )}
        </div>
      </Card>

      {/* Similar Products Section */}
      <Card style={{ marginTop: '32px' }}>
        <CardHeader
          header={
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <Brain24Regular style={{ color: '#dc382d' }} />
              <Text size={600} weight="semibold">Similar Products</Text>
              <Badge appearance="tint" color="danger">Qdrant AI</Badge>
            </div>
          }
        />
        <div style={{ padding: '0 16px 16px' }}>
          {loadingSimilar ? (
            <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}>
              <Spinner size="medium" label="Finding similar products..." />
            </div>
          ) : similarProducts && similarProducts.similar_products.length > 0 ? (
            <>
              <Text size={400} style={{ color: '#605e5c', marginBottom: '16px', display: 'block' }}>
                AI-powered recommendations based on product features and user behavior
              </Text>
              <div className="product-grid" style={{ 
                display: 'grid', 
                gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', 
                gap: '16px' 
              }}>
                {similarProducts.similar_products.map((similarProduct, index) => (
                  <Card key={similarProduct.id} style={{ cursor: 'pointer' }}>
                    <Link to={`/products/${similarProduct.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                      <div style={{ position: 'relative' }}>
                        <div style={{ 
                          height: '120px', 
                          backgroundColor: '#f3f2f1', 
                          display: 'flex', 
                          alignItems: 'center', 
                          justifyContent: 'center',
                          marginBottom: '8px'
                        }}>
                          {similarProduct.thumbnail_url ? (
                            <img
                              src={similarProduct.thumbnail_url}
                              alt={similarProduct.name}
                              style={{
                                width: '100%',
                                height: '100%',
                                objectFit: 'cover'
                              }}
                              onError={(e) => {
                                e.currentTarget.style.display = 'none';
                                e.currentTarget.parentElement!.innerHTML = '<div style="color: #605e5c; font-size: 24px;">🎯</div>';
                              }}
                            />
                          ) : (
                            <Target24Regular style={{ fontSize: '32px', color: '#605e5c' }} />
                          )}
                        </div>
                        <Badge 
                          appearance="tint" 
                          color="success" 
                          size="small"
                          style={{ 
                            position: 'absolute', 
                            top: '4px', 
                            right: '4px',
                            backgroundColor: 'rgba(255, 255, 255, 0.9)'
                          }}
                        >
                          {(similarProducts.similarity_scores[index] * 100).toFixed(0)}% match
                        </Badge>
                      </div>
                      <div style={{ padding: '8px' }}>
                        <Text size={300} weight="semibold" style={{ 
                          marginBottom: '4px', 
                          display: 'block',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap'
                        }}>
                          {similarProduct.name}
                        </Text>
                        
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                          <Badge appearance="tint" color="brand" size="small">
                            {similarProduct.category}
                          </Badge>
                          <Text size={300} weight="semibold" style={{ color: '#0078d4' }}>
                            {formatPrice(similarProduct.price)}
                          </Text>
                        </div>

                        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '4px' }}>
                          {renderStars(similarProduct.rating)}
                          <Text size={200} style={{ color: '#605e5c' }}>
                            ({similarProduct.review_count})
                          </Text>
                        </div>

                        <Badge 
                          appearance="tint" 
                          color={similarProduct.in_stock ? 'success' : 'danger'}
                          size="small"
                        >
                          {similarProduct.in_stock ? 'In Stock' : 'Out of Stock'}
                        </Badge>
                      </div>
                    </Link>
                  </Card>
                ))}
              </div>
            </>
          ) : (
            <div style={{ textAlign: 'center', padding: '40px', color: '#605e5c' }}>
              <Brain24Regular style={{ fontSize: '48px', marginBottom: '16px' }} />
              <Text size={400}>No similar products found</Text>
              <Text size={300} style={{ marginTop: '8px', display: 'block' }}>
                Our AI is still learning about this product
              </Text>
            </div>
          )}

          <div style={{ marginTop: '16px', padding: '12px', backgroundColor: '#f9f9f9', borderRadius: '6px' }}>
            <Text size={300} weight="semibold" style={{ color: '#605e5c', marginBottom: '4px', display: 'block' }}>
              AI Similarity Matching:
            </Text>
            <Text size={300} style={{ color: '#605e5c' }}>
              • <strong>Vector Embeddings</strong>: Product features converted to 384-dimensional vectors<br/>
              • <strong>Cosine Similarity</strong>: Mathematical similarity scoring between product features<br/>
              • <strong>Real-time Recommendations</strong>: Instant AI-powered product matching
            </Text>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default ProductDetailPage;