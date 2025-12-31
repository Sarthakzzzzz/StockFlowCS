from flask import Flask, request, jsonify
import sqlalchemy
import os
app = Flask(__name__)
DATABASE_URI = os.environ.get(
    'DATABASE_URL', 'postgresql+psycopg2://postgres:<user_password>@localhost:5432/inventory_db')

# used sqlalchemy to execute query using postgresql database its ordbms and sqlalchemy is orm for python
engine = sqlalchemy.create_engine(DATABASE_URI)


@app.route('/api/companies/<int:company_id>/alerts/low-stock', methods=['GET'])
def get_low_stock(company_id):
    # connect to the database using the engine
    with engine.connect() as connection:
        # --- SQL Query for Low Stock Products ---
        # This query joins the inventory, product, warehouse, and supplier tables
        # to gather all necessary information for the low stock alerts.
        # just check if current_sstock is less than or equal to threshold this will give low stock products
        # after that return the result by taking length of alerts
        query = """
        SELECT 
            p.id AS product_id,
            p.name AS product_name,
            p.sku,
            w.id AS warehouse_id,
            w.name AS warehouse_name,
            i.quantity AS current_stock,
            i.threshold,
            -- Build a JSON object for supplier details to nest the information.
            json_build_object(
                'id', s.id,
                'name', s.name,
                'contact_email', s.contact_email
            ) AS supplier
        FROM inventory i
        JOIN product p ON i.product_id = p.id
        JOIN warehouse w ON i.warehouse_id = w.id
        JOIN supplier s ON p.supplier_id = s.id
        WHERE w.company_id = :company_id AND i.quantity <= i.threshold
        """
        result = connection.execute(sqlalchemy.text(query), {
                                    "company_id": company_id})

        alerts = [dict(row._mapping) for row in result]

        return jsonify({'alerts': alerts, 'total_alerts': len(alerts)}), 200


if __name__ == '__main__':
    app.run(debug=True)
