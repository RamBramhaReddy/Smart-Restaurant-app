import json
import random
import streamlit as st
import qrcode
from PIL import Image
import io
# Updated from VS Code
# Load menu
with open("menu.json", "r") as f:
    menu = json.load(f)

st.set_page_config(page_title="Smart Restaurant", layout="centered")
st.title("🍽 Welcome to the Smart Restaurant!")

# Initialize session state
if "order_started" not in st.session_state:
    st.session_state.order_started = False
if "total_bill" not in st.session_state:
    st.session_state.total_bill = 0
if "order_items" not in st.session_state:
    st.session_state.order_items = []
if "allocated_tables" not in st.session_state:
    st.session_state.allocated_tables = set()  # track assigned tables
if "table_number" not in st.session_state:
    st.session_state.table_number = None

# Step 1: Takeaway or Dine-in
if not st.session_state.order_started:
    choice = st.radio("What are you looking for today?", ["Takeaway", "Dine-in"])
    
    if st.button("Confirm Selection"):
        if choice == "Dine-in":
            available_tables = set(range(1, 16)) - st.session_state.allocated_tables
            if available_tables:
                st.session_state.table_number = random.choice(list(available_tables))
                st.session_state.allocated_tables.add(st.session_state.table_number)
                st.success(f"✅ Your table number is: {st.session_state.table_number}")
            else:
                st.error("❌ Sorry, all tables are currently occupied!")
        st.session_state.order_started = True
        st.rerun()

# Always show table number if allocated
if st.session_state.table_number:
    st.info(f"🍴 Your Table Number: {st.session_state.table_number}")

st.subheader("Menu")

# Step 2: Category selection
dish1 = st.selectbox("Select Category", [""] + list(menu.keys()))

# Initialize variables
dish2, dish3, dish4 = None, None, None
item_name = None
size_options = []
size = None
price_per_item = 0

# Handle different menu structures
if dish1:
    if dish1 == "Indian Breads":
        # Special handling for Indian Breads (3-level structure)
        item_name = st.selectbox(
            "Select Item", 
            [""] + list(menu[dish1].keys())
        )
        
        if item_name:
            # For Indian Breads, the price is direct
            item_data = menu[dish1][item_name]
            if isinstance(item_data, (int, float)):
                price_per_item = item_data
                size_options = ["Piece"]
                size = "Piece"
            else:
                # Fallback if structure is different
                size_options = list(item_data.keys()) if isinstance(item_data, dict) else ["Piece"]
                size = st.selectbox("Select Size", [""] + size_options) if len(size_options) > 1 else size_options[0] if size_options else None
                price_per_item = item_data.get(size, item_data) if isinstance(item_data, dict) and size else item_data
    else:
        # Regular 4-level structure for other categories
        dish2 = st.selectbox(
            "Select Sub-Category", 
            [""] + (list(menu[dish1].keys()) if dish1 else [])
        )
        dish3 = st.selectbox(
            "Select Dish Type", 
            [""] + (list(menu[dish1][dish2].keys()) if dish1 and dish2 else [])
        )
        dish4 = st.selectbox(
            "Select Size", 
            [""] + (list(menu[dish1][dish2][dish3].keys()) if dish1 and dish2 and dish3 else [])
        )
        
        # For 4-level structure, the actual item name is dish3, dish4 is the size
        item_name = dish3  # This is the actual dish name like "Chicken Biryani"
        
        # Show size options if item is selected
        if dish1 and dish2 and dish3:
            item_data = menu[dish1][dish2][dish3]
            # dish4 now represents the size selection
            size_options = list(item_data.keys()) if isinstance(item_data, dict) else ["Single Serving"]

        size = dish4  # dish4 is now the selected size
        
        # Get price based on size selection
        if dish1 and dish2 and dish3 and dish4:
            item_data = menu[dish1][dish2][dish3]  # Get the dish data
            if isinstance(item_data, dict):
                price_per_item = item_data.get(dish4, 0)  # dish4 is the size
            else:
                price_per_item = item_data

# Show quantity input only after all selections are made
quantity = 1
show_quantity = False

if dish1:
    if dish1 == "Indian Breads":
        # For Indian Breads, show quantity after item selection
        if item_name:
            show_quantity = True
    else:
        # For other categories, show quantity after all selections including size
        if dish1 and dish2 and dish3 and dish4:  # dish4 is now the size
            show_quantity = True

# Display quantity input only when appropriate
if show_quantity:
    st.markdown("---")
    quantity = st.number_input("🔢 Select Quantity", min_value=1, value=1, help="Choose how many items you want")

# Step 3: Add to order button
if st.button("Add to Order"):
    if item_name and quantity > 0:
        # Validate selections based on category
        if dish1 == "Indian Breads":
            # For Indian Breads, just need item selection
            if not item_name:
                st.error("Please select an item!")
                st.stop()
        else:
            # For other categories, need all selections
            if not (dish1 and dish2 and dish3 and dish4):
                st.error("Please complete all selections!")
                st.stop()
        
        total_price = price_per_item * quantity
        
        # Add to order
        st.session_state.total_bill += total_price
        st.session_state.order_items.append({
            "item": item_name,
            "size": size if size else "Standard",
            "quantity": quantity,
            "price_per_item": price_per_item,
            "total_price": total_price
        })
        
        size_display = f" ({size})" if size and size != "Piece" and size != "Single Serving" else ""
        st.success(f"✅ Added: {item_name}{size_display} | Quantity: {quantity} | Total: ₹{total_price}")
        st.info(f"💰 Current Bill: ₹{st.session_state.total_bill}")
    else:
        st.error("Please select an item and quantity!")

# Step 4: Show current order
if st.session_state.order_items:
    st.subheader("🛒 Current Order")
    for item in st.session_state.order_items:
        size_display = f" ({item['size']})" if item['size'] not in ["Piece", "Single Serving", "Standard"] else ""
        st.write(f"📦 **{item['item']}**{size_display} - ₹{item['price_per_item']} each | **Qty: {item['quantity']}** | Total: ₹{item['total_price']}")
    st.write(f"💰 **Grand Total: ₹{st.session_state.total_bill}** | **Total Items: {sum(item['quantity'] for item in st.session_state.order_items)}**")

# Step 5: Checkout
if st.session_state.order_items and st.button("Checkout"):
    if st.session_state.table_number:
        st.info(f"🍴 Table Number: {st.session_state.table_number}")
    
    # Display detailed bill
    st.subheader("🧾 Final Bill")
    for item in st.session_state.order_items:
        size_display = f" ({item['size']})" if item['size'] not in ["Piece", "Single Serving", "Standard"] else ""
        st.write(f"📦 **{item['item']}**{size_display} - ₹{item['price_per_item']} each × **{item['quantity']}** = ₹{item['total_price']}")
    
    st.write("---")
    st.write(f"🎯 **Total Items Ordered: {sum(item['quantity'] for item in st.session_state.order_items)}**")
    st.write(f"💰 **Grand Total: ₹{st.session_state.total_bill}**")

    # Generate QR code
    qr_data = f"Restaurant Bill\nTable: {st.session_state.table_number or 'Takeaway'}\nTotal: ₹{st.session_state.total_bill}\nItems: {len(st.session_state.order_items)}"
    
    # Reduced QR size
    qr = qrcode.QRCode(version=1, box_size=5, border=5)
    qr.add_data(qr_data)
    qr.make(fit=True)

    qr_image = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    qr_image.save(buf)
    buf.seek(0)
    # 👇 Changed here to fix the display size
    st.image(buf, caption="Scan for Payment", width=200)

    # Reset order button
    if st.button("Start New Order"):
        st.session_state.order_items = []
        st.session_state.total_bill = 0
        st.session_state.order_started = False
        if st.session_state.table_number:
            st.session_state.allocated_tables.discard(st.session_state.table_number)
            st.session_state.table_number = None
        st.rerun()