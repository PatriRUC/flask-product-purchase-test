import threading
import pymysql
from Myflask import app   # 你的 Flask app
import os

def get_stock(product_id):
    conn = pymysql.connect(
        host="database-1.cpqi0aygkde7.us-west-1.rds.amazonaws.com",
        user="admin",
        password="pjg020424",
        database="testdb",
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT quantity FROM product WHERE id = %s",
                (product_id,)
            )
            return cursor.fetchone()["quantity"]
    finally:
        conn.close()


def purchase(product_id, quantity, results, index):
    """
    每个线程自己创建 client
    """
    with app.test_client() as client:
        resp = client.post(
            "/purchase",
            json={
                "product_id": product_id,
                "quantity": quantity
            }
        )
        results[index] = resp.status_code


def set_stock(product_id, quantity):
    conn = pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE product SET quantity = %s WHERE id = %s",
                (quantity, product_id)
            )
            conn.commit()
    finally:
        conn.close()

def test_concurrent_purchase():
    product_id = 100
    buy_quantity = 3
    set_stock(product_id, 5)

    before_stock = get_stock(product_id)

    results = [None, None]

    t1 = threading.Thread(
        target=purchase,
        args=(product_id, buy_quantity, results, 0)
    )
    t2 = threading.Thread(
        target=purchase,
        args=(product_id, buy_quantity, results, 1)
    )


    t1.start()
    t2.start()
    t1.join()
    t2.join()

    success_count = results.count(200)
    after_stock = get_stock(product_id)

    assert success_count == 1
    assert after_stock == before_stock - buy_quantity
