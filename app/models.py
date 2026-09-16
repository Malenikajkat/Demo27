"""
SQLAlchemy модели для всех таблиц базы данных.
"""
from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    Text,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.extensions import db


class Client(db.Model):
    """Заказчики (клиенты): поставщики и покупатели."""
    __tablename__ = "clients"

    client_id = Column(
        UUID(as_uuid=True), primary_key=True, default=func.gen_random_uuid()
    )
    name = Column(String(255), nullable=False)
    inn = Column(String(20))
    address = Column(String(255))
    phone = Column(String(20))
    client_type = Column(String(20), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "client_type IN ('Поставщик', 'Покупатель')",
            name="chk_client_type",
        ),
    )

    # Отношения
    sales_orders_as_client = relationship(
        "SalesOrder", foreign_keys="SalesOrder.client_id", back_populates="client"
    )
    sales_orders_as_executor = relationship(
        "SalesOrder", foreign_keys="SalesOrder.executor_id", back_populates="executor"
    )


class Product(db.Model):
    """Готовая продукция."""
    __tablename__ = "products"

    product_id = Column(
        UUID(as_uuid=True), primary_key=True, default=func.gen_random_uuid()
    )
    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Отношения
    prices = relationship("ProductPrice", back_populates="product", cascade="all, delete-orphan")
    spec_materials = relationship(
        "SpecificationMaterial", back_populates="product", cascade="all, delete-orphan"
    )
    spec_operations = relationship(
        "SpecificationOperation", back_populates="product", cascade="all, delete-orphan"
    )
    prod_order_items = relationship("ProductionOrderItem", back_populates="product")
    sales_order_items = relationship("SalesOrderItem", back_populates="product")


class Material(db.Model):
    """Материалы и компоненты."""
    __tablename__ = "materials"

    material_id = Column(
        UUID(as_uuid=True), primary_key=True, default=func.gen_random_uuid()
    )
    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Отношения
    prices = relationship("MaterialPrice", back_populates="material", cascade="all, delete-orphan")
    spec_materials = relationship("SpecificationMaterial", back_populates="material")


class Operation(db.Model):
    """Технологические операции."""
    __tablename__ = "operations"

    operation_id = Column(
        UUID(as_uuid=True), primary_key=True, default=func.gen_random_uuid()
    )
    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Отношения
    prices = relationship("OperationPrice", back_populates="operation", cascade="all, delete-orphan")
    spec_operations = relationship("SpecificationOperation", back_populates="operation")


class ProductPrice(db.Model):
    """Цены продукции."""
    __tablename__ = "product_prices"

    product_price_id = Column(
        UUID(as_uuid=True), primary_key=True, default=func.gen_random_uuid()
    )
    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("products.product_id", ondelete="CASCADE"),
        nullable=False,
    )
    price = Column(Numeric(10, 2), nullable=False)
    effective_date = Column(Date, nullable=False, server_default=func.current_date())

    __table_args__ = (
        CheckConstraint("price >= 0", name="chk_product_price_positive"),
    )

    product = relationship("Product", back_populates="prices")


class MaterialPrice(db.Model):
    """Цены материалов."""
    __tablename__ = "material_prices"

    material_price_id = Column(
        UUID(as_uuid=True), primary_key=True, default=func.gen_random_uuid()
    )
    material_id = Column(
        UUID(as_uuid=True),
        ForeignKey("materials.material_id", ondelete="CASCADE"),
        nullable=False,
    )
    price = Column(Numeric(10, 2), nullable=False)
    effective_date = Column(Date, nullable=False, server_default=func.current_date())

    __table_args__ = (
        CheckConstraint("price >= 0", name="chk_material_price_positive"),
    )

    material = relationship("Material", back_populates="prices")


class OperationPrice(db.Model):
    """Цены операций."""
    __tablename__ = "operation_prices"

    operation_price_id = Column(
        UUID(as_uuid=True), primary_key=True, default=func.gen_random_uuid()
    )
    operation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("operations.operation_id", ondelete="CASCADE"),
        nullable=False,
    )
    price = Column(Numeric(10, 2), nullable=False)
    effective_date = Column(Date, nullable=False, server_default=func.current_date())

    __table_args__ = (
        CheckConstraint("price >= 0", name="chk_operation_price_positive"),
    )

    operation = relationship("Operation", back_populates="prices")


class SpecificationMaterial(db.Model):
    """Спецификация материалов (норма расхода на 1 единицу продукции)."""
    __tablename__ = "specification_materials"

    spec_mat_id = Column(
        UUID(as_uuid=True), primary_key=True, default=func.gen_random_uuid()
    )
    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("products.product_id", ondelete="CASCADE"),
        nullable=False,
    )
    material_id = Column(
        UUID(as_uuid=True),
        ForeignKey("materials.material_id", ondelete="CASCADE"),
        nullable=False,
    )
    quantity_per_unit = Column(Numeric(10, 4), nullable=False)

    __table_args__ = (
        CheckConstraint("quantity_per_unit > 0", name="chk_spec_mat_qty_positive"),
    )

    product = relationship("Product", back_populates="spec_materials")
    material = relationship("Material", back_populates="spec_materials")


class SpecificationOperation(db.Model):
    """Спецификация технологических операций."""
    __tablename__ = "specification_operations"

    spec_op_id = Column(
        UUID(as_uuid=True), primary_key=True, default=func.gen_random_uuid()
    )
    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("products.product_id", ondelete="CASCADE"),
        nullable=False,
    )
    operation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("operations.operation_id", ondelete="CASCADE"),
        nullable=False,
    )
    time_norm = Column(Numeric(10, 2), nullable=False, server_default="1.0")
    op_quantity = Column(Numeric(10, 2), nullable=False, server_default="1.0")

    product = relationship("Product", back_populates="spec_operations")
    operation = relationship("Operation", back_populates="spec_operations")


class ProductionOrder(db.Model):
    """Заказы на производство."""
    __tablename__ = "production_orders"

    order_id = Column(
        UUID(as_uuid=True), primary_key=True, default=func.gen_random_uuid()
    )
    order_number = Column(String(50), unique=True, nullable=False)
    order_date = Column(Date, nullable=False)
    subdivision = Column(String(100))
    status = Column(String(20), nullable=False, server_default="Новый")
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "status IN ('Новый', 'В работе', 'Завершён', 'Отменён')",
            name="chk_prod_order_status",
        ),
    )

    items = relationship(
        "ProductionOrderItem", back_populates="production_order", cascade="all, delete-orphan"
    )


class ProductionOrderItem(db.Model):
    """Продукция в заказе на производство."""
    __tablename__ = "production_order_items"

    order_item_id = Column(
        UUID(as_uuid=True), primary_key=True, default=func.gen_random_uuid()
    )
    production_order_id = Column(
        UUID(as_uuid=True),
        ForeignKey("production_orders.order_id", ondelete="CASCADE"),
        nullable=False,
    )
    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("products.product_id", ondelete="RESTRICT"),
        nullable=False,
    )
    quantity = Column(Numeric(10, 2), nullable=False)

    __table_args__ = (
        CheckConstraint("quantity > 0", name="chk_prod_order_qty_positive"),
    )

    production_order = relationship("ProductionOrder", back_populates="items")
    product = relationship("Product", back_populates="prod_order_items")


class SalesOrder(db.Model):
    """Заказы покупателя."""
    __tablename__ = "sales_orders"

    sales_order_id = Column(
        UUID(as_uuid=True), primary_key=True, default=func.gen_random_uuid()
    )
    order_number = Column(String(50), unique=True, nullable=False)
    order_date = Column(Date, nullable=False)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.client_id"), nullable=False)
    executor_id = Column(UUID(as_uuid=True), ForeignKey("clients.client_id"), nullable=False)
    total_amount = Column(Numeric(12, 2), server_default="0.00")
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint("client_id <> executor_id", name="chk_sales_client_neq_executor"),
    )

    client = relationship(
        "Client", foreign_keys=[client_id], back_populates="sales_orders_as_client"
    )
    executor = relationship(
        "Client", foreign_keys=[executor_id], back_populates="sales_orders_as_executor"
    )
    items = relationship(
        "SalesOrderItem", back_populates="sales_order", cascade="all, delete-orphan"
    )


class SalesOrderItem(db.Model):
    """Товары в заказе покупателя."""
    __tablename__ = "sales_order_items"

    sales_order_item_id = Column(
        UUID(as_uuid=True), primary_key=True, default=func.gen_random_uuid()
    )
    sales_order_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sales_orders.sales_order_id", ondelete="CASCADE"),
        nullable=False,
    )
    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("products.product_id", ondelete="RESTRICT"),
        nullable=False,
    )
    quantity = Column(Numeric(10, 2), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    discount = Column(Numeric(10, 2), nullable=False, server_default="0.00")

    __table_args__ = (
        CheckConstraint("quantity > 0", name="chk_sales_qty_positive"),
        CheckConstraint("unit_price >= 0", name="chk_sales_price_positive"),
        CheckConstraint("discount >= 0", name="chk_sales_discount_positive"),
    )

    sales_order = relationship("SalesOrder", back_populates="items")
    product = relationship("Product", back_populates="sales_order_items")


class User(db.Model):
    """Пользователи системы с ролями и блокировкой."""
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, server_default="Пользователь")
    is_blocked = Column(Boolean, nullable=False, server_default="false")
    failed_attempts = Column(Integer, nullable=False, server_default="0")
    blocked_until = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "role IN ('Администратор', 'Пользователь')",
            name="chk_user_role",
        ),
    )

    notes = relationship("Note", back_populates="user")

    # Flask-Login required properties
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return not self.is_blocked

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.user_id)


class Note(db.Model):
    """Заметки пользователей."""
    __tablename__ = "notes"

    note_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    id_user = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="notes")
