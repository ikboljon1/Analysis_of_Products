import pandas as pd
import json

with open('data.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

df = pd.DataFrame(data)

# Etkazib berish narxini lug'atga qo'shish
delivery_costs = {
    'Мордор': 1000,
    'хутор близ Диканьки': 500,
    'отель Лето': 800,
    'гиперборея': 1200,
    'остров невезения': 300
}

df['delivery_cost'] = df['warehouse_name'].map(delivery_costs)

products_list = []
for order in data:
    for product in order["products"]:
        product_data = {
            "order_id": order["order_id"],
            "product": product["product"],
            "quantity": product["quantity"],
            "income": product["price"] * product["quantity"],
            "expenses": abs(order["highway_cost"] + df.loc[df["order_id"] == order["order_id"], "delivery_cost"].values[0]),
            "profit": product["price"] * product["quantity"] + order["highway_cost"] + df.loc[df["order_id"] == order["order_id"], "delivery_cost"].values[0],
        }
        products_list.append(product_data)

products_df = pd.DataFrame(products_list)
print(products_df)

orders_profit_df = pd.DataFrame(df[["order_id"]])
orders_profit_df["order_profit"] = products_df.groupby("order_id")["profit"].sum()
average_profit = orders_profit_df["order_profit"].mean()

print(orders_profit_df)
print("Средняя прибыль заказов:", average_profit)

warehouse_products_df = products_df.groupby([df["warehouse_name"], "product"]).agg(
    quantity=("quantity", "sum"),
    profit=("profit", "sum"),
)
total_profit_by_warehouse = warehouse_products_df.groupby("warehouse_name")[
    "profit"
].transform("sum")
warehouse_products_df["percent_profit_product_of_warehouse"] = (
    warehouse_products_df["profit"] / total_profit_by_warehouse * 100
)
print(warehouse_products_df.reset_index())

sorted_warehouse_products_df = warehouse_products_df.sort_values(
    by="percent_profit_product_of_warehouse", ascending=False
)
sorted_warehouse_products_df["accumulated_percent_profit_product_of_warehouse"] = (
    sorted_warehouse_products_df["percent_profit_product_of_warehouse"].cumsum()
)
print(sorted_warehouse_products_df.reset_index())

def assign_category(accumulated_percent):
    if accumulated_percent <= 70:
        return "A"
    elif 70 < accumulated_percent <= 90:
        return "B"
    else:
        return "C"

sorted_warehouse_products_df["category"] = sorted_warehouse_products_df[
    "accumulated_percent_profit_product_of_warehouse"
].apply(assign_category)
print(sorted_warehouse_products_df.reset_index())
