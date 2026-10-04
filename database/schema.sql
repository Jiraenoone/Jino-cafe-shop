-- ═══════════════════════════════════════════════════════════════
--  Jino Café — Azure SQL Database Schema
--  ไฟล์นี้ใช้สร้าง schema ครั้งแรก และ seed ข้อมูลตัวอย่าง
-- ═══════════════════════════════════════════════════════════════

-- ─── ล้าง schema เก่า (สำหรับ dev reset) ───────────────────────
IF OBJECT_ID('dbo.OrderItems', 'U') IS NOT NULL DROP TABLE dbo.OrderItems;
IF OBJECT_ID('dbo.Orders',     'U') IS NOT NULL DROP TABLE dbo.Orders;
IF OBJECT_ID('dbo.Products',   'U') IS NOT NULL DROP TABLE dbo.Products;
IF OBJECT_ID('dbo.Categories', 'U') IS NOT NULL DROP TABLE dbo.Categories;
IF OBJECT_ID('dbo.Users',      'U') IS NOT NULL DROP TABLE dbo.Users;
GO

-- ─── Categories ──────────────────────────────────────────────────
-- หมวดหมู่สินค้า เช่น Coffee, Tea, Bakery
CREATE TABLE dbo.Categories (
    id          INT           IDENTITY(1,1) PRIMARY KEY,
    name        NVARCHAR(100) NOT NULL,
    description NVARCHAR(500) NULL,
    image_url   NVARCHAR(500) NULL,
    sort_order  INT           NOT NULL DEFAULT 0,   -- ลำดับการแสดงผล
    is_active   BIT           NOT NULL DEFAULT 1,
    created_at  DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
);
GO

-- ─── Products ────────────────────────────────────────────────────
-- สินค้าแต่ละชิ้น เช่น Latte, Croissant
-- options เป็น JSON column เก็บตัวเลือก เช่น:
--   { "sizes": ["S","M","L"], "temperatures": ["hot","iced"] }
CREATE TABLE dbo.Products (
    id           INT            IDENTITY(1,1) PRIMARY KEY,
    category_id  INT            NOT NULL,
    name         NVARCHAR(200)  NOT NULL,
    description  NVARCHAR(1000) NULL,
    image_url    NVARCHAR(500)  NULL,
    price        DECIMAL(10,2)  NOT NULL,
    options      NVARCHAR(MAX)  NULL,  -- JSON: { "sizes": [...], "temperatures": [...] }
    is_available BIT            NOT NULL DEFAULT 1,
    created_at   DATETIME2      NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at   DATETIME2      NOT NULL DEFAULT SYSUTCDATETIME(),

    CONSTRAINT FK_Products_Categories
        FOREIGN KEY (category_id) REFERENCES dbo.Categories(id),
    CONSTRAINT CK_Products_Price
        CHECK (price >= 0)
);
GO

-- ─── Users ───────────────────────────────────────────────────────
-- ผู้ใช้งาน (admin เท่านั้นในตอนนี้ เพราะลูกค้า guest checkout)
-- role: 'CUSTOMER' | 'ADMIN'
CREATE TABLE dbo.Users (
    id         INT            IDENTITY(1,1) PRIMARY KEY,
    name       NVARCHAR(200)  NOT NULL,
    email      NVARCHAR(320)  NOT NULL,
    phone      NVARCHAR(20)   NULL,
    role       NVARCHAR(20)   NOT NULL DEFAULT 'CUSTOMER',
    created_at DATETIME2      NOT NULL DEFAULT SYSUTCDATETIME(),

    CONSTRAINT UQ_Users_Email UNIQUE (email),
    CONSTRAINT CK_Users_Role CHECK (role IN ('CUSTOMER', 'ADMIN'))
);
GO

-- ─── Orders ──────────────────────────────────────────────────────
-- คำสั่งซื้อ
-- status: PENDING → CONFIRMED → PREPARING → READY → COMPLETED | CANCELLED
-- customer_name / customer_email เก็บไว้สำหรับ guest checkout
CREATE TABLE dbo.Orders (
    id               INT            IDENTITY(1,1) PRIMARY KEY,
    user_id          INT            NULL,          -- NULL = guest
    customer_name    NVARCHAR(200)  NOT NULL,
    customer_email   NVARCHAR(320)  NOT NULL,
    customer_phone   NVARCHAR(20)   NULL,
    status           NVARCHAR(20)   NOT NULL DEFAULT 'PENDING',
    total_amount     DECIMAL(10,2)  NOT NULL,
    notes            NVARCHAR(500)  NULL,
    created_at       DATETIME2      NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at       DATETIME2      NOT NULL DEFAULT SYSUTCDATETIME(),

    CONSTRAINT FK_Orders_Users
        FOREIGN KEY (user_id) REFERENCES dbo.Users(id),
    CONSTRAINT CK_Orders_Status
        CHECK (status IN ('PENDING','CONFIRMED','PREPARING','READY','COMPLETED','CANCELLED')),
    CONSTRAINT CK_Orders_TotalAmount
        CHECK (total_amount >= 0)
);
GO

-- ─── OrderItems ──────────────────────────────────────────────────
-- รายการสินค้าในแต่ละออเดอร์
-- unit_price: snapshot ราคา ณ เวลาสั่ง (ป้องกันปัญหาถ้าราคาสินค้าเปลี่ยน)
-- selected_options: JSON เก็บสิ่งที่ลูกค้าเลือก เช่น { "size": "L", "temperature": "iced" }
CREATE TABLE dbo.OrderItems (
    id               INT            IDENTITY(1,1) PRIMARY KEY,
    order_id         INT            NOT NULL,
    product_id       INT            NOT NULL,
    quantity         INT            NOT NULL DEFAULT 1,
    unit_price       DECIMAL(10,2)  NOT NULL,
    selected_options NVARCHAR(MAX)  NULL,  -- JSON
    notes            NVARCHAR(500)  NULL,

    CONSTRAINT FK_OrderItems_Orders
        FOREIGN KEY (order_id) REFERENCES dbo.Orders(id),
    CONSTRAINT FK_OrderItems_Products
        FOREIGN KEY (product_id) REFERENCES dbo.Products(id),
    CONSTRAINT CK_OrderItems_Quantity
        CHECK (quantity >= 1),
    CONSTRAINT CK_OrderItems_UnitPrice
        CHECK (unit_price >= 0)
);
GO

-- ─── Indexes ─────────────────────────────────────────────────────
-- ช่วยให้ query เร็วขึ้น
CREATE INDEX IX_Products_CategoryId   ON dbo.Products(category_id);
CREATE INDEX IX_Products_IsAvailable  ON dbo.Products(is_available);
CREATE INDEX IX_Orders_Status         ON dbo.Orders(status);
CREATE INDEX IX_Orders_CustomerEmail  ON dbo.Orders(customer_email);
CREATE INDEX IX_Orders_CreatedAt      ON dbo.Orders(created_at DESC);
CREATE INDEX IX_OrderItems_OrderId    ON dbo.OrderItems(order_id);
CREATE INDEX IX_OrderItems_ProductId  ON dbo.OrderItems(product_id);
GO

-- ═══════════════════════════════════════════════════════════════
--  SEED DATA — ข้อมูลตัวอย่างสำหรับ dev/demo
-- ═══════════════════════════════════════════════════════════════

-- หมวดหมู่
INSERT INTO dbo.Categories (name, description, image_url, sort_order) VALUES
('Coffee',    'เครื่องดื่มกาแฟสไตล์ต่างๆ',      '/assets/images/cat-coffee.jpg',  1),
('Tea',       'ชาร้อน ชาเย็น ชาผลไม้',           '/assets/images/cat-tea.jpg',     2),
('Smoothie',  'สมูทตี้ผลไม้สดใหม่',              '/assets/images/cat-smoothie.jpg',3),
('Bakery',    'เบเกอรี่อบสดทุกเช้า',             '/assets/images/cat-bakery.jpg',  4),
('Seasonal',  'เมนูพิเศษตามฤดูกาล',              '/assets/images/cat-seasonal.jpg',5);
GO

-- สินค้า — Coffee
INSERT INTO dbo.Products (category_id, name, description, image_url, price, options) VALUES
(1, 'Signature Latte',
   'กาแฟลาเต้สูตรพิเศษของ Jino Café ผสมนมสดคัดพิเศษ',
   '/assets/images/prod-latte.jpg', 85.00,
   '{"sizes":["S","M","L"],"temperatures":["hot","iced"],"sweetness":["100%","75%","50%","25%","0%"]}'),

(1, 'Americano',
   'กาแฟอเมริกาโน่ รสชาติเข้มข้น กลมกล่อม',
   '/assets/images/prod-americano.jpg', 65.00,
   '{"sizes":["S","M","L"],"temperatures":["hot","iced"]}'),

(1, 'Cappuccino',
   'กาแฟคาปูชิโน่ 泡沫细腻，风味浓郁',
   '/assets/images/prod-cappuccino.jpg', 80.00,
   '{"sizes":["S","M"],"temperatures":["hot"]}'),

(1, 'Cold Brew',
   'Cold Brew สกัดเย็น 12 ชั่วโมง รสชาติเข้มข้น ไม่ขม',
   '/assets/images/prod-coldbrew.jpg', 90.00,
   '{"sizes":["M","L"]}'),

(1, 'Caramel Macchiato',
   'ลาเต้คาราเมลซอส ด้านบนราดด้วยคาราเมลโฮมเมด',
   '/assets/images/prod-macchiato.jpg', 95.00,
   '{"sizes":["S","M","L"],"temperatures":["hot","iced"],"sweetness":["100%","75%","50%"]}');
GO

-- สินค้า — Tea
INSERT INTO dbo.Products (category_id, name, description, image_url, price, options) VALUES
(2, 'Thai Milk Tea',
   'ชาไทยนมสดสูตรต้นตำรับ หอมหวาน',
   '/assets/images/prod-thaitea.jpg', 70.00,
   '{"sizes":["M","L"],"sweetness":["100%","75%","50%","25%","0%"]}'),

(2, 'Matcha Latte',
   'มัทฉะลาเต้จากญี่ปุ่น เกรด Ceremonial',
   '/assets/images/prod-matcha.jpg', 95.00,
   '{"sizes":["S","M","L"],"temperatures":["hot","iced"],"sweetness":["100%","75%","50%","0%"]}'),

(2, 'Jasmine Green Tea',
   'ชามะลิเขียวหอม ผ่อนคลายใจ',
   '/assets/images/prod-jasmine.jpg', 60.00,
   '{"sizes":["M","L"],"temperatures":["hot","iced"]}');
GO

-- สินค้า — Smoothie
INSERT INTO dbo.Products (category_id, name, description, image_url, price, options) VALUES
(3, 'Mango Smoothie',
   'สมูทตี้มะม่วงสดจากสวนไทย ไม่ผสมน้ำตาล',
   '/assets/images/prod-mango.jpg', 80.00,
   '{"sizes":["M","L"]}'),

(3, 'Mixed Berry',
   'สมูทตี้เบอร์รีรวม สตรอเบอร์รี บลูเบอร์รี ราสเบอร์รี',
   '/assets/images/prod-berry.jpg', 85.00,
   '{"sizes":["M","L"]}');
GO

-- สินค้า — Bakery
INSERT INTO dbo.Products (category_id, name, description, image_url, price, options) VALUES
(4, 'Butter Croissant',
   'ครัวซองต์เนยสดอบใหม่ทุกเช้า เปลือกกรอบ นุ่มด้านใน',
   '/assets/images/prod-croissant.jpg', 65.00,
   NULL),

(4, 'Banana Bread',
   'กล้วยหอมปังโฮมเมด หวานน้อย ช촉ชื้น',
   '/assets/images/prod-bananabread.jpg', 55.00,
   NULL),

(4, 'Chocolate Muffin',
   'มัฟฟินช็อกโกแลตเข้มข้น ด้านบนโรยช็อกโกแลตชิพ',
   '/assets/images/prod-muffin.jpg', 60.00,
   NULL);
GO

-- Admin user ตัวอย่าง (password จัดการนอก schema)
INSERT INTO dbo.Users (name, email, role) VALUES
('Jino Admin', 'admin@jinocafe.com', 'ADMIN');
GO

PRINT 'Schema และ seed data สร้างเสร็จแล้ว ✅';
GO
