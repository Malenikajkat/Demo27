"""
Генератор ER-диаграммы для информационной системы.
Экспорт в PDF через graphviz с использованием HTML-like меток.
"""
from graphviz import Digraph


def create_er_diagram():
    dot = Digraph('ER Diagram', format='pdf')
    dot.attr(rankdir='LR', size='20,30', dpi='150')
    dot.attr('node', fontname='Arial', fontsize='10')
    dot.attr('edge', fontname='Arial', fontsize='8')

    # Colors
    client_color = '#E3F2FD'
    product_color = '#E8F5E9'
    material_color = '#FFF3E0'
    operation_color = '#F3E5F5'
    order_color = '#FFEBEE'
    spec_color = '#E0F7FA'
    price_color = '#FCE4EC'

    def table_node(name, pk_fields, fields, color):
        """Создать узел в виде HTML-таблицы"""
        lines = ['<<TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">']
        lines.append(f'<TR><TD BGCOLOR="{color}" ALIGN="CENTER"><B>{name}</B></TD></TR>')

        # PK fields
        for f in pk_fields:
            lines.append(f'<TR><TD ALIGN="LEFT">🔑 {f}</TD></TR>')

        # Regular fields
        for f in fields:
            lines.append(f'<TR><TD ALIGN="LEFT">  {f}</TD></TR>')

        lines.append('</TABLE>>')
        return ''.join(lines)

    # ==================== TABLE: clients ====================
    dot.node('clients',
             table_node('clients',
                        ['client_id (PK, UUID)'],
                        ['name (VARCHAR(255))',
                         'inn (VARCHAR(20))',
                         'address (VARCHAR(255))',
                         'phone (VARCHAR(20))',
                         'client_type (VARCHAR(20))'],
                        client_color))

    # ==================== TABLE: products ====================
    dot.node('products',
             table_node('products',
                        ['product_id (PK, UUID)'],
                        ['name (VARCHAR(255))',
                         'code (VARCHAR(50) UNIQUE)'],
                        product_color))

    # ==================== TABLE: materials ====================
    dot.node('materials',
             table_node('materials',
                        ['material_id (PK, UUID)'],
                        ['name (VARCHAR(255))',
                         'code (VARCHAR(50) UNIQUE)'],
                        material_color))

    # ==================== TABLE: operations ====================
    dot.node('operations',
             table_node('operations',
                        ['operation_id (PK, UUID)'],
                        ['name (VARCHAR(255))',
                         'code (VARCHAR(50) UNIQUE)'],
                        operation_color))

    # ==================== TABLE: product_prices ====================
    dot.node('product_prices',
             table_node('product_prices',
                        ['product_price_id (PK, UUID)'],
                        ['product_id (FK)',
                         'price (DECIMAL(10,2))',
                         'effective_date (DATE)'],
                        price_color))

    # ==================== TABLE: material_prices ====================
    dot.node('material_prices',
             table_node('material_prices',
                        ['material_price_id (PK, UUID)'],
                        ['material_id (FK)',
                         'price (DECIMAL(10,2))',
                         'effective_date (DATE)'],
                        price_color))

    # ==================== TABLE: operation_prices ====================
    dot.node('operation_prices',
             table_node('operation_prices',
                        ['operation_price_id (PK, UUID)'],
                        ['operation_id (FK)',
                         'price (DECIMAL(10,2))',
                         'effective_date (DATE)'],
                        price_color))

    # ==================== TABLE: specification_materials ====================
    dot.node('specification_materials',
             table_node('specification_materials',
                        ['spec_mat_id (PK, UUID)'],
                        ['product_id (FK)',
                         'material_id (FK)',
                         'quantity_per_unit (DECIMAL(10,4))'],
                        spec_color))

    # ==================== TABLE: specification_operations ====================
    dot.node('specification_operations',
             table_node('specification_operations',
                        ['spec_op_id (PK, UUID)'],
                        ['product_id (FK)',
                         'operation_id (FK)',
                         'time_norm (DECIMAL(10,2))',
                         'op_quantity (DECIMAL(10,2))'],
                        spec_color))

    # ==================== TABLE: production_orders ====================
    dot.node('production_orders',
             table_node('production_orders',
                        ['order_id (PK, UUID)'],
                        ['order_number (VARCHAR(50))',
                         'order_date (DATE)',
                         'subdivision (VARCHAR(100))',
                         'status (VARCHAR(20))'],
                        order_color))

    # ==================== TABLE: production_order_items ====================
    dot.node('production_order_items',
             table_node('production_order_items',
                        ['order_item_id (PK, UUID)'],
                        ['production_order_id (FK)',
                         'product_id (FK)',
                         'quantity (DECIMAL(10,2))'],
                        order_color))

    # ==================== TABLE: sales_orders ====================
    dot.node('sales_orders',
             table_node('sales_orders',
                        ['sales_order_id (PK, UUID)'],
                        ['order_number (VARCHAR(50))',
                         'order_date (DATE)',
                         'client_id (FK - покупатель)',
                         'executor_id (FK - исполнитель)',
                         'total_amount (DECIMAL(12,2))'],
                        order_color))

    # ==================== TABLE: sales_order_items ====================
    dot.node('sales_order_items',
             table_node('sales_order_items',
                        ['sales_order_item_id (PK, UUID)'],
                        ['sales_order_id (FK)',
                         'product_id (FK)',
                         'quantity (DECIMAL(10,2))',
                         'unit_price (DECIMAL(10,2))',
                         'discount (DECIMAL(10,2))'],
                        order_color))

    # ==================== TABLE: users ====================
    dot.node('users',
             table_node('users',
                        ['user_id PK SERIAL'],
                        ['login VARCHAR(50) UNIQUE',
                         'password_hash VARCHAR(255)',
                         'role VARCHAR(20)',
                         'is_blocked BOOLEAN',
                         'failed_attempts INTEGER',
                         'blocked_until TIMESTAMP',
                         'created_at TIMESTAMP'],
                        '#FFF9C4'))

    # ==================== TABLE: notes ====================
    dot.node('notes',
             table_node('notes',
                        ['note_id PK SERIAL'],
                        ['title VARCHAR(255)',
                         'content TEXT',
                         'id_user FK users',
                         'created_at TIMESTAMP'],
                        '#E1BEE7'))

    # ==================== RELATIONSHIPS ====================

    dot.edge('clients', 'sales_orders', label='покупатель 1..M', color='blue', penwidth='2.0')
    dot.edge('clients', 'sales_orders', label='исполнитель 1..M', color='green', penwidth='2.0', style='dashed')

    dot.edge('products', 'product_prices', label='имеет цену 1..M', color='purple')
    dot.edge('materials', 'material_prices', label='имеет цену 1..M', color='purple')
    dot.edge('operations', 'operation_prices', label='имеет цену 1..M', color='purple')

    dot.edge('products', 'specification_materials', label='содержит 1..M', color='orange')
    dot.edge('materials', 'specification_materials', label='включён 1..M', color='orange')

    dot.edge('products', 'specification_operations', label='требует 1..M', color='darkviolet')
    dot.edge('operations', 'specification_operations', label='в спецификации 1..M', color='darkviolet')

    dot.edge('production_orders', 'production_order_items', label='содержит 1..M', color='red')
    dot.edge('products', 'production_order_items', label='в заказе 1..M', color='red')

    dot.edge('sales_orders', 'sales_order_items', label='содержит 1..M', color='darkred')
    dot.edge('products', 'sales_order_items', label='в заказе покупателя 1..M', color='darkred')

    # users -> notes
    dot.edge('users', 'notes', label='содержит заметки 1..M', color='purple')

    # Save and render
    dot.render('er_diagram', cleanup=True)
    print("ER-диаграмма создана: er_diagram.pdf")


if __name__ == '__main__':
    create_er_diagram()
