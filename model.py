"""
Provides the model classes representing the state of the OORMS
system.

Submitting lab group: [your names here]
Submission date: [date here]

Original code by EEE320 instructors.
"""

from constants import TABLES, MENU_ITEMS


class Restaurant:

    def __init__(self):
        super().__init__()
        self.tables = [Table(seats, loc) for seats, loc in TABLES]
        self.menu_items = [MenuItem(name, price) for name, price in MENU_ITEMS]
        self.views = []

    def add_view(self, view):
        self.views.append(view)

    def notify_views(self):
        for view in self.views:
            view.update()


class Table:

    def __init__(self, n_seats, location):
        self.n_seats = n_seats
        self.location = location
        self.orders = [Order(i) for i in range(n_seats)]

    def has_any_active_orders(self):
        for order in self.orders:
            for item in order.items:
                if item.has_been_ordered() and not item.has_been_served():
                    return True
        return False

    def has_order_for(self, seat):
        return bool(self.orders[seat].items)

    def order_for(self, seat):
        return self.orders[seat]

    def clear_table(self):
        self.orders.clear()
        self.orders = [Order(i) for i in range(self.n_seats)]


class Order:

    def __init__(self, seat_number):
        self.items = []
        self.seat_number = seat_number

    def add_item(self, menu_item):
        item = OrderItem(menu_item)
        self.items.append(item)

    def remove_item(self, menu_item):
        self.items.remove(menu_item)

    def place_new_orders(self):
        for item in self.unordered_items():
            item.mark_as_ordered()

    def remove_unordered_items(self):
        for item in self.unordered_items():
            self.items.remove(item)

    def unordered_items(self):
        return [item for item in self.items if not item.has_been_ordered()]

    def total_cost(self):
        return sum((item.details.price for item in self.items))

    def is_empty(self):
        for item in self.items:
            if item.has_been_ordered():
                return False
        return True


class OrderItem:

    def __init__(self, menu_item):
        self.details = menu_item
        self.state = "unordered"

    def mark_as_ordered(self):
        self.state = "ordered"

    def has_been_ordered(self):
        return self.state == "ordered"

    def has_been_served(self):
        return self.state == "served"

    def can_be_cancelled(self):
        return self.state != "served"


class MenuItem:

    def __init__(self, name, price):
        self.name = name
        self.price = price

class Bill:
    def __init__(self, order):
        if order!=None:
            self.orders = [order]
        else:
            self.orders = []
        self.items = {}
        self.update_items()

    def add_order(self, order):
        self.orders.append(order)
        self.update_items()

    def remove_order(self, order):
        self.orders.remove(order)
        self.update_items()

    def total_cost(self):
        total = 0.0
        for item in self.items:
            total += self.items[item]*item.price
        return total

    def update_items(self):
        self.items.clear()
        for order in self.orders:
            for item in order.items:
                key = item.details
                if key in self.items:
                    self.items[key] += 1
                else:
                    self.items[key] = 1

