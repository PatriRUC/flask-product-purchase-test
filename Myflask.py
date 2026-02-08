from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import os

import os

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "your_user"),
    "password": os.getenv("DB_PASSWORD", "your_password"),
    "database": os.getenv("DB_NAME", "your_db"),
    "cursorclass": pymysql.cursors.DictCursor 
}


app = Flask(__name__)
CORS(app)

# ===== 数据库配置 =====
'''
DB_CONFIG = {
    "host": "database-1.cpqi0aygkde7.us-west-1.rds.amazonaws.com",
    "user": "admin",
    "password": "pjg020424",
    "database": "testdb",
    "cursorclass": pymysql.cursors.DictCursor
}
'''
def get_db_connection():
    return pymysql.connect(**DB_CONFIG)

# ===== 查询产品接口 =====
@app.route("/product", methods=["GET"])
def get_product():
    name = request.args.get("name", "")

    if not name:
        return jsonify({"error": "name is required"}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT id, name, price, quantity FROM product WHERE name = %s"
            cursor.execute(sql, (name,))
            result = cursor.fetchone()
    finally:
        conn.close()

    if not result:
        return jsonify({"error": "product not found"}), 404

    return jsonify(result)


# ================== 购买接口 ==================
@app.route("/purchase", methods=["POST"])
def purchase_product():
    data = request.get_json()

    product_id = data.get("product_id")
    buy_quantity = data.get("quantity")

    # -------- 参数校验（你刚刚发现 bug 的地方）--------
    if product_id is None or buy_quantity is None:
        return jsonify({"error": "product_id and quantity are required"}), 400

    if not isinstance(buy_quantity, int):
        return jsonify({"error": "quantity must be an integer"}), 400

    if buy_quantity <= 0 or buy_quantity > 5:
        return jsonify({"error": "quantity must be integer between 1 and 5"}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # -------- 核心：原子更新 --------
            sql = """
                UPDATE product
                SET quantity = quantity - %s
                WHERE id = %s AND quantity >= %s
            """
            affected_rows = cursor.execute(
                sql, (buy_quantity, product_id, buy_quantity)
            )

            if affected_rows == 0:
                # 没更新成功，说明：
                # 1) product 不存在
                # 2) 或库存不足
                cursor.execute(
                    "SELECT quantity FROM product WHERE id = %s",
                    (product_id,)
                )
                product = cursor.fetchone()

                if not product:
                    return jsonify({"error": "product not found"}), 404

                return jsonify({
                    "error": "not enough stock",
                    "current_stock": product["quantity"]
                }), 400

            conn.commit()

            # 查询剩余库存（可选，但对前端友好）
            cursor.execute(
                "SELECT quantity FROM product WHERE id = %s",
                (product_id,)
            )
            new_stock = cursor.fetchone()["quantity"]

    finally:
        conn.close()
        a = 1

    return jsonify({
        "message": "purchase success",
        "remaining_stock": new_stock
    }), 200



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
