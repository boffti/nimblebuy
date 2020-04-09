from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

database_path = 'sqlite:///sfv_veggies.db'

db = SQLAlchemy()
def db_init(app):
    app.config.from_object('config')
    db.app = app
    db.init_app(app)
    migrate = Migrate(app, db)
    return db

class Vegetable(db.Model):
    __tablename__ = 'vegetables'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    price = db.Column(db.Float)
    image = db.Column(db.String(120))
    onSale = db.Column(db.Boolean, default=True)

    order_details = db.relationship('OrderDetails', backref='ordered_item')

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'image': self.image,
            'onSale': self.onSale
        }
    
    def format2(self):
        return({
            self.id : {
            'name': self.name,
            'price': self.price,
            'image': self.image,
            'onSale': self.onSale
        }
        })

    def __repr__(self):
        return f'<Vegetable {self.id} {self.name}>'

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String)
    password = db.Column(db.String)
    fname = db.Column(db.String)
    apt = db.Column(db.Integer)

    orders = db.relationship('Order', backref='customer')

    def __init__(self, fname, apt, phone, password):
        self.fname = fname
        self.apt = apt
        self.phone = phone
        self.password = password

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'phone': self.phone,
            'fname': self.fname,
            'apt': self.apt,
        }

    def __repr__(self):
        return f'<User {self.id} {self.fname}>'

class Stock(db.Model):
    __tablename__ = 'stock'
    id = db.Column(db.Integer, primary_key=True)
    in_stock = db.Column(db.Boolean, default = True)
    stock = db.Column(db.Float)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f'<Stock {self.id} {self.stock}>'

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_number = db.Column(db.String)
    order_date = db.Column(db.String)

    order_details = db.relationship('OrderDetails', backref='order')

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'order_number': self.order_number,
            'order_date': self.order_date
        }

    def __repr__(self):
        return f'<Order {self.id} {self.customer_id}>'

class OrderDetails(db.Model):
    __tablename__ = 'order_details'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('vegetables.id'))
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    price = db.Column(db.String)
    qty = db.Column(db.String)
    total = db.Column(db.String)

    def format(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'order_id': self.order_id,
            'price': self.price,
            'qty': self.qty,
            'total': self.total
        }

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f'<OrderDetails {self.id} {self.price}>'

class Testimonial(db.Model):
    __tablename__ = 'testimonials'
    id = db.Column(db.Integer, primary_key=True)
    testimonial = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def format(self):
        return({
            self.id : {
            'name': self.name,
            'testimonial': self.testimonial,
        }
        })   

