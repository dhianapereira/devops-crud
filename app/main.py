import os
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from app.models import db, Item

def create_app():
    app = Flask(__name__)

    # Load environment variables for DB connection
    db_user = os.environ.get("DB_USER")
    db_password = os.environ.get("DB_PASSWORD")
    db_host = os.environ.get("DB_HOST", "db")
    db_port = os.environ.get("DB_PORT", "5432")
    db_name = os.environ.get("DB_NAME")

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    Migrate(app, db)

    @app.route("/health", methods=["GET"])
    def health():
        """Simple health check endpoint."""
        return {"status": "ok"}, 200

    # === CRUD ROUTES ===

    @app.route("/items", methods=["POST"])
    def create_item():
        """Create a new item."""
        data = request.get_json()
        name = data.get("name")
        description = data.get("description")

        if not name:
            return {"error": "name is required"}, 400

        item = Item(name=name, description=description)
        db.session.add(item)
        db.session.commit()

        return {
            "id": item.id,
            "name": item.name,
            "description": item.description,
        }, 201

    @app.route("/items", methods=["GET"])
    def list_items():
        """List all items."""
        items = Item.query.all()
        return jsonify(
            [
                {"id": i.id, "name": i.name, "description": i.description}
                for i in items
            ]
        )

    @app.route("/items/<int:item_id>", methods=["GET"])
    def get_item(item_id):
        """Get an item by ID."""
        item = Item.query.get_or_404(item_id)
        return {"id": item.id, "name": item.name, "description": item.description}

    @app.route("/items/<int:item_id>", methods=["PUT", "PATCH"])
    def update_item(item_id):
        """Update an existing item."""
        item = Item.query.get_or_404(item_id)
        data = request.get_json() or {}
        item.name = data.get("name", item.name)
        item.description = data.get("description", item.description)
        db.session.commit()
        return {
            "id": item.id,
            "name": item.name,
            "description": item.description,
        }

    @app.route("/items/<int:item_id>", methods=["DELETE"])
    def delete_item(item_id):
        """Delete an item."""
        item = Item.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return {"message": "item deleted"}, 200

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000)