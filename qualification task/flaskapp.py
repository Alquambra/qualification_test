# Python 3.8


from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://iwsyqfiw:h8TEb9kYFp3-kE-KtjPooskvcrGyTAvb@hattie.db.elephantsql.com:5432/iwsyqfiw'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Category(db.Model):
    """Таблица с категориями товаров"""
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    def __init__(self, name):
        self.name = name


class Producer(db.Model):
    """Таблица с производителями товаров"""
    __tablename__ = 'producer'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    def __init__(self, name):
        self.name = name


class HardwareGood(db.Model):
    """Таблица с параметрами товара"""
    __tablename__ = 'hardware_good'
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    producer_id = db.Column(db.Integer, db.ForeignKey('producer.id'))
    photo = db.Column(db.LargeBinary, nullable=True)
    price = db.Column(db.Integer)
    description = db.Column(db.String)
    quantity = db.Column(db.Integer, default=10)

    def __init__(self, category_id, producer_id, photo, price, description):
        self.category_id = category_id
        self.producer_id = producer_id
        self.photo = photo
        self.price = price
        self.description = description


class User(db.Model):
    """Таблица с данными пользователей"""
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    # telegram_id = db.Column(db.Integer)
    name = db.Column(db.String(50), unique=True)
    phone = db.Column(db.String(50), unique=True)


class Order(db.Model):
    """Таблица с данными заказов"""
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    good_id = db.Column(db.Integer, db.ForeignKey('hardware_good.id'))
    status = db.Column(db.String(50))


# @app.route('/', methods=['GET'])
# def index():
#     """Главная страница"""
#     return render_template('index.html')


@app.route('/shop', methods=['GET'])
def get_all_categories():
    """Страница с доступными категориями товаров"""
    all_categories = db.session.query(Category).all()
    output = []
    for category in all_categories:
        category_data = {}
        category_data['id'] = category.id
        category_data['name'] = category.name
        output.append(category_data)
    return jsonify({'categories': output})


@app.route('/shop/<category>', methods=['GET'])
def get_producers_by_categories(category):
    """Страница с доступными производителями товаров с фильтром по категории"""
    producers_by_categories = db.session.query(Producer).distinct(Producer.name) \
        .join(HardwareGood, HardwareGood.producer_id == Producer.id) \
        .join(Category, Category.id == HardwareGood.category_id) \
        .filter(Category.name == category.replace('+', ' ')).all()
    output = []
    for producer in producers_by_categories:
        producer_data = {}
        producer_data['id'] = producer.id
        producer_data['name'] = producer.name
        output.append(producer_data)
    return jsonify({'producers': output})


@app.route('/shop/<category>/<producer>', methods=['GET'])
def get_goods_by_producers(category, producer):
    """Страница с доступными товарами с фильтром по производителю и категории"""
    goods_by_producers = db.session.query(Category.name.label('category'), Producer.name.label('producer'),
                                          HardwareGood.photo, HardwareGood.description, HardwareGood.price,
                                          HardwareGood.quantity) \
        .join(Category, HardwareGood.category_id == Category.id) \
        .join(Producer, HardwareGood.producer_id == Producer.id) \
        .filter(Category.name == category.replace('+', ' '), Producer.name == producer).all()
    output = []
    for good in goods_by_producers:
        good_data = {}
        good_data['category'] = good.category
        good_data['producer'] = good.producer
        good_data['photo'] = good.photo
        good_data['description'] = good.description
        good_data['price'] = good.price
        good_data['quantity'] = good.quantity
        output.append(good_data)
    return jsonify({'goods': output})


# @app.route('/category', methods=['GET'])
# def category():
#     all_categories = db.session.query(Category.name).all()
#     payload = all_categories
#     print(request.args)
#     if request.method == 'GET':
#         if request.args.get('cat'):
#             category = request.args.get('cat')
#             producers_by_categories = db.session.query(Producer.name).distinct(Producer.name) \
#                 .join(HardwareGood, HardwareGood.producer_id == Producer.id) \
#                 .join(Category, Category.id == HardwareGood.category_id) \
#                 .filter(Category.name == category).all()
#             if request.args.get('pro'):
#                 producer = request.args.get('pro')
#                 goods_by_producers = db.session.query(HardwareGood)\
#                     .join(Category, HardwareGood.category_id == Category.id)\
#                     .join(Producer, HardwareGood.producer_id == Producer.id)\
#                     .filter(Category.name == category, Producer.name == producer).all()
#                 return render_template('category.html', category=category, producer=producer, goods=goods_by_producers)
#             return render_template('category.html', category=category, producers=producers_by_categories)
#     return render_template('category.html', categories=payload)


@app.route('/user', methods=['GET'])
def get_all_users():
    """Страница с данными всех пользователей"""
    users = db.session.query(User).all()
    output = []
    for user in users:
        user_data = {}
        user_data['id'] = user.id
        user_data['name'] = user.name
        user_data['phone'] = user.phone
        output.append(user_data)
    return jsonify({'users': output})


@app.route('/user/<user_id>', methods=['GET'])
def get_one_user(user_id):
    """Страница с данными пользователя по его id"""
    user = db.session.query(User).filter(User.id == user_id).first()
    if not user:
        return jsonify({'message': 'Пользователь не найден'})
    user_data = {}
    user_data['id'] = user.id
    user_data['name'] = user.name
    user_data['phone'] = user.phone
    return jsonify({'user': user_data})


@app.route('/user', methods=['POST'])
def create_user():
    """Добавление пользователя в базу данных"""
    data = request.get_json()
    new_user = User(name=data['name'], phone=str(data['phone']))
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'Создан новый пользователь'})


@app.route('/user/<user_id>', methods=['DElETE'])
def delete_user(user_id):
    """Удаление пользователя из базы данных"""
    user = db.session.query(User).filter(User.id == user_id).first()
    if not user:
        return jsonify({'message': 'Пользователь не найден'})
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'Пользователь удален'})


@app.route('/order', methods=['GET'])
def get_all_orders():
    """Страница со всеми заказами с фильтром по номеру телефона пользователя"""
    data = request.get_json()
    orders = db.session.query(Order.id, Order.user_id, Order.status, HardwareGood.price, HardwareGood.description,
                         Producer.name.label('producer'), Category.name.label('category'))\
        .join(HardwareGood, Order.good_id == HardwareGood.id)\
        .join(Producer, HardwareGood.producer_id == Producer.id)\
        .join(Category, HardwareGood.category_id == Category.id)\
        .join(User, Order.user_id == User.id)\
        .filter(User.phone == data['phone']).all()
    output = []
    for order in orders:
        order_data = {}
        order_data['id'] = order.id
        order_data['user_id'] = order.user_id
        order_data['category'] = order.category
        order_data['producer'] = order.producer
        order_data['description'] = order.description
        order_data['price'] = order.price
        order_data['status'] = order.status
        output.append(order_data)
    return jsonify({'orders': output})


@app.route('/order/<order_id>', methods=['GET'])
def get_one_order(order_id):
    """Страница с данными заказа с фильтром по id"""
    order = db.session.query(Order.id, Order.user_id, Order.status, HardwareGood.price, HardwareGood.description,
                         Producer.name.label('producer'), Category.name.label('category'))\
        .join(HardwareGood, Order.good_id == HardwareGood.id)\
        .join(Producer, HardwareGood.producer_id == Producer.id)\
        .join(Category, HardwareGood.category_id == Category.id)\
        .filter(Order.id == order_id).first()
    if not order:
        return jsonify({'message': 'Заказ не найден'})
    order_data = {}
    order_data['id'] = order.id
    order_data['user_id'] = order.user_id
    order_data['category'] = order.category
    order_data['producer'] = order.producer
    order_data['description'] = order.description
    order_data['price'] = order.price
    order_data['status'] = order.status
    return jsonify({'order': order_data})


@app.route('/order', methods=['POST'])
def create_order():
    """Добавление заказа в базу данных"""
    data = request.get_json()
    user = db.session.query(User).filter(User.id == data['user_id']).all()
    if not user:
        return jsonify({'message': 'Пользователь не найден'})
    good = db.session.query(HardwareGood).filter(HardwareGood.id == data['hardware_good_id']).all()
    if not good:
        return jsonify({'message': 'Товар не найден'})
    new_order = Order(user_id=data['user_id'], good_id=data['hardware_good_id'], status='На рассмотрении')
    hw_good = db.session.query(HardwareGood).filter(HardwareGood.id == data['hardware_good_id']).first()
    hw_good.quantity -= 1
    db.session.add(new_order)
    db.session.commit()
    return jsonify({'message': 'Товар добавлен в корзину'})


@app.route('/order/<order_id>', methods=['DELETE'])
def delete_order(order_id):
    """Удаление заказа из базы данных"""
    order = db.session.query(Order).filter(Order.id == order_id).first()
    if not order:
        return jsonify({'message': 'Заказ не найден'})
    hw_good = db.session.query(HardwareGood).filter(HardwareGood.id == order.good_id).first()
    hw_good.quantity += 1
    db.session.delete(order)
    db.session.commit()
    return jsonify({'message': 'Заказ удален'})


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)