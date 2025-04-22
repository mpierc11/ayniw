import streamlit as st
import pandas as pd
import math
from datetime import datetime, timedelta


import streamlit as st

# Simple password protection
password = st.text_input("Enter the password", type="password")
if password != "eoq":
    st.error("Incorrect password")
    st.stop()  # Stop the app if password is wrong


# Custom CSS for the header background and text styling
# Create a centered layout with st.columns
col1, col2, col3 = st.columns([1, 2, 1])

with col2:  # Center column
    #st.image('logo-wine-glasses.png', use_container_width=True)
    st.image('logo-wine-glasses.png')
# st.image('logo-wine-glasses.png', width=150)
st.markdown(
    """
    <style>
        .header-container {
            text-align: center;
            font-size: 40px;
            font-weight: bold;
            font-family: 'Pacifico', cursive;
            padding: 30px;
            background: linear-gradient(to bottom, lightblue 10%, lightyellow 75%, rgba(240, 128, 128, 0.8) 100%);
        }
        .header-text {
            color: #8B0000;
            padding: 10px;
        }
        @import url('https://fonts.googleapis.com/css2?family=Pacifico&display=swap');
    </style>
    <div class="header-container">
        <div class="header-text">All You Need is Wine</div>
    </div>
    """,
    unsafe_allow_html=True
)

# Load the Excel file (backend)
def load_data():
    file_path = "AYNIW.xlsx"
    return pd.read_excel(file_path, sheet_name="Model")

# Load the DRP data
data = load_data()


# Streamlit app starts here
st.title("EOQ & Reorder Point Dashboard")
st.subheader("Determine the optimal order quantity and reorder point.")
st.write("Find the current inventory on Amazon Seller Central via Inventory>FBA Inventory. It is the on-hand quantity.")

# User inputs
selected_date = st.date_input("Select a Date for Inventory Projection", datetime.today())
inventory_on_hand = st.number_input("Enter Current Inventory (units)", min_value=0, step=1)

# Find the closest month in the dataset for forecasting
selected_month = selected_date.strftime("%B")  # Extracts month name (e.g., "January")

# Filter data for the selected month
selected_data = data[data["Month"] == selected_month]

if not selected_data.empty:
    # Extract values from the dataset
    forecasted_sales = round(selected_data["Forecasted Sales"].values[0])  # Ensure integer
    safety_stock = int(selected_data["Safety Stock"].values[0])  # Ensure integer
    reorder_level = int(selected_data["Reorder Level"].values[0])  # Ensure integer
    order_quantity = int(selected_data["Order Quantity"].values[0])  # Ensure integer
    lead_time = selected_data["Lead Time"].values[0]  # Lead time isn't rounded to integer since it's a duration

    # Check if reorder is needed
    if inventory_on_hand <= reorder_level:
         # Calculate adjusted EOQ to be a multiple of 6
        adjusted_eoq = ((order_quantity + 5) // 6) * 6  # Round up to nearest multiple of 6
        st.warning(f"Reorder Needed! Suggested Order Quantity (EOQ): **{order_quantity} units.**")
        st.info(f"Since the product comes in boxes of 6, the adjusted EOQ is: **{adjusted_eoq} units, or {int(adjusted_eoq/6)} cartons.**")
    else:
        st.success("No Reorder Needed. Inventory is sufficient.")

    # Calculate Ending Inventory dynamically
    predicted_ending_inventory = (
        #  inventory_on_hand - forecasted_sales + order_quantity
        inventory_on_hand - forecasted_sales + adjusted_eoq
        if inventory_on_hand <= reorder_level
        else inventory_on_hand - forecasted_sales
    )

   # Calculate next check date
    total_inventory = inventory_on_hand + (adjusted_eoq if inventory_on_hand <= reorder_level else 0)
    daily_sales_forecast = forecasted_sales / 30  # Convert monthly forecast to daily
    days_until_check = (total_inventory - safety_stock) / daily_sales_forecast

    if days_until_check > 0:
        next_check_date = selected_date + timedelta(days=days_until_check)
        st.info(f"📅 **Next Check Date:** {next_check_date.strftime('%Y-%m-%d')}")
    else:
        st.warning("⚠️ Inventory is already at or below safety stock! Check immediately.")
 

    # Update the table with dynamic values
    filtered_table = selected_data.copy()
    filtered_table["Inventory on Hand"] = inventory_on_hand
    filtered_table["Predicted Ending Inventory"] = int(predicted_ending_inventory)  # Ensure integer
    filtered_table = filtered_table[["Month", "Forecasted Sales", "Inventory on Hand", "Predicted Ending Inventory"]]

    # Round all numeric columns to integers
    #filtered_table = filtered_table.astype({"Forecasted Sales":int, "Inventory on Hand":int, "Predicted Ending Inventory":int})

    # Show the filtered table
    st.subheader("Table for Selected Month")
    st.write(filtered_table)

    # Display key outputs for clarity
    st.subheader("Key Outputs")
    st.write(f"- **Forecasted Sales:** {forecasted_sales} units")
    st.write(f"- **Predicted Ending Inventory:** {predicted_ending_inventory} units")
else:
    st.error("No data available for the selected month. Please check the Excel file.")



# Footer
st.info("This tool uses your past sales data to calculate EOQ, update inventory levels, and make reorder suggestions. The next check date is an estimation of when the safety stock will be reached.")



# if not selected_data.empty:
#     # Extract values from the dataset
#     forecasted_demand = selected_data["Forecasted Demand"].values[0]
#     safety_stock = selected_data["Safety Stock"].values[0]
#     reorder_level = selected_data["Reorder Level"].values[0]
#     order_quantity = int(selected_data["Order Quantity"].values[0])  # Ensure EOQ is an integer
#     lead_time = selected_data["Lead Time"].values[0]

#     # Check if reorder is needed
#     if inventory_on_hand <= reorder_level:
#         st.warning(f"Reorder Needed! Suggested Order Quantity (EOQ): **{order_quantity} units.**")
#     else:
#         st.success("No Reorder Needed. Inventory is sufficient.")

#     # Calculate Ending Inventory dynamically
#     ending_inventory = (
#         inventory_on_hand - forecasted_demand + order_quantity
#         if inventory_on_hand <= reorder_level
#         else inventory_on_hand - forecasted_demand
#     )

#     # Update the DRP table with dynamic values
#     updated_data = data.copy()
#     updated_data.loc[updated_data["Month"] == month, "Inventory on Hand"] = inventory_on_hand
#     updated_data.loc[updated_data["Month"] == month, "Ending Inventory"] = ending_inventory

#     # Show updated DRP table
#     st.subheader("Updated DRP Table")
#     st.write(updated_data)

#     # Display key calculations
#     st.subheader("Key Outputs")
#     st.write(f"- **Forecasted Demand:** {forecasted_demand} units")
#     st.write(f"- **Safety Stock:** {safety_stock} units")
#     st.write(f"- **Reorder Level:** {reorder_level} units")
#     st.write(f"- **Ending Inventory:** {ending_inventory} units")
# else:
#     st.error("No data available for the selected month. Please check the Excel file.")

# # Footer
# st.info("This tool uses your DRP dataset to calculate EOQ, update inventory levels, and make reorder suggestions.")



# if not selected_data.empty:
#     # Extract values from the dataset
#     forecasted_demand = selected_data["Forecasted Demand"].values[0]
#     safety_stock = selected_data["Safety Stock"].values[0]
#     reorder_level = selected_data["Reorder Level"].values[0]
#     order_quantity = selected_data["Order Quantity"].values[0]

#     # Check if reorder is needed
#     if inventory_on_hand <= reorder_level:
#         st.warning(f"Reorder Needed! Suggested Order Quantity: {order_quantity} units.")
#     else:
#         st.success("No Reorder Needed. Inventory is sufficient.")

#     # Calculate Ending Inventory
#     ending_inventory = inventory_on_hand - forecasted_demand + order_quantity if inventory_on_hand <= reorder_level else inventory_on_hand - forecasted_demand
#     st.subheader("Ending Inventory")
#     st.write(f"Expected Ending Inventory: {ending_inventory} units")

#     # Optional: Show reference data
#     if st.checkbox("Show DRP Table"):
#         st.write(data)
# else:
#     st.error("No data available for the selected month. Please check the Excel file.")

# # Footer
# st.info("This tool uses the DRP dataset to determine reorder points and order quantities dynamically.")