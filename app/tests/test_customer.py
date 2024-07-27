import unittest
import datetime
from app import create_app, db
from app.models import Customer, Order

class TestCustomers(unittest.TestCase):

    '''The setUp() method is a special method in unittest classes that is run before each individual test method. 
       Its purpose is to set up any state or resources that are needed for the tests.
    '''
    def setUp(self):
        #initializes a Flask application using a configuration named 'testing'.
        self.app = create_app('testing') 
                   
        '''test_client() creates a test client for interacting with the Flask application in a testing context.
        This allows you to simulate HTTP requests to your application endpoints without actually running the server.'''           
        self.client = self.app.test_client()        

        '''app_context() creates an application context for the Flask application. 
        The application context is necessary for accessing application-specific data during tests. '''                                            
        self.ctx = self.app.app_context()
        self.ctx.push()

        '''create_all() method in SQLAlchemy creates all the database tables defined by your models (app.models). 
        This ensures that before each test runs, the database schema is set up and ready for use.'''
        db.create_all()

    '''The tearDown() method is also a special method in unittest classes that is run after each individual test method. 
    Its purpose is to clean up any resources that were set up in setUp() to ensure each test runs independently and does not leave behind any side effects.'''
    def tearDown(self):
        '''remove() method cleans up the database session. This ensures that any database session used during the test is 
        properly closed and any transaction is rolled back, preventing data leakage or interference between tests.'''
        db.session.remove()

        '''drop_all() method in SQLAlchemy drops all the tables in the database. 
        This is typically done to clean up after tests so that the next test run starts with a clean slate.'''
        db.drop_all()

        '''pop() method pops the application context off the stack. 
        This deactivates the application context and cleans up any application-specific state that was set up during setUp().'''
        self.ctx.pop()

    #post method for customer list
    def test_customer_creation(self):
        data = {'name': 'Test Customer', 'contact_info': 'test@example.com'}
        response = self.client.post('/customers/', json = data)
        self.assertEqual(response.status_code, 201)
        self.assertIn('id', response.json)

    #get method for customer list
    def test_list_customers(self):
        customer_1 = Customer(name='Customer 1', contact_info='customer1@example.com')
        customer_2 = Customer(name='Customer 2', contact_info='customer2@example.com')
        db.session.add(customer_1)
        db.session.add(customer_2)
        db.session.commit()

        response = self.client.get('/customers/')
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.json), 2)
        self.assertEqual(response.json[0]['name'], 'Customer 1')
        self.assertEqual(response.json[1]['name'], 'Customer 2')

    #get method for customer details by id
    def test_get_customer_by_id(self):
        customer = Customer(name='Test customer', contact_info='test@example.com')
        db.session.add(customer)
        db.session.commit()

        response = self.client.get(f'/customers/{customer.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Test customer')
        self.assertEqual(response.json['contact_info'], 'test@example.com')

    #put method for customer details by id
    def test_update_customer_by_id(self):
        customer = Customer(name = 'Test customer', contact_info='test@example.com')
        db.session.add(customer)
        db.session.commit()

        data = {'name':'updated customer', 'contact_info':'test@example.com'}
        response = self.client.put(f'/customers/{customer.id}', json = data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'updated customer')
        self.assertEqual(response.json['contact_info'], 'test@example.com')

    #delete method for customer details by id
    '''This test case will cover the following scenarios:
        1) Attempting to delete a customer that doesn't exist.
        2) Attempting to delete a customer that has associated orders.
        3) Successfully deleting a customer without associated orders.
    '''
    def test_delete_customer_not_found(self):
        # Attempt to delete a customer that does not exist (ID 999)
        response = self.client.delete('/customers/999')
        self.assertEqual(response.status_code, 404)
        self.assertIn('Customer 999 not found', response.json['message'])

    def test_delete_customer_with_orders(self):
        customer = Customer(name='Test Customer', contact_info='test@example.com')
        db.session.add(customer)
        db.session.commit()

        order_date = datetime.datetime(2023,7,10)
        order = Order(customer_id=customer.id, order_date=order_date, status='Pending')
        db.session.add(order)
        db.session.commit()

        response = self.client.delete(f'/customers/{customer.id}')
        self.assertEqual(response.status_code, 400)
        self.assertIn('has associated data in orders tables and cannot be deleted', response.json['message'])
        
    def test_delete_customer_success(self):
        customer = Customer(name = 'Test customer', contact_info='test@example.com')
        db.session.add(customer)
        db.session.commit()

        response = self.client.delete(f'/customers/{customer.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('customer deleted successfully', response.json['message'])
        self.assertIsNone(Customer.query.get(customer.id))

if __name__ == '__main__':
    unittest.main()