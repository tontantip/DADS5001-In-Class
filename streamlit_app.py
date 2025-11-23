import streamlit as st
import pymongo
from bson.objectid import ObjectId

# Initialize connection.
@st.cache_resource
def init_connection():
    # ตรวจสอบว่ามี secrets หรือไม่
    if "mongo" in st.secrets:
        return pymongo.MongoClient(**st.secrets["mongo"])
    else:
        st.error("ไม่พบข้อมูลการเชื่อมต่อใน st.secrets")
        return None

client = init_connection()

# ฟังก์ชันดึงข้อมูล (Read)
@st.cache_data(ttl=600)
def get_data(query_filter):
    if client:
        db = client.mydb
        items = db.mycollection.find(query_filter)
        return list(items)
    return []

# ฟังก์ชันอัปเดตข้อมูล (Update)
def update_item(item_id, new_name, new_pet):
    if client:
        db = client.mydb
        try:
            result = db.mycollection.update_one(
                {"_id": item_id},
                {"$set": {"name": new_name, "pet": new_pet}}
            )
            
            if result.modified_count > 0:
                st.success("✅ อัปเดตข้อมูลเรียบร้อยแล้ว!")
                # เคลียร์ Cache เพื่อให้ดึงข้อมูลใหม่ล่าสุดมาแสดง
                get_data.clear()
                # Rerun หน้าเว็บใหม่
                st.rerun()
            else:
                st.info("ℹ️ ไม่มีการเปลี่ยนแปลงข้อมูล (ค่าใหม่เหมือนกับค่าเดิม)")
                
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการอัปเดต: {e}")

st.title("My pet 🐟😺🐶")

# --- ส่วนที่ 1: การค้นหา (Filter/Query) ---
st.subheader("🔍 ค้นหาข้อมูล")

col1, col2 = st.columns(2)
with col1:
    search_name = st.text_input("ค้นหาจากชื่อ (Name):")
    search_name1 = st.text_input("ค้นหาจากชนิดของสัตว์เลี้ยง (Pet):")
    
with col2:
    filter_pet = st.selectbox("กรองชนิดสัตว์เลี้ยง:", ["ทั้งหมด", "cat", "dog", "fish", "bird"])

# สร้าง Query
final_query = {}
if search_name:
    final_query["name"] = {"$regex": search_name, "$options": "i"}
if filter_pet != "ทั้งหมด":
    final_query["pet"] = filter_pet
if search_name1:
    final_query["pet"] = {"$regex": search_name1, "$options": "i"}

# ดึงข้อมูล
items = []
if client:
    items = get_data(final_query)
    
    st.info(f"พบข้อมูลจำนวน: {len(items)} รายการ")
    
    # แสดงรายการแบบย่อ
    if items:
        with st.expander("ดูรายการข้อมูลทั้งหมด", expanded=True):
            for item in items:
                name = item.get('name', 'Unknown')
                pet = item.get('pet', '-')
                st.write(f"- **{name}** (Pet: {pet})")
    else:
        st.warning("ไม่พบข้อมูลตามเงื่อนไข")

# --- ส่วนที่ 2: การแก้ไขข้อมูล (Update) ---
st.divider()
st.subheader("📝 แก้ไขข้อมูล (Update Data)")

if items:
    # 1. เลือกรายการที่ต้องการแก้
    # สร้าง Dictionary เพื่อ map ชื่อที่จะแสดงใน Dropdown กับ Object จริง
    # เราใช้ ID ต่อท้ายเพื่อให้แยกแยะชื่อที่ซ้ำกันได้
    item_options = {f"{item.get('name')} (Pet: {item.get('pet')}) [ID: {str(item['_id'])[-4:]}]": item for item in items}
    
    selected_label = st.selectbox("เลือกรายการที่ต้องการแก้ไข:", list(item_options.keys()))
    
    if selected_label:
        selected_item = item_options[selected_label]
        
        st.write("---")
        st.write("Provide new values:")
        
        # 2. ฟอร์มสำหรับแก้ไขข้อมูล
        with st.form("update_form"):
            # แสดง ID ให้ดู (แก้ไขไม่ได้)
            st.text_input("Object ID (แก้ไขไม่ได้)", value=str(selected_item['_id']), disabled=True)
            
            # ช่องกรอกชื่อ (ดึงค่าเดิมมาใส่ให้)
            new_name_input = st.text_input("แก้ไขชื่อ:", value=selected_item.get('name', ''))
            
            # ช่องเลือกสัตว์เลี้ยง (พยายามเลือกค่าเดิมให้ถูกต้อง)
            pet_options = ["cat", "dog", "fish", "bird", "other"]
            current_pet = selected_item.get('pet', 'other')
            
            # หา index ของค่าเดิม ถ้าไม่มีให้เป็น 0
            try:
                pet_index = pet_options.index(current_pet)
            except ValueError:
                pet_index = 0 # Default ถ้าค่าเดิมไม่อยู่ใน list
                
            new_pet_input = st.selectbox("แก้ไขสัตว์เลี้ยง:", pet_options, index=pet_index)
            
            # ปุ่ม Submit
            submitted = st.form_submit_button("💾 บันทึกการแก้ไข")
            
            if submitted:
                # เรียกฟังก์ชัน Update
                update_item(selected_item['_id'], new_name_input, new_pet_input)

else:
    st.write("กรุณาค้นหาข้อมูล หรือรอให้มีข้อมูลแสดงเพื่อทำการแก้ไข")
