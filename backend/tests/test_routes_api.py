import io
import os
import json
from app.models import Product, PriceHistory


class TestProductRoutes:
    """Test suite for product API endpoints"""

    def test_add_product(self, client, db_session):
        """Test adding a new product"""
        response = client.post(
            "/api/products",
            data={
                "name": "Test Product",
                "category": "Electronics",
                "target_price": "100.0",
                "current_price": "150.0",
            },
            content_type="multipart/form-data",
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["name"] == "Test Product"
        assert data["target_price"] == 100.0
        assert data["current_price"] == 150.0
        assert data["target_reached"] == False  # 150 > 100

    def test_add_product_missing_fields(self, client, db_session):
        """Test adding product without required fields"""
        response = client.post(
            "/api/products",
            data={"name": "No Price"},
            content_type="multipart/form-data",
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_get_products(self, client, db_session):
        """Test getting all products"""
        # Add test products
        product1 = Product(
            name="iPhone 15",
            category="Electronics",
            target_price=800,
            current_price=999,
        )
        db_session.add(product1)
        db_session.commit()

        product2 = Product(
            name="MacBook Pro",
            category="Computers",
            target_price=1500,
            current_price=2499,
        )
        db_session.add(product2)
        db_session.commit()

        response = client.get("/api/products")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 2
        assert [p["name"] for p in data] == ["MacBook Pro", "iPhone 15"]

    def test_add_product_creates_initial_history(self, client, db_session):
        """A new product must start with exactly one history record
        holding its initial price (regression test)."""
        response = client.post(
            "/api/products",
            data={
                "name": "History Product",
                "target_price": "100.0",
                "current_price": "150.0",
            },
            content_type="multipart/form-data",
        )
        created = json.loads(response.data)

        data = json.loads(client.get(f"/api/products/{created['id']}").data)

        assert len(data["price_history"]) == 1
        assert data["price_history"][0]["price"] == 150.0

    def test_add_product_missing_fields_creates_no_history(self, client, db_session):
        """A rejected request must not leave orphan history rows behind."""
        response = client.post(
            "/api/products",
            data={"name": "No Price"},
            content_type="multipart/form-data",
        )

        assert response.status_code == 400
        assert db_session.query(PriceHistory).count() == 0

    def test_get_product_with_history(self, client, db_session):
        """Test getting a product with price history"""
        product = Product(
            name="Sony WH-1000XM5",
            category="Audio",
            target_price=250,
            current_price=399,
        )
        db_session.add(product)
        db_session.flush()

        # Add price history records
        history1 = PriceHistory(product_id=product.id, price=399)
        history2 = PriceHistory(product_id=product.id, price=380)
        history3 = PriceHistory(product_id=product.id, price=350)

        db_session.add_all([history1, history2, history3])
        db_session.commit()

        response = client.get(f"/api/products/{product.id}")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["name"] == "Sony WH-1000XM5"
        assert len(data["price_history"]) == 3
        assert data["price_history"][0]["price"] == 399

    def test_get_product_not_found(self, client):
        """Test getting a non-existent product"""
        response = client.get("/api/products/999")

        assert response.status_code == 404

    def test_delete_product(self, client, db_session):
        """Test deleting a product"""
        product = Product(
            name="Test Delete", category="Test", target_price=50, current_price=100
        )
        db_session.add(product)
        db_session.commit()
        product_id = product.id

        response = client.delete(f"/api/products/{product_id}")

        assert response.status_code == 200

        # Verify it's deleted
        deleted_product = db_session.get(Product, product_id)
        assert deleted_product is None

    def test_delete_product_not_found(self, client):
        """Test deleting a non-existent product"""
        response = client.delete("/api/products/999")

        assert response.status_code == 404

    def test_add_product_with_image(self, client, db_session):
        response = client.post(
            "/api/products",
            data={
                "name": "With Image",
                "target_price": "100",
                "current_price": "150",
                "image": (io.BytesIO(b"fake"), "pic.png"),
            },
            content_type="multipart/form-data",
        )

        assert response.status_code == 201
        assert response.json["image_url"].startswith("/api/uploads/")

    def test_add_product_rejects_bad_image_extension(self, client, db_session):
        response = client.post(
            "/api/products",
            data={
                "name": "Bad Image",
                "target_price": "100",
                "current_price": "150",
                "image": (io.BytesIO(b"x"), "evil.exe"),
            },
            content_type="multipart/form-data",
        )

        assert response.status_code == 400
        assert db_session.query(Product).count() == 0

    def test_add_product_invalid_price(self, client, db_session):
        response = client.post(
            "/api/products",
            data={"name": "X", "target_price": "abc", "current_price": "150"},
            content_type="multipart/form-data",
        )

        assert response.status_code == 400

    def test_delete_product_removes_image_file(self, client, db_session):
        created = client.post(
            "/api/products",
            data={
                "name": "Delete Image",
                "target_price": "100",
                "current_price": "150",
                "image": (io.BytesIO(b"fake"), "pic.png"),
            },
            content_type="multipart/form-data",
        ).json

        assert client.get(created["image_url"]).status_code == 200

        client.delete(f"/api/products/{created['id']}")

        assert client.get(created["image_url"]).status_code == 404

    def test_delete_product_when_image_file_missing(self, client, db_session):
        """Deleting must succeed even if the image file is already gone."""
        created = client.post(
            "/api/products",
            data={
                "name": "Missing Image",
                "target_price": "100",
                "current_price": "150",
                "image": (io.BytesIO(b"fake"), "pic.png"),
            },
            content_type="multipart/form-data",
        ).json

        # remove the file manually, behind the app's back
        filename = os.path.basename(created["image_url"])
        os.remove(os.path.join(os.environ["UPLOAD_FOLDER"], filename))

        response = client.delete(f"/api/products/{created['id']}")

        assert response.status_code == 200
        assert db_session.get(Product, created["id"]) is None

    def test_uploaded_image_can_be_fetched(self, client, db_session):
        created = client.post(
            "/api/products",
            data={
                "name": "Fetch Image",
                "target_price": "100",
                "current_price": "150",
                "image": (io.BytesIO(b"fake"), "pic.png"),
            },
            content_type="multipart/form-data",
        ).json

        response = client.get(created["image_url"])

        assert response.status_code == 200
        assert response.data == b"fake"
