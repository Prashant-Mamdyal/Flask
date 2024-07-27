import unittest
import datetime
from app import create_app, db
from app.models import Customer, Order, OrderItem, Shipment, Product, Supplier

class TestOrders(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')           
        self.client = self.app.test_client()                                          
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    # Get method for order list
    def test_get_orders(self):
        '''Test retrieving all orders when there are no orders.
           Test retrieving all orders when there are multiple orders.
        '''
        # Test retrieving all orders when there are no orders
        response = self.client.get('/orders/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [])

        # Create a customer to associate with the orders
        customer = Customer(name='Test Customer', contact_info='test@example.com')
        db.session.add(customer)
        db.session.commit()

        # Test retrieving all orders when there are multiple orders
        order_date = datetime.datetime(2023, 7, 10)
        order1 = Order(customer_id=customer.id, order_date=order_date, status='Pending')
        order2 = Order(customer_id=customer.id, order_date=order_date, status='Fulfilled')
        db.session.add(order1)
        db.session.add(order2)
        db.session.commit()
        
        response = self.client.get('/orders/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)
        self.assertEqual(response.json[0]['status'], 'Pending')
        self.assertEqual(response.json[1]['status'], 'Fulfilled')

    # Post method for order list
    def test_create_orders(self):
        customer = Customer(name='Test Customer', contact_info='test@example.com')
        db.session.add(customer)
        db.session.commit()

        valid_order_data = {
            'customer_id': customer.id,
            'order_date': '2023-07-10T00:00:00',  # ISO 8601 format
            'status': 'Pending'
        }
        response = self.client.post('/orders/', json=valid_order_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['customer_id'], customer.id)
        self.assertEqual(response.json['status'], 'Pending')

        invalid_order_data = {
            'customer_id': 999,  # Non-existent customer ID
            'order_date': '2023-07-10T00:00:00',  # ISO 8601 format
            'status': 'Pending'
        }
        response = self.client.post('/orders/', json=invalid_order_data)
        self.assertEqual(response.status_code, 404)
        self.assertIn('Customer 999 not present', response.json['message'])

    # Get method for order details
    def test_get_order_by_id(self):
        customer = Customer(name='Test Customer', contact_info='test@example.com')
        db.session.add(customer)
        db.session.commit()

        order_date = datetime.datetime(2023, 7, 10)
        order = Order(customer_id=customer.id, order_date=order_date, status='Pending')
        db.session.add(order)
        db.session.commit()

        # Retrieve the order by its ID
        response = self.client.get(f'/orders/{order.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['id'], order.id)
        self.assertEqual(response.json['customer_id'], customer.id)
        self.assertEqual(response.json['status'], 'Pending')

        # Attempt to retrieve a non-existent order by its ID
        response = self.client.get('/orders/999')
        self.assertEqual(response.status_code, 404)
        self.assertIn('Order 999 not found', response.json['message'])
    
    def test_update_order_by_id(self):
        customer = Customer(name='Test Customer', contact_info='test@example.com')
        db.session.add(customer)
        db.session.commit()

        order_date = datetime.datetime(2023, 7, 10)
        order = Order(customer_id=customer.id, order_date=order_date, status='Pending')
        db.session.add(order)
        db.session.commit()

        # Update the order by its ID
        updated_data = {
            'customer_id': customer.id,
            'order_date': '2023-07-15T00:00:00',  # ISO 8601 format
            'status': 'Fulfilled'
        }
        response = self.client.put(f'/orders/{order.id}', json=updated_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['customer_id'], updated_data['customer_id'])
        self.assertEqual(response.json['order_date'], updated_data['order_date'])
        self.assertEqual(response.json['status'], updated_data['status'])
        
        # Data to update the order with a non-existent customer ID
        updated_data_invalid_customer = {
            'customer_id': 999,  # Non-existent customer ID
            'order_date': '2023-07-15T00:00:00',  # ISO 8601 format
            'status': 'Fulfilled'
        }
        response = self.client.put(f'/orders/{order.id}', json=updated_data_invalid_customer)
        self.assertEqual(response.status_code, 404)
        self.assertIn('Customer 999 not present', response.json['message'])

        # Data to update a non-existent order
        updated_data = {
            'customer_id': customer.id,
            'order_date': '2023-07-15T00:00:00',  # ISO 8601 format
            'status': 'Fulfilled'
        }
        response = self.client.put('/orders/999', json=updated_data)
        self.assertEqual(response.status_code, 404)
        self.assertIn('Order 999 not present', response.json['message'])

    def test_delete_order(self):
        # Test 1: Create and delete an order without associated data
        customer = Customer(name='Test Customer', contact_info='test@example.com')
        db.session.add(customer)
        db.session.commit()

        order_date = datetime.datetime(2023, 7, 10)
        order = Order(customer_id=customer.id, order_date=order_date, status='Pending')
        db.session.add(order)
        db.session.commit()

        # Test: Delete an order with no associated order items or shipments
        response = self.client.delete(f'/orders/{order.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Order deleted successfully')

        # Test 2: Recreate the order and add an associated order item
        order = Order(customer_id=customer.id, order_date=order_date, status='Pending')
        db.session.add(order)
        db.session.commit()

        order_item = OrderItem(order_id=order.id, product_id=1, quantity=2, price=50.0)
        db.session.add(order_item)
        db.session.commit()

        # Test: Attempt to delete an order with associated order items
        response = self.client.delete(f'/orders/{order.id}')
        self.assertEqual(response.status_code, 400)
        self.assertIn('has associated data in order items table and cannot be deleted', response.json['message'])

        # Test 3: Recreate the order and add an associated shipment
        order = Order(customer_id=customer.id, order_date=order_date, status='Pending')
        db.session.add(order)
        db.session.commit()

        shipment = Shipment(order_id=order.id, shipment_date=datetime.datetime(2023, 7, 11), delivery_date=datetime.datetime(2023, 7, 12), status='Shipped')
        db.session.add(shipment)
        db.session.commit()

        # Test: Attempt to delete an order with associated shipment
        response = self.client.delete(f'/orders/{order.id}')
        self.assertEqual(response.status_code, 400)
        self.assertIn('has associated data in shipment table and cannot be deleted', response.json['message'])

        # Test 4: Attempt to delete a non-existent order
        response = self.client.delete('/orders/999')
        self.assertEqual(response.status_code, 404)
        self.assertIn('Order 999 not found', response.json['message'])

    def test_patch_order_status(self):
        # Create a customer
        customer = Customer(name='Test Customer', contact_info='test@example.com')
        db.session.add(customer)
        db.session.commit()

        # Create an order
        order_date = datetime.datetime(2023, 7, 10)
        order = Order(customer_id=customer.id, order_date=order_date, status='Pending')
        db.session.add(order)
        db.session.commit()

        # Test 1: Successfully update order status to a valid status
        valid_statuses = ['Pending', 'Fulfilled', 'Cancelled']
        for status in valid_statuses:
            response = self.client.patch(f'/orders/{order.id}/status', json={'status': status})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json['status'], status)

        # Test 2: Fail to update order status with an invalid status
        response = self.client.patch(f'/orders/{order.id}/status', json={'status': 'InvalidStatus'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid status. Please set status to Pending, Fulfilled, or Cancelled.', response.json['message'])

        # Test 3: Fail to update order status for a non-existent order
        response = self.client.patch('/orders/999/status', json={'status': 'Pending'})
        self.assertEqual(response.status_code, 404)
        self.assertIn('Order 999 not found', response.json['message'])

    def test_get_order_items(self):
        # Create a supplier
        supplier = Supplier(name='Test Supplier', contact_info='test@supplier.com')
        db.session.add(supplier)
        db.session.commit()

        # Create a customer
        customer = Customer(name='Test Customer', contact_info='test@example.com')
        db.session.add(customer)
        db.session.commit()

        # Create products
        product1 = Product(name='Test Product1', description='A Product1 for Testing', price=30, supplier_id=supplier.id, stock=50)
        product2 = Product(name='Test Product2', description='A Product2 for Testing', price=10, supplier_id=supplier.id, stock=100)
        db.session.add(product1)
        db.session.add(product2)
        db.session.commit()

        # Create an order
        order_date = datetime.datetime(2023, 7, 10)
        order = Order(customer_id=customer.id, order_date=order_date, status='Pending')
        db.session.add(order)
        db.session.commit()

        # Create order items
        order_item1 = OrderItem(order_id=order.id, product_id=product1.id, quantity=20, price=40)
        order_item2 = OrderItem(order_id=order.id, product_id=product2.id, quantity=10, price=30)
        db.session.add(order_item1)
        db.session.add(order_item2)
        db.session.commit()

        # Test 1: Successfully retrieve items for an existing order
        response = self.client.get(f'/orders/{order.id}/items')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)
        self.assertEqual(response.json[0]['product']['name'], 'Test Product1')
        self.assertEqual(response.json[1]['product']['name'], 'Test Product2')

        # Test 2: Retrieve empty list for an order with no items
        new_order = Order(customer_id=customer.id, order_date=datetime.datetime(2023, 7, 11), status='Pending')
        db.session.add(new_order)
        db.session.commit()

        response = self.client.get(f'/orders/{new_order.id}/items')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [])

        # Test 3: Fail to retrieve items for a non-existent order
        response = self.client.get('/orders/999/items')
        self.assertEqual(response.status_code, 404)
        self.assertIn('Order 999 not present', response.json['message'])

if __name__ == '__main__':
    unittest.main()