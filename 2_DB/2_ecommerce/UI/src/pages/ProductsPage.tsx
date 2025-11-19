import {
  Badge,
  Button,
  Card,
  CardHeader,
  Dropdown,
  Field,
  Input,
  Option,
  Spinner,
  Text,
} from "@fluentui/react-components";
import {
  Database24Regular,
  Filter24Regular,
  Search24Regular,
  ShoppingBag24Regular,
  Star24Filled,
  Star24Regular,
} from "@fluentui/react-icons";
import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useApp } from "../components/AppProvider";
import { mssqlService } from "../services/api";
import type { Product, PaginationInfo } from "../types";

const ProductsPage: React.FC = () => {
  const { state, setLoading, setError } = useApp();
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [currentPage, setCurrentPage] = useState(1);
  const [pagination, setPagination] = useState<PaginationInfo | null>(null);
  const [priceFilter, setPriceFilter] = useState("all");
  const [searchTerm, setSearchTerm] = useState("");
  const pageSize = 20;

  const handlePageChange = (newPage: number) => {
    setCurrentPage(newPage);
  };

  const resetToFirstPage = () => {
    setCurrentPage(1);
  };

  // Reset to page 1 when filters change
  useEffect(() => {
    resetToFirstPage();
  }, [selectedCategory, priceFilter, searchTerm]);

  useEffect(() => {
    loadCategories();
  }, []);

  useEffect(() => {
    loadProducts();
  }, [selectedCategory, currentPage, priceFilter, searchTerm]);

  const loadCategories = async () => {
    try {
      const categoriesData = await mssqlService.getCategories();
      setCategories(categoriesData);
    } catch (error) {
      console.error("Failed to load categories:", error);
      setError("Failed to load categories");
    }
  };

  const loadProducts = async () => {
    setLoading(true);
    setError(null);

    try {
      const category =
        selectedCategory === "all" ? undefined : selectedCategory;
      const response = await mssqlService.getProducts(
        currentPage,
        pageSize,
        category
      );

      const productsData = response.products || [];
      setPagination(response.pagination);

      let filteredProducts = Array.isArray(productsData) ? productsData : [];

      // Apply search filter
      if (searchTerm) {
        filteredProducts = filteredProducts.filter(
          (product) =>
            product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            product.description
              .toLowerCase()
              .includes(searchTerm.toLowerCase()) ||
            product.brand.toLowerCase().includes(searchTerm.toLowerCase())
        );
      }

      // Apply price filter
      if (priceFilter !== "all") {
        switch (priceFilter) {
          case "under50":
            filteredProducts = filteredProducts.filter((p) => p.price < 50);
            break;
          case "50to100":
            filteredProducts = filteredProducts.filter(
              (p) => p.price >= 50 && p.price <= 100
            );
            break;
          case "100to250":
            filteredProducts = filteredProducts.filter(
              (p) => p.price > 100 && p.price <= 250
            );
            break;
          case "over250":
            filteredProducts = filteredProducts.filter((p) => p.price > 250);
            break;
        }
      }

      setProducts(filteredProducts);
    } catch (error) {
      console.error("Failed to load products:", error);
      setError("Failed to load products");
    } finally {
      setLoading(false);
    }
  };

  const renderStars = (rating: number) => {
    const stars = [];
    for (let i = 1; i <= 5; i++) {
      stars.push(
        i <= rating ? (
          <Star24Filled key={i} style={{ color: "#ffb900" }} />
        ) : (
          <Star24Regular key={i} style={{ color: "#d1d1d1" }} />
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

  const totalPages = pagination?.total_pages || 1;
  const totalProducts = pagination?.total_items || 0;

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
          <Database24Regular style={{ fontSize: "32px", color: "#0078d4" }} />
          <div>
            <Text as="h1" size={800} weight="semibold">
              Product Catalog
            </Text>
            <Text size={400} style={{ color: "#605e5c" }}>
              Powered by Microsoft SQL Server - Demonstrating relational data,
              complex queries, and ACID transactions
            </Text>
          </div>
        </div>

        <div className="database-section">
          <div className="database-title">
            <Database24Regular />
            MSSQL Features Demonstrated
          </div>
          <div className="database-description">
            This page showcases SQL Server's strengths in handling structured
            product data with complex relationships and queries.
          </div>
          <ul className="feature-list">
            <li>
              Complex JOIN operations between products, categories, and
              inventory
            </li>
            <li>ACID transactions for order processing</li>
            <li>Advanced filtering and pagination</li>
            <li>Aggregated data (ratings, review counts, stock levels)</li>
            <li>Foreign key relationships and referential integrity</li>
          </ul>
        </div>
      </div>

      {/* Filters */}
      <Card style={{ marginBottom: "24px" }}>
        <CardHeader
          header={
            <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
              <Filter24Regular />
              <Text size={500} weight="semibold">
                Filters
              </Text>
            </div>
          }
        />
        <div style={{ padding: "0 16px 16px" }}>
          <div className="search-filters">
            <Field label="Search Products">
              <Input
                placeholder="Search by name, description, or brand..."
                value={searchTerm}
                onChange={(_, data) => setSearchTerm(data.value)}
                contentBefore={<Search24Regular />}
                style={{ minWidth: "250px" }}
              />
            </Field>

            <Field label="Category">
              <Dropdown
                placeholder="All Categories"
                value={
                  selectedCategory === "all"
                    ? "All Categories"
                    : selectedCategory
                }
                onOptionSelect={(_, data) =>
                  setSelectedCategory(data.optionValue || "all")
                }
              >
                <Option value="all">All Categories</Option>
                {categories.map((category) => (
                  <Option key={category} value={category}>
                    {category}
                  </Option>
                ))}
              </Dropdown>
            </Field>

            <Field label="Price Range">
              <Dropdown
                placeholder="All Prices"
                value={priceFilter === "all" ? "All Prices" : priceFilter}
                onOptionSelect={(_, data) =>
                  setPriceFilter(data.optionValue || "all")
                }
              >
                <Option value="all">All Prices</Option>
                <Option value="under50">Under $50</Option>
                <Option value="50to100">$50 - $100</Option>
                <Option value="100to250">$100 - $250</Option>
                <Option value="over250">Over $250</Option>
              </Dropdown>
            </Field>

            <Button
              appearance="secondary"
              onClick={() => {
                setSelectedCategory("all");
                setPriceFilter("all");
                setSearchTerm("");
                setCurrentPage(1);
              }}
            >
              Clear Filters
            </Button>
          </div>
        </div>
      </Card>

      {/* Products Grid */}
      {state.loading ? (
        <div className="loading-container">
          <Spinner size="large" label="Loading products..." />
        </div>
      ) : state.error ? (
        <div className="error-container">
          <Text size={500} style={{ color: "#d13438" }}>
            {state.error}
          </Text>
        </div>
      ) : (
        <>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "16px",
            }}
          >
            <Text size={400} style={{ color: "#605e5c" }}>
              Showing {products.length} of {totalProducts} products
            </Text>
            <Text size={300} style={{ color: "#605e5c" }}>
              Page {currentPage} of {totalPages}
            </Text>
          </div>

          <div className="product-grid">
            {products.map((product) => (
              <Card key={product.id} className="product-card">
                <div
                  className="product-image"
                  style={{
                    backgroundImage: product.thumbnail_url
                      ? `url(${product.thumbnail_url})`
                      : "none",
                    backgroundSize: "cover",
                    backgroundPosition: "center",
                    backgroundRepeat: "no-repeat",
                  }}
                >
                  {!product.thumbnail_url && <ShoppingBag24Regular />}
                </div>
                <div className="product-info">
                  <Text className="product-name">{product.name}</Text>
                  <Text className="product-description">
                    {product.description}
                  </Text>

                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      marginBottom: "8px",
                    }}
                  >
                    <Badge appearance="tint" color="brand">
                      {product.category}
                    </Badge>
                    <Text size={300} style={{ color: "#605e5c" }}>
                      {product.brand}
                    </Text>
                  </div>

                  <Text className="product-price">
                    {formatPrice(product.price)}
                  </Text>

                  <div className="product-rating">
                    <div style={{ display: "flex" }}>
                      {renderStars(Math.round(product.rating))}
                    </div>
                    <Text size={300}>
                      {product.rating.toFixed(1)} ({product.review_count}{" "}
                      reviews)
                    </Text>
                  </div>

                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      marginTop: "12px",
                    }}
                  >
                    <Badge
                      appearance="tint"
                      color={product.stock_quantity > 0 ? "success" : "danger"}
                    >
                      {product.stock_quantity > 0
                        ? `${product.stock_quantity} in stock`
                        : "Out of stock"}
                    </Badge>
                    <Link
                      to={`/products/${product.id}`}
                      style={{ textDecoration: "none" }}
                    >
                      <Button appearance="primary" size="small">
                        View Details
                      </Button>
                    </Link>
                  </div>
                </div>
              </Card>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="pagination-container">
              <div
                style={{ display: "flex", gap: "8px", alignItems: "center" }}
              >
                <Button
                  appearance="secondary"
                  disabled={!pagination?.has_previous}
                  onClick={() => handlePageChange(currentPage - 1)}
                >
                  Previous
                </Button>

                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  const page = i + 1;
                  return (
                    <Button
                      key={page}
                      appearance={
                        currentPage === page ? "primary" : "secondary"
                      }
                      onClick={() => handlePageChange(page)}
                    >
                      {page}
                    </Button>
                  );
                })}

                {totalPages > 5 && currentPage < totalPages - 2 && (
                  <>
                    <Text>...</Text>
                    <Button
                      appearance="secondary"
                      onClick={() => handlePageChange(totalPages)}
                    >
                      {totalPages}
                    </Button>
                  </>
                )}

                <Button
                  appearance="secondary"
                  disabled={!pagination?.has_next}
                  onClick={() => handlePageChange(currentPage + 1)}
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default ProductsPage;
