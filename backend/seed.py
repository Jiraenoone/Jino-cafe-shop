"""
seed.py — ใส่ข้อมูลตัวอย่างลง SQLite สำหรับ local development

รันด้วย: python seed.py
"""
import asyncio
import json
import sys

sys.path.insert(0, ".")


async def seed() -> None:
    from app.database.connection import AsyncSessionLocal, init_db
    from app.models.category import Category
    from app.models.product import Product

    print("Seeding database...")
    await init_db()

    async with AsyncSessionLocal() as db:
        from sqlalchemy import delete
        from app.models.order import OrderItem, Order
        await db.execute(delete(OrderItem))
        await db.execute(delete(Order))
        await db.execute(delete(Product))
        await db.execute(delete(Category))
        await db.commit()

        # ── Categories ─────────────────────────────────────
        categories = [
            Category(name="Coffee",   description="เครื่องดื่มกาแฟสไตล์ต่างๆ",   sort_order=1),
            Category(name="Tea",      description="ชาร้อน ชาเย็น ชาผลไม้",       sort_order=2),
            Category(name="Smoothie", description="สมูทตี้ผลไม้สดใหม่",          sort_order=3),
            Category(name="Bakery",   description="เบเกอรี่อบสดทุกเช้า",         sort_order=4),
            Category(name="Seasonal", description="เมนูพิเศษตามฤดูกาล",         sort_order=5),
        ]
        for c in categories:
            db.add(c)
        await db.flush()

        coffee_id   = categories[0].id
        tea_id      = categories[1].id
        smoothie_id = categories[2].id
        bakery_id   = categories[3].id

        # ── Products ───────────────────────────────────────
        products = [
            # Coffee
            Product(category_id=coffee_id, name="Signature Latte",
                    description="กาแฟลาเต้สูตรพิเศษของ Jino Café ผสมนมสดคัดพิเศษ",
                    price=85.00, image_url="/assets/images/latte.jpg",
                    options=json.dumps({"sizes":["S","M","L"],"temperatures":["hot","iced"],"sweetness":["100%","75%","50%","25%","0%"]})),
            Product(category_id=coffee_id, name="Americano",
                    description="กาแฟอเมริกาโน่ รสชาติเข้มข้น กลมกล่อม",
                    price=65.00, image_url="/assets/images/americano.jpg",
                    options=json.dumps({"sizes":["S","M","L"],"temperatures":["hot","iced"]})),
            Product(category_id=coffee_id, name="Cappuccino",
                    description="กาแฟคาปูชิโน่ ฟองนมละเอียด รสชาติเข้มข้น",
                    price=80.00, image_url="/assets/images/cappuccino.jpg",
                    options=json.dumps({"sizes":["S","M"],"temperatures":["hot"]})),
            Product(category_id=coffee_id, name="Cold Brew",
                    description="Cold Brew สกัดเย็น 12 ชั่วโมง รสชาติเข้มข้น ไม่ขม",
                    price=90.00, image_url="/assets/images/coldbrew.jpg",
                    options=json.dumps({"sizes":["M","L"]})),
            Product(category_id=coffee_id, name="Caramel Macchiato",
                    description="ลาเต้คาราเมลซอส ราดด้วยคาราเมลโฮมเมด",
                    price=95.00, image_url="/assets/images/macchiato.jpg",
                    options=json.dumps({"sizes":["S","M","L"],"temperatures":["hot","iced"],"sweetness":["100%","75%","50%"]})),
            # Tea
            Product(category_id=tea_id, name="Thai Milk Tea",
                    description="ชาไทยนมสดสูตรต้นตำรับ หอมหวาน",
                    price=70.00, image_url="/assets/images/thaitea.jpg",
                    options=json.dumps({"sizes":["M","L"],"sweetness":["100%","75%","50%","25%","0%"]})),
            Product(category_id=tea_id, name="Matcha Latte",
                    description="มัทฉะลาเต้จากญี่ปุ่น เกรด Ceremonial",
                    price=95.00, image_url="/assets/images/matcha.jpg",
                    options=json.dumps({"sizes":["S","M","L"],"temperatures":["hot","iced"],"sweetness":["100%","75%","50%","0%"]})),
            Product(category_id=tea_id, name="Jasmine Green Tea",
                    description="ชามะลิเขียวหอม ผ่อนคลายใจ",
                    price=60.00, image_url="/assets/images/jasmine.jpg",
                    options=json.dumps({"sizes":["M","L"],"temperatures":["hot","iced"]})),
            # Smoothie
            Product(category_id=smoothie_id, name="Mango Smoothie",
                    description="สมูทตี้มะม่วงสดจากสวนไทย ไม่ผสมน้ำตาล",
                    price=80.00, image_url="/assets/images/mango.jpg",
                    options=json.dumps({"sizes":["M","L"]})),
            Product(category_id=smoothie_id, name="Mixed Berry",
                    description="สมูทตี้เบอร์รีรวม สตรอเบอร์รี บลูเบอร์รี ราสเบอร์รี",
                    price=85.00, image_url="/assets/images/berry.jpg",
                    options=json.dumps({"sizes":["M","L"]})),
            # Bakery
            Product(category_id=bakery_id, name="Butter Croissant",
                    description="ครัวซองต์เนยสดอบใหม่ทุกเช้า เปลือกกรอบ นุ่มด้านใน",
                    price=65.00, image_url="/assets/images/croissant.jpg"),
            Product(category_id=bakery_id, name="Banana Bread",
                    description="กล้วยหอมปังโฮมเมด หวานน้อย촉ชื้น",
                    price=55.00, image_url="/assets/images/bananabread.jpg"),
            Product(category_id=bakery_id, name="Chocolate Muffin",
                    description="มัฟฟินช็อกโกแลตเข้มข้น โรยช็อกโกแลตชิพ",
                    price=60.00, image_url="/assets/images/muffin.jpg"),
        ]
        for p in products:
            db.add(p)

        await db.commit()
        print(f"Seeded {len(categories)} categories and {len(products)} products!")


if __name__ == "__main__":
    asyncio.run(seed())
