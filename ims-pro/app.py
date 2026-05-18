from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import traceback
import random
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'inventory-secret-key-2024')

# ============================================================
# DATABASE CONNECTION - Production Ready
# ============================================================
# Render/Koyeb पर DATABASE_URL environment variable में Neon connection string डालें
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    # Local development के लिए (अगर environment variable नहीं है तो)
    DATABASE_URL = "postgresql://neondb_owner:npg_F1kgVCxvAK2o@ep-quiet-river-aoi8ja0k-pooler.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# Neon URL format fix - 'postgres://' को 'postgresql://' में बदलें
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 5,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
}

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ========== DATABASE MODELS ==========
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default='user')
    full_name = db.Column(db.String(200), default='')
    email = db.Column(db.String(200), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    sku_code = db.Column(db.String(100), unique=True, nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    unit = db.Column(db.String(50), default='Pcs')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Inventory(db.Model):
    __tablename__ = 'inventory'
    id = db.Column(db.Integer, primary_key=True)
    sku_code = db.Column(db.String(100), nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    batch_number = db.Column(db.String(100), nullable=False)
    manufacturing_date = db.Column(db.Date, nullable=True)
    expiry_date = db.Column(db.Date, nullable=True)
    quantity = db.Column(db.Integer, default=0)
    purchase_price = db.Column(db.Float, default=0)
    mrp = db.Column(db.Float, default=0)
    selling_price = db.Column(db.Float, default=0)
    condition = db.Column(db.String(50), default='Good')
    bin_no = db.Column(db.String(50))
    warehouse_name = db.Column(db.String(100))
    location_code = db.Column(db.String(100))
    remarks = db.Column(db.Text)
    updated_by = db.Column(db.String(100))
    updated_on = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SalesOrder(db.Model):
    __tablename__ = 'sales_orders'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(100), unique=True, nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    sku_code = db.Column(db.String(100), nullable=False)
    item_name = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    sale_value = db.Column(db.Float, nullable=False)
    order_status = db.Column(db.String(50), default='Created')
    payment_mode = db.Column(db.String(50), default='Cash')
    created_by = db.Column(db.String(100))
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'))
    business_type = db.Column(db.String(50), default='')
    platform_name = db.Column(db.String(50), default='')
    original_bin_no = db.Column(db.String(50), default='')
    original_batch_no = db.Column(db.String(100), default='')
    original_warehouse = db.Column(db.String(100), default='')

class GRN(db.Model):
    __tablename__ = 'grn'
    id = db.Column(db.Integer, primary_key=True)
    grn_number = db.Column(db.String(100), unique=True, nullable=False)
    grn_date = db.Column(db.DateTime, default=datetime.utcnow)
    supplier_name = db.Column(db.String(200), nullable=False)
    invoice_number = db.Column(db.String(100))
    invoice_date = db.Column(db.Date)
    warehouse_name = db.Column(db.String(100), nullable=False)
    total_amount = db.Column(db.Float, default=0)
    status = db.Column(db.String(50), default='Draft')
    created_by = db.Column(db.String(100))
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    remarks = db.Column(db.Text)

class GRNItem(db.Model):
    __tablename__ = 'grn_items'
    id = db.Column(db.Integer, primary_key=True)
    grn_id = db.Column(db.Integer, db.ForeignKey('grn.id'))
    sku_code = db.Column(db.String(100), nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    batch_number = db.Column(db.String(100), nullable=False)
    manufacturing_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date)
    quantity = db.Column(db.Integer, default=0)
    purchase_price = db.Column(db.Float, default=0)
    mrp = db.Column(db.Float, default=0)
    selling_price = db.Column(db.Float, default=0)
    condition = db.Column(db.String(50), default='Good')
    bin_no = db.Column(db.String(50))
    location_code = db.Column(db.String(100))
    remarks = db.Column(db.Text)

class TransferItem(db.Model):
    __tablename__ = 'transfer_items'
    id = db.Column(db.Integer, primary_key=True)
    transfer_id = db.Column(db.String(100), nullable=False)
    sku_code = db.Column(db.String(100), nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    batch_number = db.Column(db.String(100), nullable=False)
    bin_no = db.Column(db.String(50), nullable=False)
    dest_bin = db.Column(db.String(50), default='')
    quantity = db.Column(db.Integer, default=0)
    from_warehouse = db.Column(db.String(100), nullable=False)
    to_warehouse = db.Column(db.String(100), nullable=False)
    location_code = db.Column(db.String(100), default='')
    received_date = db.Column(db.Date, nullable=True)
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TransactionHistory(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    transaction_type = db.Column(db.String(100))
    reference_id = db.Column(db.String(100))
    details = db.Column(db.Text)
    username = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def calculate_shelf_life(expiry_date):
    if not expiry_date:
        return "No expiry date", 0
    
    today = datetime.now().date()
    
    if expiry_date < today:
        days_overdue = (today - expiry_date).days
        return f"Expired ({days_overdue} days ago)", 0
    
    days_remaining = (expiry_date - today).days
    months = days_remaining // 30
    days = days_remaining % 30
    total_expected_days = 365
    percentage = round((days_remaining / total_expected_days) * 100)
    if percentage > 100:
        percentage = 100
    
    if months > 0 and days > 0:
        return f"{months} months, {days} days", percentage
    elif months > 0:
        return f"{months} months", percentage
    else:
        return f"{days} days", percentage

def log_transaction(transaction_type, reference_id, details, username):
    try:
        transaction = TransactionHistory(
            transaction_type=transaction_type,
            reference_id=reference_id,
            details=details,
            username=username
        )
        db.session.add(transaction)
        db.session.commit()
    except Exception:
        db.session.rollback()

def generate_unique_order_id(base_id):
    existing = SalesOrder.query.filter_by(order_id=base_id).first()
    if not existing:
        return base_id
    
    timestamp = datetime.now().strftime('%H%M%S')
    random_num = random.randint(100, 999)
    new_id = f"{base_id}_{timestamp}_{random_num}"
    return generate_unique_order_id(new_id)

def is_valid_status_transition(current_status, new_status):
    if new_status == 'Cancelled':
        if current_status == 'Returned':
            return {'valid': False, 'message': '❌ Cannot cancel an already returned order!'}
        return {'valid': True, 'message': ''}
    
    if new_status == 'Returned':
        if current_status == 'Created':
            return {'valid': False, 'message': '❌ Cannot return an order that is only Created. Must be Invoiced or Shipped first!'}
        if current_status == 'Returned':
            return {'valid': False, 'message': '❌ Order already returned!'}
        if current_status == 'Cancelled':
            return {'valid': False, 'message': '❌ Cannot return a cancelled order!'}
        return {'valid': True, 'message': ''}
    
    if new_status == 'Invoiced':
        if current_status == 'Created':
            return {'valid': True, 'message': ''}
        if current_status == 'Invoiced':
            return {'valid': False, 'message': '❌ Order is already Invoiced!'}
        return {'valid': False, 'message': f'❌ Cannot move from {current_status} to Invoiced. Order must be Created first!'}
    
    if new_status == 'Shipped':
        if current_status == 'Invoiced':
            return {'valid': True, 'message': ''}
        if current_status == 'Shipped':
            return {'valid': False, 'message': '❌ Order is already Shipped!'}
        if current_status == 'Created':
            return {'valid': False, 'message': '❌ Cannot ship directly from Created. Must be Invoiced first!'}
        return {'valid': False, 'message': f'❌ Cannot move from {current_status} to Shipped. Order must be Invoiced first!'}
    
    return {'valid': False, 'message': '❌ Invalid status transition!'}

# ========== PAGE ROUTES ==========
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            log_transaction('LOGIN', username, f'User {username} logged in', username)
            return redirect(url_for('dashboard'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@app.route('/orders')
@login_required
def orders():
    return render_template('orders.html', user=current_user)

@app.route('/inventory')
@login_required
def inventory():
    return render_template('inventory.html', user=current_user)

@app.route('/stock-transfer')
@login_required
def stock_transfer():
    return render_template('stock_transfer.html', user=current_user)

@app.route('/grn')
@login_required
def grn():
    return render_template('grn.html', user=current_user)

@app.route('/reports')
@login_required
def reports():
    return render_template('reports.html', user=current_user)

@app.route('/users')
@login_required
def users():
    if current_user.role != 'admin':
        flash('Access denied. Admin rights required.')
        return redirect(url_for('dashboard'))
    return render_template('users.html', user=current_user)

@app.route('/transactions')
@login_required
def transactions():
    if current_user.role != 'admin':
        flash('Access denied. Admin rights required.')
        return redirect(url_for('dashboard'))
    return render_template('transactions.html', user=current_user)

@app.route('/logout')
@login_required
def logout():
    log_transaction('LOGOUT', current_user.username, f'User {current_user.username} logged out', current_user.username)
    logout_user()
    return redirect(url_for('login'))

# ========== API ROUTES ==========

@app.route('/api/test')
@login_required
def test_api():
    try:
        product_count = Product.query.count()
        return jsonify({
            'success': True,
            'message': 'API is working',
            'product_count': product_count,
            'user': current_user.username
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ========== PRODUCTS API ==========
@app.route('/api/products', methods=['GET', 'POST'])
@login_required
def products_api():
    if request.method == 'POST':
        try:
            data = request.get_json()
            existing = Product.query.filter_by(sku_code=data['sku_code'].upper()).first()
            if existing:
                return jsonify({'success': False, 'error': 'SKU already exists'}), 400
            
            product = Product(
                sku_code=data['sku_code'].upper(),
                product_name=data['product_name'],
                unit=data.get('unit', 'Pcs')
            )
            db.session.add(product)
            db.session.commit()
            
            log_transaction('PRODUCT_ADDED', product.sku_code, f'Added product: {product.product_name}', current_user.username)
            return jsonify({'success': True, 'message': 'Product added successfully', 'id': product.id})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    products = Product.query.all()
    return jsonify([{
        'sku_code': p.sku_code,
        'product_name': p.product_name,
        'unit': p.unit,
        'created_at': p.created_at.strftime('%Y-%m-%d %H:%M:%S') if p.created_at else None
    } for p in products])

@app.route('/api/products/<sku>', methods=['GET'])
@login_required
def get_product(sku):
    product = Product.query.filter_by(sku_code=sku.upper()).first()
    if product:
        return jsonify({
            'sku_code': product.sku_code,
            'product_name': product.product_name,
            'unit': product.unit
        })
    return jsonify({'error': 'Product not found'}), 404

@app.route('/api/products/update', methods=['PUT'])
@login_required
def update_product():
    try:
        data = request.get_json()
        product = Product.query.filter_by(sku_code=data['sku_code'].upper()).first()
        if not product:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        
        product.product_name = data['product_name']
        product.unit = data.get('unit', product.unit)
        db.session.commit()
        
        Inventory.query.filter_by(sku_code=data['sku_code'].upper()).update({'product_name': data['product_name']})
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Product updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ========== INVENTORY API ==========
@app.route('/api/inventory', methods=['GET', 'POST'])
@login_required
def inventory_api():
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            product = Product.query.filter_by(sku_code=data['sku_code'].upper()).first()
            if not product:
                return jsonify({'success': False, 'error': f'SKU Code {data["sku_code"]} not found. Please add product first.'}), 404
            
            bin_no = data.get('bin_no')
            if not bin_no or bin_no == '':
                if data['warehouse_name'] == 'Kaushambi':
                    kaushambi_bins = ['K-B01', 'K-B02', 'K-B03', 'K-B04']
                    bin_no = kaushambi_bins[Inventory.query.filter_by(warehouse_name='Kaushambi').count() % 4]
                else:
                    manak_bins = ['A-01', 'A-02', 'A-03', 'A-04', 'B-01', 'B-02', 'B-03', 'B-04', 
                                  'C-01', 'C-02', 'C-03', 'C-04', 'D-01', 'D-02', 'D-03', 'D-04', 
                                  'E-01', 'E-02', 'E-03', 'E-04', 'F-02', 'F-03', 'G-01', 'G-02', 'G-03', 'G-04']
                    bin_no = manak_bins[Inventory.query.filter_by(warehouse_name='Manak_Vihar').count() % len(manak_bins)]
            
            manufacturing_date = None
            expiry_date = None
            if data.get('manufacturing_date') and data['manufacturing_date'] != 'NA' and data['manufacturing_date']:
                try:
                    manufacturing_date = datetime.strptime(data['manufacturing_date'], '%Y-%m-%d').date()
                except:
                    manufacturing_date = None
            if data.get('expiry_date') and data['expiry_date'] != 'NA' and data['expiry_date']:
                try:
                    expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d').date()
                except:
                    expiry_date = None
            
            inventory = Inventory(
                sku_code=data['sku_code'].upper(),
                product_name=product.product_name,
                batch_number=data.get('batch_number', ''),
                manufacturing_date=manufacturing_date,
                expiry_date=expiry_date,
                quantity=int(data.get('quantity', 0)),
                purchase_price=float(data.get('purchase_price', 0)),
                mrp=float(data.get('mrp', 0)),
                selling_price=float(data.get('selling_price', 0)),
                condition=data.get('condition', 'Good'),
                bin_no=bin_no,
                warehouse_name=data.get('warehouse_name', 'Manak_Vihar'),
                location_code=data.get('location_code', ''),
                remarks=data.get('remarks', ''),
                updated_by=current_user.username
            )
            db.session.add(inventory)
            db.session.commit()
            
            log_transaction('STOCK_RECEIVED', inventory.sku_code, 
                           f'Received {inventory.quantity} units at {inventory.warehouse_name}, Batch: {inventory.batch_number}', 
                           current_user.username)
            
            return jsonify({'success': True, 'message': 'Stock received successfully', 'bin_no': bin_no})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    warehouse = request.args.get('warehouse', '')
    query = Inventory.query.filter(Inventory.quantity > 0)
    if warehouse:
        query = query.filter_by(warehouse_name=warehouse)
    
    items = []
    for inv in query.order_by(Inventory.expiry_date).all():
        shelf_life_text, shelf_life_percentage = calculate_shelf_life(inv.expiry_date)
        
        items.append({
            'id': inv.id,
            'sku_code': inv.sku_code,
            'product_name': inv.product_name,
            'batch_number': inv.batch_number,
            'quantity': inv.quantity,
            'purchase_price': inv.purchase_price,
            'mrp': inv.mrp,
            'selling_price': inv.selling_price,
            'manufacturing_date': inv.manufacturing_date.strftime('%Y-%m-%d') if inv.manufacturing_date else '',
            'expiry_date': inv.expiry_date.strftime('%Y-%m-%d') if inv.expiry_date else '',
            'condition': inv.condition,
            'bin_no': inv.bin_no,
            'location_code': inv.location_code,
            'warehouse_name': inv.warehouse_name,
            'remarks': inv.remarks,
            'updated_by': inv.updated_by,
            'updated_on': inv.updated_on.strftime('%Y-%m-%d %H:%M:%S') if inv.updated_on else '',
            'remaining_shelf_life': shelf_life_text,
            'shelf_life_percentage': shelf_life_percentage
        })
    return jsonify(items)

# ========== ORDERS API ==========

@app.route('/api/orders', methods=['GET'])
@login_required
def get_orders():
    try:
        orders = SalesOrder.query.order_by(SalesOrder.created_on.desc()).all()
        print(f"Total orders found: {len(orders)}")
        
        result = {}
        for order in orders:
            if order.order_id not in result:
                result[order.order_id] = {
                    'order_id': order.order_id,
                    'order_status': order.order_status,
                    'created_on': order.created_on.strftime('%Y-%m-%d %H:%M:%S') if order.created_on else '',
                    'created_by': order.created_by,
                    'order_date': order.order_date.strftime('%Y-%m-%d') if order.order_date else '',
                    'business_type': order.business_type or '',
                    'platform_name': order.platform_name or '',
                    'items': []
                }
            result[order.order_id]['items'].append({
                'sku_code': order.sku_code,
                'item_name': order.item_name,
                'quantity': order.quantity,
                'sale_value': float(order.sale_value),
                'batch_number': order.original_batch_no or '',
                'bin_no': order.original_bin_no or '',
                'warehouse_name': order.original_warehouse or 'Manak_Vihar'
            })
        
        return jsonify(list(result.values()))
    except Exception as e:
        print(f"Error in get_orders: {str(e)}")
        traceback.print_exc()
        return jsonify([]), 500


@app.route('/api/orders/advanced', methods=['POST'])
@login_required
def advanced_orders_api():
    try:
        data = request.get_json()
        print("=" * 60)
        print("Received order data:", data)
        
        user_order_id = data.get('order_id')
        order_date_str = data.get('order_date')
        business_type = data.get('business_type')
        platform_name = data.get('platform_name')
        payment_mode = data.get('payment_mode')
        items = data.get('items', [])
        
        current_location = data.get('warehouse_name') or 'Manak_Vihar'
        
        if not business_type:
            return jsonify({'success': False, 'error': 'Please select Business Type'}), 400
        if not platform_name:
            return jsonify({'success': False, 'error': 'Please select Platform Name'}), 400
        if not items:
            return jsonify({'success': False, 'error': 'No items in order'}), 400
        
        final_order_id = None
        
        if not user_order_id or user_order_id.strip() == '':
            final_order_id = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            print(f"Auto-generated order ID: {final_order_id}")
        else:
            existing = SalesOrder.query.filter_by(order_id=user_order_id).first()
            if existing:
                final_order_id = f"{user_order_id}-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
                print(f"⚠️ Order ID '{user_order_id}' already exists! Using auto-generated: {final_order_id}")
            else:
                final_order_id = user_order_id
                print(f"Using provided order ID: {final_order_id}")
        
        if order_date_str:
            try:
                order_date = datetime.strptime(order_date_str, '%Y-%m-%d')
                if order_date.date() > datetime.now().date():
                    return jsonify({'success': False, 'error': 'Cannot create order for future date'}), 400
            except:
                order_date = datetime.now()
        else:
            order_date = datetime.now()
        
        created_items = []
        for item in items:
            sku = item.get('sku_code')
            batch = item.get('batch_number')
            bin_no = item.get('bin_no')
            quantity = item.get('quantity')
            item_price = item.get('item_price')
            item_name = item.get('item_name')
            warehouse = item.get('warehouse_name', current_location)
            
            print(f"Processing: SKU={sku}, Batch={batch}, Bin={bin_no}, Qty={quantity}")
            
            inventory_item = Inventory.query.filter_by(
                sku_code=sku,
                batch_number=batch,
                bin_no=bin_no,
                condition='Good'
            ).first()
            
            if not inventory_item:
                inventory_item = Inventory.query.filter_by(
                    sku_code=sku,
                    batch_number=batch,
                    condition='Good'
                ).first()
            
            if not inventory_item:
                return jsonify({'success': False, 'error': f'Stock not found for SKU: {sku}, Batch: {batch}'}), 400
            
            if inventory_item.quantity < quantity:
                return jsonify({'success': False, 'error': f'Insufficient stock for {sku}. Available: {inventory_item.quantity}'}), 400
            
            inventory_item.quantity -= quantity
            inventory_item.updated_by = current_user.username
            inventory_item.updated_on = datetime.utcnow()
            
            order = SalesOrder(
                order_id=final_order_id,
                order_date=order_date,
                sku_code=sku,
                item_name=item_name,
                quantity=quantity,
                sale_value=quantity * item_price,
                created_by=current_user.username,
                inventory_id=inventory_item.id,
                payment_mode=payment_mode,
                business_type=business_type,
                platform_name=platform_name,
                original_bin_no=bin_no,
                original_batch_no=batch,
                original_warehouse=warehouse
            )
            db.session.add(order)
            created_items.append(order)
            print(f"Added order item for {sku}")
        
        db.session.commit()
        print(f"✅ Order {final_order_id} created successfully with {len(created_items)} items!")
        
        log_transaction('ORDER_CREATED_ADVANCED', final_order_id, 
                       f'Order created - Type: {business_type}, Platform: {platform_name}', 
                       current_user.username)
        
        return jsonify({'success': True, 'order_id': final_order_id, 'message': 'Order created successfully'})
    
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error in order creation: {str(e)}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/orders/<order_id>/status', methods=['PUT'])
@login_required
def update_order_status(order_id):
    try:
        data = request.get_json()
        new_status = data.get('status')
        orders = SalesOrder.query.filter_by(order_id=order_id).all()
        
        if not orders:
            return jsonify({'success': False, 'error': 'Order not found'}), 404
        
        current_status = orders[0].order_status
        
        validation = is_valid_status_transition(current_status, new_status)
        if not validation['valid']:
            return jsonify({'success': False, 'error': validation['message']}), 400
        
        if new_status in ['Cancelled', 'Returned']:
            for order in orders:
                inventory_item = Inventory.query.get(order.inventory_id)
                if inventory_item:
                    inventory_item.quantity += order.quantity
        
        for order in orders:
            order.order_status = new_status
        
        db.session.commit()
        log_transaction('ORDER_STATUS_UPDATED', order_id, f'Status changed from {current_status} to {new_status}', current_user.username)
        
        return jsonify({'success': True, 'message': f'Order status updated to {new_status}'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/orders/<order_id>', methods=['DELETE'])
@login_required
def delete_order(order_id):
    try:
        if current_user.role != 'admin':
            return jsonify({'success': False, 'error': 'Only admin can delete orders'}), 403
        
        orders = SalesOrder.query.filter_by(order_id=order_id).all()
        if not orders:
            return jsonify({'success': False, 'error': 'Order not found'}), 404
        
        for order in orders:
            db.session.delete(order)
        
        db.session.commit()
        log_transaction('ORDER_DELETED', order_id, f'Order {order_id} deleted by {current_user.username}', current_user.username)
        
        return jsonify({'success': True, 'message': f'Order {order_id} deleted successfully'})
    
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting order: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ========== SALES SUMMARY API ==========
@app.route('/api/sales-summary', methods=['GET'])
@login_required
def sales_summary():
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    month_start = today.replace(day=1)
    
    today_sales = db.session.query(db.func.sum(SalesOrder.sale_value)).filter(
        db.func.date(SalesOrder.created_on) == today,
        SalesOrder.order_status == 'Shipped'
    ).scalar() or 0
    
    yesterday_sales = db.session.query(db.func.sum(SalesOrder.sale_value)).filter(
        db.func.date(SalesOrder.created_on) == yesterday,
        SalesOrder.order_status == 'Shipped'
    ).scalar() or 0
    
    mtd_sales = db.session.query(db.func.sum(SalesOrder.sale_value)).filter(
        db.func.date(SalesOrder.created_on) >= month_start,
        SalesOrder.order_status == 'Shipped'
    ).scalar() or 0
    
    return jsonify({
        'today_sales': float(today_sales),
        'yesterday_sales': float(yesterday_sales),
        'mtd_sales': float(mtd_sales)
    })

# ========== REPORTS API ==========
@app.route('/api/reports/sales', methods=['GET'])
@login_required
def sales_report():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    warehouse = request.args.get('warehouse', '')
    
    query = SalesOrder.query
    if start_date and end_date:
        query = query.filter(
            db.func.date(SalesOrder.created_on) >= start_date,
            db.func.date(SalesOrder.created_on) <= end_date
        )
    if warehouse:
        query = query.filter(SalesOrder.original_warehouse == warehouse)
    
    reports = []
    for order in query.order_by(SalesOrder.created_on.desc()).all():
        reports.append({
            'order_date': order.order_date.strftime('%Y-%m-%d'),
            'order_id': order.order_id,
            'sku_code': order.sku_code,
            'item_name': order.item_name,
            'quantity': order.quantity,
            'sale_value': float(order.sale_value),
            'order_status': order.order_status,
            'payment_mode': order.payment_mode,
            'created_by': order.created_by,
            'created_on': order.created_on.strftime('%Y-%m-%d %H:%M:%S'),
            'business_type': order.business_type or '',
            'platform_name': order.platform_name or ''
        })
    return jsonify(reports)

@app.route('/api/reports/returns', methods=['GET'])
@login_required
def return_report():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    warehouse = request.args.get('warehouse', '')
    
    query = SalesOrder.query.filter(SalesOrder.order_status == 'Returned')
    if start_date and end_date:
        query = query.filter(
            db.func.date(SalesOrder.created_on) >= start_date,
            db.func.date(SalesOrder.created_on) <= end_date
        )
    if warehouse:
        query = query.filter(SalesOrder.original_warehouse == warehouse)
    
    reports = []
    for order in query.order_by(SalesOrder.created_on.desc()).all():
        reports.append({
            'order_date': order.order_date.strftime('%Y-%m-%d'),
            'order_id': order.order_id,
            'sku_code': order.sku_code,
            'item_name': order.item_name,
            'quantity': order.quantity,
            'sale_value': float(order.sale_value),
            'order_status': order.order_status,
            'payment_mode': order.payment_mode,
            'created_by': order.created_by,
            'created_on': order.created_on.strftime('%Y-%m-%d %H:%M:%S')
        })
    return jsonify(reports)

@app.route('/api/reports/cancelled', methods=['GET'])
@login_required
def cancelled_report():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    warehouse = request.args.get('warehouse', '')
    
    query = SalesOrder.query.filter(SalesOrder.order_status == 'Cancelled')
    if start_date and end_date:
        query = query.filter(
            db.func.date(SalesOrder.created_on) >= start_date,
            db.func.date(SalesOrder.created_on) <= end_date
        )
    if warehouse:
        query = query.filter(SalesOrder.original_warehouse == warehouse)
    
    reports = []
    for order in query.order_by(SalesOrder.created_on.desc()).all():
        reports.append({
            'order_date': order.order_date.strftime('%Y-%m-%d'),
            'order_id': order.order_id,
            'sku_code': order.sku_code,
            'item_name': order.item_name,
            'quantity': order.quantity,
            'sale_value': float(order.sale_value),
            'order_status': order.order_status,
            'payment_mode': order.payment_mode,
            'created_by': order.created_by,
            'created_on': order.created_on.strftime('%Y-%m-%d %H:%M:%S'),
            'business_type': order.business_type or '',
            'platform_name': order.platform_name or ''
        })
    return jsonify(reports)

@app.route('/api/reports/expiry-alert', methods=['GET'])
@login_required
def expiry_alert():
    six_months_later = datetime.now().date() + timedelta(days=180)
    today = datetime.now().date()
    warehouse = request.args.get('warehouse', '')
    
    query = Inventory.query.filter(
        Inventory.expiry_date <= six_months_later,
        Inventory.expiry_date >= today,
        Inventory.quantity > 0
    )
    if warehouse:
        query = query.filter_by(warehouse_name=warehouse)
    
    items = query.order_by(Inventory.expiry_date).all()
    result = []
    for item in items:
        shelf_life, percentage = calculate_shelf_life(item.expiry_date)
        result.append({
            'sku_code': item.sku_code,
            'product_name': item.product_name,
            'batch_number': item.batch_number,
            'manufacturing_date': item.manufacturing_date.strftime('%Y-%m-%d') if item.manufacturing_date else '',
            'expiry_date': item.expiry_date.strftime('%Y-%m-%d') if item.expiry_date else '',
            'bin_no': item.bin_no,
            'quantity': item.quantity,
            'remaining_shelf_life': shelf_life,
            'shelf_life_percentage': percentage
        })
    return jsonify(result)

@app.route('/api/reports/expired-stock', methods=['GET'])
@login_required
def expired_stock():
    today = datetime.now().date()
    warehouse = request.args.get('warehouse', '')
    
    query = Inventory.query.filter(
        Inventory.expiry_date < today,
        Inventory.quantity > 0
    )
    if warehouse:
        query = query.filter_by(warehouse_name=warehouse)
    
    items = query.order_by(Inventory.expiry_date).all()
    result = []
    for item in items:
        result.append({
            'sku_code': item.sku_code,
            'product_name': item.product_name,
            'batch_number': item.batch_number,
            'manufacturing_date': item.manufacturing_date.strftime('%Y-%m-%d') if item.manufacturing_date else '',
            'expiry_date': item.expiry_date.strftime('%Y-%m-%d') if item.expiry_date else '',
            'bin_no': item.bin_no,
            'quantity': item.quantity
        })
    return jsonify(result)

# ========== STOCK TRANSFER API ==========

@app.route('/api/stock-transfer', methods=['GET', 'POST'])
@login_required
def stock_transfer_api():
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            from_warehouse = data.get('from_warehouse')
            to_warehouse = data.get('to_warehouse')
            items = data.get('items', [])
            transfer_reason = data.get('transfer_reason', '')
            transfer_date = data.get('transfer_date', datetime.now().strftime('%Y-%m-%d'))
            transfer_ref_no = data.get('transfer_ref_no', '')
            
            if not from_warehouse or not to_warehouse:
                return jsonify({'success': False, 'error': 'Please select source and destination warehouses'}), 400
            if not items:
                return jsonify({'success': False, 'error': 'No items to transfer'}), 400
            
            if transfer_ref_no:
                transfer_id = transfer_ref_no
            else:
                transfer_id = f"TRF-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            existing = TransferItem.query.filter_by(transfer_id=transfer_id).first()
            if existing:
                transfer_id = f"TRF-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            
            transferred_items = []
            
            for item in items:
                sku = item.get('sku_code')
                batch = item.get('batch_number')
                bin_no = item.get('bin_no')
                quantity = item.get('quantity')
                product_name = item.get('product_name', '')
                remarks = item.get('remarks', '')
                
                print(f"Processing: SKU={sku}, Batch={batch}, Bin={bin_no}, Qty={quantity}")
                
                source_inventory = Inventory.query.filter_by(
                    sku_code=sku,
                    batch_number=batch,
                    bin_no=bin_no,
                    warehouse_name=from_warehouse,
                    condition='Good'
                ).first()
                
                if not source_inventory:
                    source_inventory = Inventory.query.filter_by(
                        sku_code=sku,
                        batch_number=batch,
                        warehouse_name=from_warehouse,
                        condition='Good'
                    ).first()
                
                if not source_inventory:
                    return jsonify({
                        'success': False, 
                        'error': f'Stock not found: {sku} in {from_warehouse}, Bin: {bin_no}'
                    }), 400
                
                if source_inventory.quantity < quantity:
                    return jsonify({
                        'success': False, 
                        'error': f'Insufficient stock: {sku}. Available: {source_inventory.quantity}, Requested: {quantity}'
                    }), 400
                
                source_inventory.quantity -= quantity
                source_inventory.updated_by = current_user.username
                source_inventory.updated_on = datetime.utcnow()
                
                transfer_item = TransferItem(
                    transfer_id=transfer_id,
                    sku_code=sku,
                    product_name=product_name or source_inventory.product_name,
                    batch_number=batch,
                    bin_no=bin_no,
                    quantity=quantity,
                    from_warehouse=from_warehouse,
                    to_warehouse=to_warehouse,
                    remarks=remarks
                )
                db.session.add(transfer_item)
                
                transferred_items.append({
                    'sku_code': sku,
                    'batch_number': batch,
                    'bin_no': bin_no,
                    'quantity': quantity
                })
            
            log_transaction('STOCK_TRANSFER', transfer_id, 
                           f'Transferred {len(transferred_items)} items from {from_warehouse} to {to_warehouse}', 
                           current_user.username)
            
            db.session.commit()
            
            return jsonify({
                'success': True, 
                'transfer_id': transfer_id, 
                'message': f'Successfully transferred {len(transferred_items)} items'
            })
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {str(e)}")
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    transfers = TransactionHistory.query.filter_by(
        transaction_type='STOCK_TRANSFER'
    ).order_by(TransactionHistory.timestamp.desc()).all()
    
    result = []
    for t in transfers:
        transfer_items = TransferItem.query.filter_by(transfer_id=t.reference_id).all()
        items_list = []
        for item in transfer_items:
            items_list.append({
                'sku_code': item.sku_code,
                'product_name': item.product_name,
                'batch_number': item.batch_number,
                'bin_no': item.bin_no,
                'dest_bin': item.dest_bin or '',
                'quantity': item.quantity,
                'from_warehouse': item.from_warehouse,
                'to_warehouse': item.to_warehouse,
                'location_code': item.location_code or '',
                'received_date': item.received_date.strftime('%Y-%m-%d') if item.received_date else '',
                'remarks': item.remarks
            })
        
        result.append({
            'transfer_id': t.reference_id,
            'details': t.details,
            'username': t.username,
            'timestamp': t.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'items': items_list
        })
    return jsonify(result)


@app.route('/api/stock-transfer/items', methods=['GET'])
@login_required
def get_transfer_items():
    warehouse = request.args.get('warehouse', '')
    sku = request.args.get('sku', '')
    
    query = Inventory.query.filter(
        Inventory.quantity > 0,
        Inventory.condition == 'Good'
    )
    
    if warehouse:
        query = query.filter_by(warehouse_name=warehouse)
    if sku:
        query = query.filter_by(sku_code=sku.upper())
    
    items = []
    for inv in query.order_by(Inventory.expiry_date).all():
        items.append({
            'id': inv.id,
            'sku_code': inv.sku_code,
            'product_name': inv.product_name,
            'batch_number': inv.batch_number,
            'bin_no': inv.bin_no,
            'quantity': inv.quantity,
            'expiry_date': inv.expiry_date.strftime('%Y-%m-%d') if inv.expiry_date else '',
            'warehouse_name': inv.warehouse_name
        })
    return jsonify(items)


@app.route('/api/stock-transfer/receive', methods=['POST'])
@login_required
def receive_stock_transfer():
    try:
        data = request.get_json()
        transfer_id = data.get('transfer_id')
        receive_date = data.get('receive_date', datetime.now().strftime('%Y-%m-%d'))
        received_items = data.get('received_items', [])
        remarks = data.get('remarks', '')
        
        transfer_items = TransferItem.query.filter_by(transfer_id=transfer_id).all()
        
        if not transfer_items:
            return jsonify({'success': False, 'error': 'Transfer not found'}), 404
        
        if transfer_items[0].received_date:
            return jsonify({'success': False, 'error': f'Transfer {transfer_id} has already been received on {transfer_items[0].received_date}'}), 400
        
        for idx, item in enumerate(transfer_items):
            dest_bin = received_items[idx].get('dest_bin') if idx < len(received_items) else item.bin_no
            location_code = received_items[idx].get('location_code') if idx < len(received_items) else ''
            
            source_inventory = Inventory.query.filter_by(
                sku_code=item.sku_code,
                batch_number=item.batch_number,
                bin_no=item.bin_no,
                warehouse_name=item.from_warehouse
            ).first()
            
            if not source_inventory:
                source_inventory = Inventory.query.filter_by(
                    sku_code=item.sku_code,
                    batch_number=item.batch_number,
                    warehouse_name=item.from_warehouse
                ).first()
            
            dest_inventory = Inventory.query.filter_by(
                sku_code=item.sku_code,
                batch_number=item.batch_number,
                bin_no=dest_bin,
                warehouse_name=item.to_warehouse
            ).first()
            
            if dest_inventory:
                dest_inventory.quantity += item.quantity
                dest_inventory.updated_by = current_user.username
                dest_inventory.updated_on = datetime.utcnow()
                dest_inventory.location_code = location_code
                if remarks:
                    dest_inventory.remarks = f"Received from transfer {transfer_id} - {remarks}"
            else:
                new_inventory = Inventory(
                    sku_code=item.sku_code,
                    product_name=item.product_name,
                    batch_number=item.batch_number,
                    quantity=item.quantity,
                    purchase_price=source_inventory.purchase_price if source_inventory else 0,
                    mrp=source_inventory.mrp if source_inventory else 0,
                    selling_price=source_inventory.selling_price if source_inventory else 0,
                    manufacturing_date=source_inventory.manufacturing_date if source_inventory else None,
                    expiry_date=source_inventory.expiry_date if source_inventory else None,
                    condition=source_inventory.condition if source_inventory else 'Good',
                    bin_no=dest_bin,
                    warehouse_name=item.to_warehouse,
                    location_code=location_code,
                    remarks=f"Received from transfer {transfer_id} - {remarks}",
                    updated_by=current_user.username,
                    updated_on=datetime.utcnow()
                )
                db.session.add(new_inventory)
            
            item.dest_bin = dest_bin
            item.location_code = location_code
            item.received_date = datetime.strptime(receive_date, '%Y-%m-%d').date()
        
        db.session.commit()
        
        log_transaction('TRANSFER_RECEIVED', transfer_id, 
                       f'Transfer {transfer_id} received by {current_user.username}', 
                       current_user.username)
        
        return jsonify({'success': True, 'message': f'Transfer {transfer_id} received successfully!'})
    
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error: {str(e)}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# ========== GRN API ==========

@app.route('/api/grn', methods=['GET', 'POST'])
@login_required
def grn_api():
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            grn_number = data.get('grn_number')
            grn_date = data.get('grn_date')
            supplier_name = data.get('supplier_name')
            invoice_number = data.get('invoice_number')
            invoice_date = data.get('invoice_date')
            warehouse_name = data.get('warehouse_name')
            items = data.get('items', [])
            remarks = data.get('remarks', '')
            
            if not grn_number:
                grn_number = f"GRN-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            if not supplier_name:
                return jsonify({'success': False, 'error': 'Please enter supplier name'}), 400
            if not warehouse_name:
                return jsonify({'success': False, 'error': 'Please select warehouse'}), 400
            if not items:
                return jsonify({'success': False, 'error': 'No items to receive'}), 400
            
            existing = GRN.query.filter_by(grn_number=grn_number).first()
            if existing:
                grn_number = f"GRN-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(100, 999)}"
            
            if grn_date:
                try:
                    grn_date_obj = datetime.strptime(grn_date, '%Y-%m-%d').date()
                    grn_datetime = datetime.combine(grn_date_obj, datetime.min.time())
                except:
                    grn_datetime = datetime.now()
            else:
                grn_datetime = datetime.now()
            
            invoice_date_obj = None
            if invoice_date:
                try:
                    invoice_date_obj = datetime.strptime(invoice_date, '%Y-%m-%d').date()
                except:
                    invoice_date_obj = None
            
            total_amount = sum(item.get('quantity', 0) * item.get('purchase_price', 0) for item in items)
            
            grn = GRN(
                grn_number=grn_number,
                grn_date=grn_datetime,
                supplier_name=supplier_name,
                invoice_number=invoice_number,
                invoice_date=invoice_date_obj,
                warehouse_name=warehouse_name,
                total_amount=total_amount,
                status='Completed',
                created_by=current_user.username,
                remarks=remarks
            )
            db.session.add(grn)
            db.session.flush()
            
            for item in items:
                sku = item.get('sku_code')
                product_name = item.get('product_name')
                batch = item.get('batch_number')
                mfg_date = item.get('manufacturing_date')
                exp_date = item.get('expiry_date')
                quantity = item.get('quantity')
                purchase_price = item.get('purchase_price')
                mrp = item.get('mrp')
                selling_price = item.get('selling_price')
                condition = item.get('condition', 'Good')
                bin_no = item.get('bin_no')
                location_code = item.get('location_code')
                item_remarks = item.get('remarks', '')
                
                product = Product.query.filter_by(sku_code=sku.upper()).first()
                if not product:
                    product = Product(
                        sku_code=sku.upper(),
                        product_name=product_name,
                        unit='Pcs'
                    )
                    db.session.add(product)
                    db.session.flush()
                
                if not bin_no:
                    if warehouse_name == 'Kaushambi':
                        kaushambi_bins = ['K-B01', 'K-B02', 'K-B03', 'K-B04']
                        bin_no = kaushambi_bins[Inventory.query.filter_by(warehouse_name='Kaushambi').count() % 4]
                    else:
                        manak_bins = ['A-01', 'A-02', 'A-03', 'A-04', 'B-01', 'B-02', 'B-03', 'B-04', 
                                      'C-01', 'C-02', 'C-03', 'C-04', 'D-01', 'D-02', 'D-03', 'D-04', 
                                      'E-01', 'E-02', 'E-03', 'E-04', 'F-02', 'F-03', 'G-01', 'G-02', 'G-03', 'G-04']
                        bin_no = manak_bins[Inventory.query.filter_by(warehouse_name='Manak_Vihar').count() % len(manak_bins)]
                
                inventory = Inventory(
                    sku_code=sku.upper(),
                    product_name=product_name,
                    batch_number=batch,
                    manufacturing_date=datetime.strptime(mfg_date, '%Y-%m-%d').date() if mfg_date else None,
                    expiry_date=datetime.strptime(exp_date, '%Y-%m-%d').date() if exp_date else None,
                    quantity=quantity,
                    purchase_price=purchase_price,
                    mrp=mrp,
                    selling_price=selling_price,
                    condition=condition,
                    bin_no=bin_no,
                    warehouse_name=warehouse_name,
                    location_code=location_code,
                    remarks=f"GRN: {grn_number} - {item_remarks}",
                    updated_by=current_user.username
                )
                db.session.add(inventory)
                
                grn_item = GRNItem(
                    grn_id=grn.id,
                    sku_code=sku.upper(),
                    product_name=product_name,
                    batch_number=batch,
                    manufacturing_date=datetime.strptime(mfg_date, '%Y-%m-%d').date() if mfg_date else None,
                    expiry_date=datetime.strptime(exp_date, '%Y-%m-%d').date() if exp_date else None,
                    quantity=quantity,
                    purchase_price=purchase_price,
                    mrp=mrp,
                    selling_price=selling_price,
                    condition=condition,
                    bin_no=bin_no,
                    location_code=location_code,
                    remarks=item_remarks
                )
                db.session.add(grn_item)
            
            db.session.commit()
            
            log_transaction('GRN_CREATED', grn_number, 
                           f'Created GRN with {len(items)} items from {supplier_name}', 
                           current_user.username)
            
            return jsonify({'success': True, 'grn_number': grn_number, 'message': 'GRN created successfully'})
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error in GRN creation: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    grn_list = GRN.query.order_by(GRN.created_on.desc()).all()
    result = []
    for grn in grn_list:
        result.append({
            'id': grn.id,
            'grn_number': grn.grn_number,
            'grn_date': grn.grn_date.strftime('%Y-%m-%d %H:%M:%S'),
            'supplier_name': grn.supplier_name,
            'invoice_number': grn.invoice_number,
            'warehouse_name': grn.warehouse_name,
            'total_amount': grn.total_amount,
            'status': grn.status,
            'created_by': grn.created_by,
            'created_on': grn.created_on.strftime('%Y-%m-%d %H:%M:%S'),
            'remarks': grn.remarks
        })
    return jsonify(result)

@app.route('/api/grn/<int:grn_id>', methods=['GET'])
@login_required
def get_grn_details(grn_id):
    grn = GRN.query.get(grn_id)
    if not grn:
        return jsonify({'error': 'GRN not found'}), 404
    
    items = GRNItem.query.filter_by(grn_id=grn_id).all()
    items_list = []
    for item in items:
        items_list.append({
            'sku_code': item.sku_code,
            'product_name': item.product_name,
            'batch_number': item.batch_number,
            'manufacturing_date': item.manufacturing_date.strftime('%Y-%m-%d') if item.manufacturing_date else '',
            'expiry_date': item.expiry_date.strftime('%Y-%m-%d') if item.expiry_date else '',
            'quantity': item.quantity,
            'purchase_price': item.purchase_price,
            'mrp': item.mrp,
            'selling_price': item.selling_price,
            'condition': item.condition,
            'bin_no': item.bin_no,
            'location_code': item.location_code,
            'remarks': item.remarks
        })
    
    return jsonify({
        'id': grn.id,
        'grn_number': grn.grn_number,
        'grn_date': grn.grn_date.strftime('%Y-%m-%d %H:%M:%S'),
        'supplier_name': grn.supplier_name,
        'invoice_number': grn.invoice_number,
        'invoice_date': grn.invoice_date.strftime('%Y-%m-%d') if grn.invoice_date else '',
        'warehouse_name': grn.warehouse_name,
        'total_amount': grn.total_amount,
        'status': grn.status,
        'created_by': grn.created_by,
        'created_on': grn.created_on.strftime('%Y-%m-%d %H:%M:%S'),
        'remarks': grn.remarks,
        'items': items_list
    })

# ========== USERS API ==========

@app.route('/api/users', methods=['GET', 'POST'])
@login_required
def manage_users():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized. Admin access required.'}), 403
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            existing = User.query.filter_by(username=data['username']).first()
            if existing:
                return jsonify({'error': 'Username already exists'}), 400
            
            user = User(
                username=data['username'],
                password=generate_password_hash(data['password']),
                role=data.get('role', 'user'),
                full_name=data.get('full_name', ''),
                email=data.get('email', '')
            )
            db.session.add(user)
            db.session.commit()
            
            log_transaction('USER_CREATED', data['username'], f'New user created with role {data.get("role", "user")}', current_user.username)
            return jsonify({'success': True, 'message': 'User created successfully'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    users = User.query.all()
    return jsonify([{
        'id': u.id,
        'username': u.username,
        'full_name': u.full_name or '',
        'email': u.email or '',
        'role': u.role,
        'created_at': u.created_at.strftime('%Y-%m-%d %H:%M:%S') if u.created_at else None
    } for u in users])


@app.route('/api/users/<int:user_id>/details', methods=['PUT'])
@login_required
def update_user_details(user_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    user.full_name = data.get('full_name', user.full_name)
    user.email = data.get('email', user.email)
    db.session.commit()
    
    log_transaction('USER_DETAILS_UPDATED', user.username, f'Details updated by {current_user.username}', current_user.username)
    return jsonify({'success': True, 'message': 'User details updated successfully'})


@app.route('/api/users/<int:user_id>/password', methods=['PUT'])
@login_required
def reset_user_password(user_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    user.password = generate_password_hash(data['password'])
    db.session.commit()
    
    log_transaction('PASSWORD_RESET', user.username, f'Password reset by {current_user.username}', current_user.username)
    return jsonify({'success': True, 'message': 'Password reset successfully'})


@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if user.username == 'admin':
        return jsonify({'error': 'Cannot delete main admin user'}), 400
    
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot delete your own account'}), 400
    
    db.session.delete(user)
    db.session.commit()
    
    log_transaction('USER_DELETED', user.username, f'User {user.username} deleted', current_user.username)
    return jsonify({'success': True, 'message': 'User deleted successfully'})


@app.route('/api/users/<int:user_id>/role', methods=['PUT'])
@login_required
def update_user_role(user_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    user.role = data.get('role', user.role)
    db.session.commit()
    
    log_transaction('USER_ROLE_UPDATED', user.username, f'Role changed to {user.role}', current_user.username)
    return jsonify({'success': True, 'message': 'User role updated successfully'})


# ========== TRANSACTION HISTORY API ==========
@app.route('/api/transactions', methods=['GET'])
@login_required
def get_transactions():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized. Admin access required.'}), 403
    
    limit = request.args.get('limit', 500, type=int)
    transactions = TransactionHistory.query.order_by(TransactionHistory.timestamp.desc()).limit(limit).all()
    
    return jsonify([{
        'id': t.id,
        'transaction_type': t.transaction_type,
        'reference_id': t.reference_id,
        'details': t.details,
        'username': t.username,
        'timestamp': t.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    } for t in transactions])

# ========== DASHBOARD STATS API ==========
@app.route('/api/dashboard/stats', methods=['GET'])
@login_required
def dashboard_stats():
    today = datetime.now().date()
    
    total_products = Product.query.count()
    total_inventory_mrp_value = db.session.query(db.func.sum(Inventory.quantity * Inventory.mrp)).scalar() or 0
    low_stock = Inventory.query.filter(Inventory.quantity < 10, Inventory.quantity > 0).count()
    orders_today = SalesOrder.query.filter(
        db.func.date(SalesOrder.created_on) == today
    ).distinct(SalesOrder.order_id).count()
    
    return jsonify({
        'total_products': total_products,
        'total_inventory_mrp_value': float(total_inventory_mrp_value),
        'low_stock_items': low_stock,
        'orders_today': orders_today
    })

# ========== MAIN ENTRY POINT ==========
if __name__ == '__main__':
    with app.app_context():
        print("\n" + "=" * 60)
        print("🔄 Creating database tables...")
        
        db.create_all()
        print("✅ Tables created successfully!")
        
        # Add new columns to users table if not exists
        try:
            db.session.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS full_name VARCHAR(200)")
            db.session.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS email VARCHAR(200)")
            db.session.commit()
            print("✅ Added full_name and email columns to users table")
        except Exception as e:
            print(f"Note: {e}")
        
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                password=generate_password_hash('admin123'),
                role='admin',
                full_name='Administrator',
                email='admin@imspro.com'
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user created: admin / admin123")
        else:
            print("✅ Admin user already exists")
        
        print("=" * 60)
    
    # Production server ke liye - Render automatically PORT environment variable set karega
    port = int(os.environ.get('PORT', 5000))
    
    print("\n" + "=" * 60)
    print("🚀 INVENTORY MANAGEMENT SYSTEM STARTED!")
    print(f"📍 Access at: http://localhost:{port}")
    print("🔐 Login: admin / admin123")
    print("=" * 60 + "\n")
    
    # Production mode mein debug=False
    app.run(debug=False, host='0.0.0.0', port=port)