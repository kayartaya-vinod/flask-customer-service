from flask import Flask, request, abort
from flask_restful import Api, Resource
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
import uuid

app = Flask(__name__)
api = Api(app)  # a wrapper object around the "app"
mm = Marshmallow(app)  # another wrapper object around the "app"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.sqlite3'
db = SQLAlchemy(app)


class Customer(db.Model):

    __tablename__ = 'customers'

    id = db.Column(db.String, primary_key=True)
    firstname = db.Column(db.String)
    lastname = db.Column(db.String)
    gender = db.Column(db.String, default='Male')
    email = db.Column(db.String, unique=True)
    phone = db.Column(db.String, unique=True)
    address = db.Column(db.String)
    city = db.Column(db.String)
    state = db.Column(db.String)
    country = db.Column(db.String)
    avatar = db.Column(db.String)

    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.firstname = kwargs.get('firstname')
        self.lastname = kwargs.get('lastname')
        self.gender = kwargs.get('gender')
        self.email = kwargs.get('email')
        self.phone = kwargs.get('phone')
        self.address = kwargs.get('address')
        self.city = kwargs.get('city')
        self.state = kwargs.get('state')
        self.country = kwargs.get('country')
        self.avatar = kwargs.get('avatar')

    def __repr__(self):
        return f'Customer (firstname="{self.firstname}", lastname="{self.lastname}, email="{self.email}")'


class CustomerSchema(mm.Schema):
    class Meta:
        fields = ('id', 'firstname', 'lastname', 'email', 'phone', 'address', 'city', 'state', 'country', 'avatar')


customer_schema = CustomerSchema()
customer_list_schema = CustomerSchema(many=True)


# this class handles all requests for url '/api/customers'
# handlers for POST and GET requests
class CustomerListResource(Resource):

    def get(self):

        if 'email' in request.args:
            # using query.filter
            c1 = Customer.query.filter(Customer.email == request.args['email']).first()
            return None if c1 is None else customer_schema.dump(c1)

        if 'phone' in request.args:
            # using query.filter_by
            c1 = Customer.query.filter_by(phone=request.args['phone']).first()
            return None if c1 is None else customer_schema.dump(c1)

        limit = int(request.args['_limit']) if '_limit' in request.args else 10
        page = int(request.args['_page']) if '_page' in request.args else 1
        offset = (page-1) * limit

        if 'city' in request.args:
            print(f'city = {request.args["city"]}')
            customers = Customer.query.filter(Customer.city == request.args['city']).limit(limit).offset(offset).all()
            customer_count = Customer.query.filter(Customer.city == request.args['city']).count()
        else:
            customers = Customer.query.limit(limit).offset(offset).all()
            customer_count = Customer.query.count()
        return {'customers': customer_list_schema.dump(customers), 'count': customer_count}

    def post(self):
        try:
            c1 = Customer(**request.json)
            c1.id = str(uuid.uuid4())
            db.session.add(c1)
            db.session.commit()
            return customer_schema.dump(c1), 201
        except Exception as e:
            return abort(500, str(e))


# this class handles all requests for url '/api/customers/<customer-id>'
# handlers for GET, PUT, PATCH, and DELETE requests
class CustomerResource(Resource):

    def get(self, customer_id):
        c1 = Customer.query.get_or_404(customer_id, description=f'No data found for the input id {customer_id}')
        return customer_schema.dump(c1)

    # PATCH can also be used for updating (PUT) the entire row of the given id
    def patch(self, customer_id):
        c1 = Customer.query.get_or_404(customer_id, description=f'No data found for the input id {customer_id}')
        # control reaches here only if c1 is found; else it is aborted with 404 error
        if 'firstname' in request.json:
            c1.firstname = request.json['firstname']
        if 'lastname' in request.json:
            c1.lastname = request.json['lastname']
        if 'email' in request.json:
            c1.email = request.json['email']
        if 'phone' in request.json:
            c1.phone = request.json['phone']
        if 'gender' in request.json:
            c1.gender = request.json['gender']
        if 'address' in request.json:
            c1.address = request.json['address']
        if 'city' in request.json:
            c1.city = request.json['city']
        if 'state' in request.json:
            c1.state = request.json['state']
        if 'country' in request.json:
            c1.country = request.json['country']
        if 'avatar' in request.json:
            c1.avatar = request.json['avatar']

        db.session.commit()
        return customer_schema.dump(c1)

    def delete(self, customer_id):
        c1 = Customer.query.get_or_404(customer_id, description=f'No data found for the input id {customer_id}')
        db.session.delete(c1)
        db.session.commit()
        return {'message': f'Customer with id {customer_id} deleted successfully'}, 200


api.add_resource(CustomerListResource, '/api/customers')
api.add_resource(CustomerResource, '/api/customers/<string:customer_id>')


if __name__ == '__main__':
    app.run(port=8080, debug=True)
