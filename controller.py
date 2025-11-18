"""
Provides the controller layer for the OORMS system.

Submitting lab group: [your names here]
Submission date: [date here]

Original code by EEE320 instructors.
"""
from model import Bill


class Controller:

    def __init__(self, view, restaurant):
        self.view = view
        self.restaurant = restaurant


class RestaurantController(Controller):

    def create_ui(self):
        self.view.create_restaurant_ui()

    def table_touched(self, table_number):
        self.view.set_controller(TableController(self.view, self.restaurant,
                                                 self.restaurant.tables[table_number]))
        self.view.update()


class TableController(Controller):

    def __init__(self, view, restaurant, table):
        super().__init__(view, restaurant)
        self.table = table

    def create_ui(self):
        self.view.create_table_ui(self.table)

    def seat_touched(self, seat_number):
        self.view.set_controller(OrderController(self.view, self.restaurant, self.table, seat_number))
        self.view.update()

    def make_bills(self, printer):
        self.view.set_controller(BillsController(self.view, self.restaurant, self.table))
        self.view.update()
        printer.print(f'Set up bills for table {self.restaurant.tables.index(self.table)}')

    def done(self):
        self.view.set_controller(RestaurantController(self.view, self.restaurant))
        self.view.update()


class OrderController(Controller):

    def __init__(self, view, restaurant, table, seat_number):
        super().__init__(view, restaurant)
        self.table = table
        self.order = self.table.order_for(seat_number)

    def create_ui(self):
        self.view.create_order_ui(self.order)

    def add_item(self, menu_item):
        self.order.add_item(menu_item)
        self.restaurant.notify_views()

    def remove(self, order_item):
        self.order.remove_item(order_item)
        self.restaurant.notify_views()

    def update_order(self):
        self.order.place_new_orders()
        self.view.set_controller(TableController(self.view, self.restaurant, self.table))
        self.restaurant.notify_views()

    def cancel_changes(self):
        self.order.remove_unordered_items()
        self.view.set_controller(TableController(self.view, self.restaurant, self.table))
        self.restaurant.notify_views()


class BillsController(Controller):
    def __init__(self, view, restaurant, table):
        super().__init__(view, restaurant)
        self.bills = []
        self.table = table
        for order in table.orders:
            if not order.is_empty():
                order.remove_unordered_items()
                self.bills.append(Bill(order))
        self.current_bill = self.bills[0]

    def print_bill(self, bill):
        date_str = "YYYY-MM-DD"
        time_str = "HH:MM"

        self.view.printer_window.print("----------Stressed & Koultoure----------\n")
        self.view.printer_window.print("            15, Valour Drive            ")
        self.view.printer_window.print("       Kingston, Ontario, G5X 2J9       ")
        self.view.printer_window.print(f"{date_str:<32}{time_str}\n")
        # Items
        for menu_item, qty in bill.items.items():
            line_total = menu_item.price * qty
            self.view.printer_window.print(f"{qty:<5} {menu_item.name:<20} {line_total:>10}$")

        self.view.printer_window.print(f"\nTotal:{bill.total_cost():>30}$")

        self.view.printer_window.print("\nMéthode de paiement")
        self.view.printer_window.print("-"*40)

    def remove_bill(self, bill):
        self.bills.remove(bill)

    def add_bill(self, bill):
        self.bills.append(bill)

    def change_current(self, new_bill):
        self.current_bill = new_bill
        self.restaurant.notify_views()

    def done(self):
        self.table.clear_table()
        self.view.set_controller(RestaurantController(self.view, self.restaurant))
        self.view.update()

    def fuse_bills(self):
        self.view.set_controller(FusionController(self.view, self.restaurant, self.table, self.bills))
        self.restaurant.notify_views()

    def create_ui(self):
        self.view.create_bills_ui(self.bills, self.current_bill)

class FusionController(Controller):
    def __init__(self, view, restaurant, table, bills):
        super().__init__(view, restaurant)
        self.seat_ids = {}
        self.table_id = None
        self.selected = []
        self.bills = bills
        self.table = table

    def create_ui(self):
        self.view.create_fusion_ui(self.table)

    def seat_touched(self, seat_id):
        if seat_id is None:
            self.view.printer_window.print("Invalid seat clicked")
            return
        seat_number = None
        for key, value in self.seat_ids.items():
            if value == seat_id:
                seat_number = key
                break
        if seat_number is None:
            self.view.printer_window.print("Seat ID not found in seat_ids")
            return
        self.view.change_seat_style(seat_id)
        if seat_number in self.selected:
            self.selected.remove(seat_number)
        else:
            self.selected.append(seat_number)


    def remove_bill(self, bill):
        self.bills.remove(bill)

    def add_bill(self, bill):
        self.bills.append(bill)

    def done(self):
        new_bill, bills_to_remove = self.merge_selected_orders(self.selected, self.bills)
        new_bill.update_items()
        for bill in bills_to_remove:
            self.view.controller.remove_bill(bill)
        self.view.controller.add_bill(new_bill)
        self.view.set_controller(BillsController(self.view, self.restaurant, self.table))
        self.view.controller.bills = self.bills
        self.view.update()

    def merge_selected_orders(self, select, bills):
        new_bill = Bill(None)
        bills_to_remove = []

        for bill in bills:
            orders_to_move = [o for o in bill.orders if o.seat_number in select]
            for order in orders_to_move:
                new_bill.orders.append(order)
                bill.orders.remove(order)
            if not bill.orders:
                bills_to_remove.append(bill)

        return new_bill, bills_to_remove