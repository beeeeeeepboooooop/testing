import unittest
from datetime import date, timedelta
from HotelSystem import HotelSystem
from Person import Person
from Guest import Guest
from Employee import Employee
from Manager import Manager
from Room import Room
from SingleRoom import SingleRoom
from DoubleRoom import DoubleRoom
from SuiteRoom import SuiteRoom
from Booking import Booking
from Service import Service
from Payment import Payment
from Invoice import Invoice
from LoyaltyProgram import LoyaltyProgram


# My awesome hotel system tests!!
# Written by: Me (obviously)
# Date: Whenever the due date is lol

class HotelSystemTests(unittest.TestCase):
    def setUp(self):
        """Set up stuff before tests run"""
        # Make a new hotel
        self.hotel = HotelSystem()

        # Add some cool rooms
        single_room = SingleRoom(101, "Single", ["TV", "WiFi", "Mini Fridge with Questionable Contents"], 100.0, True,
                                 True, 1, True)
        double_room = DoubleRoom(201, "Double", ["TV", "WiFi", "Mini Bar", "Weird Painting That Stares At You"], 150.0,
                                 True, 2, True, False)
        suite_room = SuiteRoom(301, "Suite", ["TV", "WiFi", "Mini Bar", "Jacuzzi That Nobody Knows How To Use"], 300.0,
                               True, 2, True, True)

        self.hotel.addRoom(single_room)
        self.hotel.addRoom(double_room)
        self.hotel.addRoom(suite_room)

        # Set up loyalty program with cool rewards
        points_scheme = {"booking": 10.0, "service": 5.0}
        status_thresholds = {"Silver": 100, "Gold": 500, "Platinum": 1000}
        reward_options = {
            "Silver": {"Free Breakfast (Toast Only)": 50, "Late Checkout (15 Minutes)": 30},
            "Gold": {"Room Upgrade (To Room With Window)": 100, "Free Parking (In Sketchy Lot)": 75},
            "Platinum": {"Free Night (On Christmas)": 200, "Spa Credit (For Broken Massage Chair)": 150}
        }

        self.hotel.loyaltyProgram = LoyaltyProgram(points_scheme, status_thresholds, reward_options)

        # Hire some staff
        self.hotel.hireEmployee("Chad McBro", "chad@hotel.com", "420-6969", "Dudebro Receptionist", 3000.0)
        self.hotel.hireEmployee("Karen Complainer", "karen@hotel.com", "555-MANAGER", "Professional Karen", 2800.0)
        self.manager = self.hotel.hireManager("Bossy McBossface", "boss@hotel.com", "911-HELP", 5000.0, "Front Office")

    def tearDown(self):
        """Clean up after tests (professor said we need this)"""
        # Clear everything
        self.hotel.rooms.clear()
        self.hotel.services.clear()
        self.hotel.guests.clear()
        self.hotel.employees.clear()
        self.hotel.bookings.clear()
        self.hotel.payments.clear()
        self.hotel.invoices.clear()

    # 1. Guest Account Creation Tests
    def test_guest_registration_successful(self):
        """Testing if guests can register without the system exploding"""
        # Example 1: Register a guest with a funny name
        guest1 = self.hotel.registerGuest("Yolo Swaggins", "lordofthewing@middleearth.com", "123-HOBBIT")
        self.assertIsNotNone(guest1)
        self.assertEqual(guest1.getName(), "Yolo Swaggins")
        self.assertEqual(guest1.getEmail(), "lordofthewing@middleearth.com")
        self.assertEqual(guest1.getPhone(), "123-HOBBIT")
        self.assertEqual(guest1.loyaltyStatus, "Regular")  # Boring default status
        self.assertEqual(guest1.loyaltyPoints, 0)  # Poor hobbit has no points

        # Example 2: Another weird guest
        guest2 = self.hotel.registerGuest("Darth Invader", "notevil@deathstar.gov", "ORDER-66")
        self.assertIsNotNone(guest2)
        self.assertEqual(guest2.getName(), "Darth Invader")
        self.assertEqual(guest2.loyaltyPoints, 0)

        # Make sure both guests are in system
        self.assertEqual(len(self.hotel.guests), 2)

    def test_guest_registration_invalid(self):
        """Testing when people mess up their info"""
        # Example 1: Empty email should make system angry
        with self.assertRaises(ValueError):
            self.hotel.registerGuest("Forgetful Fred", "", "123-DUDE")

        # Example 2: Phone number can't be "pizza"
        with self.assertRaises(ValueError):
            self.hotel.registerGuest("Pizza Lover", "ilovepizza@food.com", "PIZZA")

    def test_guest_profile_update(self):
        """Testing if guests can change their minds about their info"""
        # Example 1: Guest changes everything
        guest = self.hotel.registerGuest("Clark Kent", "definitely.not.superman@dailyplanet.com", "555-HERO")
        result = guest.updateProfile("Superman", "itsme@superman.com", "555-CAPE")
        self.assertTrue(result)
        self.assertEqual(guest.getName(), "Superman")
        self.assertEqual(guest.getEmail(), "itsme@superman.com")
        self.assertEqual(guest.getPhone(), "555-CAPE")

        # Example 2: Guest changes just email to something weird
        guest2 = self.hotel.registerGuest("Wifi Hacker", "hacker@coffee.shop", "555-HACK")
        result = guest2.updateProfile("Wifi Hacker", "thispasswordistoostrong@nsa.gov", "555-HACK")
        self.assertTrue(result)
        self.assertEqual(guest2.getEmail(), "thispasswordistoostrong@nsa.gov")

    # 2. Searching for Available Rooms Tests
    def test_find_available_rooms_by_date(self):
        """Testing if we can find empty rooms by date (duh)"""
        # Set up some dates
        today = date.today()
        tomorrow = today + timedelta(days=1)  # Math is hard
        next_week = today + timedelta(days=7)

        # Example 1: Look for rooms when all are empty
        empty_rooms = self.hotel.findAvailableRooms(tomorrow, next_week, None)
        self.assertEqual(len(empty_rooms), 3)  # All rooms better be empty!

        # Book a room so we can test if it shows up as unavailable
        guest = self.hotel.registerGuest("Party Animal", "party@allnight.com", "555-WOOO")
        room = self.hotel.rooms[101]  # The single room
        booking = self.hotel.makeBooking(guest, room, tomorrow, next_week)

        # Example 2: Now one room should be booked by our party dude
        empty_rooms = self.hotel.findAvailableRooms(tomorrow, next_week, None)
        self.assertEqual(len(empty_rooms), 2)  # Should be one less available room
        self.assertNotIn(room, empty_rooms)  # Party room shouldn't be in results

    def test_find_available_rooms_by_type(self):
        """Testing if we can find rooms by their type"""
        # Set up dates
        check_in = date.today() + timedelta(days=1)
        check_out = date.today() + timedelta(days=3)

        # Example 1: Find single rooms for lonely travelers
        lonely_rooms = self.hotel.findAvailableRooms(check_in, check_out, "Single")
        self.assertEqual(len(lonely_rooms), 1)
        self.assertEqual(lonely_rooms[0].roomType, "Single")

        # Example 2: Find fancy rooms for rich people
        fancy_rooms = self.hotel.findAvailableRooms(check_in, check_out, "Suite")
        self.assertEqual(len(fancy_rooms), 1)
        self.assertEqual(fancy_rooms[0].roomType, "Suite")

    def test_find_available_rooms_no_results(self):
        """Testing what happens when there are no rooms (sad times)"""
        # Example 1: Look for a type of room that doesn't exist
        check_in = date.today() + timedelta(days=1)
        check_out = date.today() + timedelta(days=3)
        magical_rooms = self.hotel.findAvailableRooms(check_in, check_out, "Hogwarts Dormitory")
        self.assertEqual(len(magical_rooms), 0)  # No magic here :(

        # Example 2: Try invalid dates (checkout before checkin, time travel not invented yet)
        with self.assertRaises(ValueError):
            self.hotel.findAvailableRooms(check_out, check_in, None)

    # 3. Making a Room Reservation Tests
    def test_make_booking_successful(self):
        """Testing if people can actually book rooms"""
        # Set up dates
        check_in = date.today() + timedelta(days=1)
        check_out = date.today() + timedelta(days=3)

        # Example 1: Book a normal room for a normal person (boring)
        guest = self.hotel.registerGuest("Boring Bob", "bob@normalperson.com", "555-BOOO")
        room = self.hotel.rooms[101]  # Single room
        booking = self.hotel.makeBooking(guest, room, check_in, check_out)

        self.assertIsNotNone(booking)
        self.assertEqual(booking.status, "Confirmed")
        self.assertEqual(booking.checkInDate, check_in)
        self.assertEqual(booking.checkOutDate, check_out)
        self.assertFalse(room.isAvailable)  # Room should be taken now

        # Example 2: Book a fancy room for a fancy cat
        guest2 = self.hotel.registerGuest("Mr. Whiskers", "meow@catmail.com", "555-MEOW")
        room2 = self.hotel.rooms[301]  # Suite room
        booking2 = self.hotel.makeBooking(guest2, room2, check_in, check_out)

        self.assertIsNotNone(booking2)
        self.assertEqual(booking2.status, "Confirmed")
        self.assertEqual(len(self.hotel.bookings), 2)

    def test_make_booking_invalid(self):
        """Testing when booking fails (sad trombone)"""
        # Set up dates
        check_in = date.today() + timedelta(days=1)
        check_out = date.today() + timedelta(days=3)

        # Add a guest
        guest = self.hotel.registerGuest("Double Booker", "oops@didittwice.com", "555-OOPS")

        # Example 1: Try to book same room twice (greedy!)
        room = self.hotel.rooms[101]  # Single room
        # First booking is fine
        self.hotel.makeBooking(guest, room, check_in, check_out)

        # Second booking should explode
        with self.assertRaises(ValueError):
            self.hotel.makeBooking(guest, room, check_in, check_out)

        # Example 2: Try to book with checkout before checkin (time travel fail)
        room2 = self.hotel.rooms[201]  # Double room
        with self.assertRaises(ValueError):
            self.hotel.makeBooking(guest, room2, check_out, check_in)

    # 4. Booking Confirmation Notification Tests
    def test_booking_confirmation(self):
        """Testing if confirmation emails work (they never check them anyway)"""
        # Set up dates
        check_in = date.today() + timedelta(days=1)
        check_out = date.today() + timedelta(days=3)

        # Example 1: Send confirmation to normal email
        guest = self.hotel.registerGuest("Email Checker", "actually.reads.email@gmail.com", "555-READ")
        room = self.hotel.rooms[201]  # Double room
        booking = self.hotel.makeBooking(guest, room, check_in, check_out)

        # Send the confirmation
        result = booking.sendConfirmation()
        self.assertTrue(result)

        # Example 2: Change dates and send again (indecisive customer)
        # Change booking dates to even more confusing dates
        new_check_in = check_in + timedelta(days=1)
        new_check_out = check_out + timedelta(days=1)
        booking.checkInDate = new_check_in
        booking.checkOutDate = new_check_out

        # Send another confirmation (spam their inbox)
        result = booking.sendConfirmation()
        self.assertTrue(result)

    def test_booking_confirmation_failure(self):
        """Testing when confirmations fail (blame the IT department)"""
        # Example 1: Try to confirm a canceled booking (awkward)
        check_in = date.today() + timedelta(days=1)
        check_out = date.today() + timedelta(days=3)

        guest = self.hotel.registerGuest("Booking Canceler", "nope@changed.mind", "555-NOPE")
        room = self.hotel.rooms[201]  # Double room
        booking = self.hotel.makeBooking(guest, room, check_in, check_out)

        # Cancel the booking after having second thoughts
        booking.cancel()

        # Try to confirm the canceled booking (oops)
        result = booking.sendConfirmation()
        self.assertFalse(result)

        # Example 2: Missing information = no confirmation
        guest2 = self.hotel.registerGuest("Forgetful Freddie", "what@was.that", "555-HUH?")
        room2 = self.hotel.rooms[301]  # Suite room
        booking2 = self.hotel.makeBooking(guest2, room2, check_in, check_out)

        # Erase important info (happens when I don't get enough coffee)
        booking2.checkInDate = None

        # Try to send confirmation with missing info
        with self.assertRaises(ValueError):
            booking2.sendConfirmation()

    # 5. Invoice Generation Tests
    def test_invoice_generation(self):
        """Testing if we can make people pay for things"""
        # Set up dates
        check_in = date.today() + timedelta(days=1)
        check_out = date.today() + timedelta(days=4)  # 3 nights stay

        # Example 1: Basic boring invoice
        guest = self.hotel.registerGuest("Money Bags", "rich@person.com", "555-CASH")
        room = self.hotel.rooms[101]  # Single room, $100 per night
        booking = self.hotel.makeBooking(guest, room, check_in, check_out)

        # Create invoice
        invoice_date = date.today()
        invoice = Invoice(1, invoice_date, booking.totalPrice, 0.08, 0, 0)

        # Math is hard, let's check our work
        total = invoice.calculateTotal()
        self.assertEqual(booking.totalPrice, 300)  # 3 nights at $100
        self.assertEqual(total, 324)  # $300 + 8% tax = $324

        # Example 2: Fancy invoice with discount for cool people
        guest2 = self.hotel.registerGuest("Discount Hunter", "coupon@clipper.com", "555-SAVE")
        guest2.loyaltyPoints = 150  # Silver status
        guest2.loyaltyStatus = "Silver"

        room2 = self.hotel.rooms[301]  # Suite room, $300 per night
        booking2 = self.hotel.makeBooking(guest2, room2, check_in, check_out)

        # Create invoice with sweet discount
        invoice2 = Invoice(2, invoice_date, booking2.totalPrice, 0.08, 0.1, 0)
        total2 = invoice2.calculateTotal()

        # Math time again (ugh)
        # 3 nights at $300 = $900, 10% discount = $810, plus 8% tax = $874.80
        self.assertEqual(booking2.totalPrice, 900)
        discounted_subtotal = invoice2.applyDiscount(booking2.totalPrice, 0.1)
        self.assertEqual(discounted_subtotal, 810)
        self.assertEqual(total2, 874.80)

    def test_invoice_generation_with_services(self):
        """Testing invoices with extra stuff people order"""
        # Set up dates
        check_in = date.today() + timedelta(days=1)
        check_out = date.today() + timedelta(days=3)  # 2 nights stay

        # Example 1: Room service for a hungry customer
        guest = self.hotel.registerGuest("Hungry Harry", "alwayshungry@food.net", "555-FOOD")
        room = self.hotel.rooms[201]  # Double room, $150 per night
        booking = self.hotel.makeBooking(guest, room, check_in, check_out)

        # Add ridiculously expensive room service
        service = self.hotel.requestService(guest, "Room Service", "Tiny Burger With Fancy Name", 50.0, booking)
        booking.services.append(service)

        # Calculate total with overpriced food
        updated_total = booking.calculateTotalPrice()
        self.assertEqual(updated_total, 350)  # 2 nights at $150 + $50 for tiny burger

        # Create invoice
        invoice = Invoice(3, date.today(), updated_total, 0.08, 0, 0)
        final_total = invoice.calculateTotal()
        self.assertEqual(final_total, 378)  # $350 + 8% tax

        # Example 2: Guest who orders everything
        guest2 = self.hotel.registerGuest("Service Addict", "need@everything.com", "555-MORE")
        room2 = self.hotel.rooms[301]  # Suite room, $300 per night
        booking2 = self.hotel.makeBooking(guest2, room2, check_in, check_out)

        # Add spa service
        service1 = self.hotel.requestService(guest2, "Spa", "Massage By Trainee", 100.0, booking2)
        booking2.services.append(service1)

        # Add transportation
        service2 = self.hotel.requestService(guest2, "Transport", "Ride In Manager's Car", 75.0, booking2)
        booking2.services.append(service2)

        # Calculate total with all the extras
        updated_total2 = booking2.calculateTotalPrice()
        self.assertEqual(updated_total2, 775)  # 2 nights at $300 + $100 + $75 services

        # Create invoice with pity discount
        invoice2 = Invoice(4, date.today(), updated_total2, 0.08, 0.05, 0)
        discounted = invoice2.applyDiscount(updated_total2, 0.05)
        self.assertEqual(discounted, 736.25)  # $775 with 5% discount

        final_total2 = invoice2.calculateTotal()
        self.assertEqual(final_total2, 795.15)  # $736.25 + 8% tax

    # 6. Processing Different Payment Methods Tests
    def test_payment_processing(self):
        """Testing if money machine go brrrr"""
        check_in = date.today() + timedelta(days=1)
        check_out = date.today() + timedelta(days=3)

        # Example 1: Credit card that hopefully won't bounce
        guest = self.hotel.registerGuest("Maxed Out", "no.credit.left@debt.com", "555-DEBT")
        room = self.hotel.rooms[201]  # Double room
        booking = self.hotel.makeBooking(guest, room, check_in, check_out)

        # Create payment
        payment = Payment(1, booking.totalPrice, date.today(), "Credit Card", "Pending")

        # Process payment (fingers crossed)
        result = payment.processPayment()
        self.assertTrue(result)
        self.assertEqual(payment.status, "Completed")

        # Example 2: Pay with weird app that only gen Z uses
        guest2 = self.hotel.registerGuest("Zoomer", "ok@boomer.lol", "555-TikTok")
        room2 = self.hotel.rooms[301]  # Suite room
        booking2 = self.hotel.makeBooking(guest2, room2, check_in, check_out)

        # Create payment
        payment2 = Payment(2, booking2.totalPrice, date.today(), "SuperCoolPayApp", "Pending")

        # Process payment
        result2 = payment2.processPayment()
        self.assertTrue(result2)
        self.assertEqual(payment2.status, "Completed")

        # Check receipt (nobody reads these anyway)
        receipt = payment2.generateReceipt()
        self.assertIsNotNone(receipt)
        self.assertTrue(isinstance(receipt, str))
        self.assertTrue("SuperCoolPayApp" in receipt)

    def test_payment_refunds(self):
        """Testing when people want their money back"""
        check_in = date.today() + timedelta(days=1)
        check_out = date.today() + timedelta(days=3)

        # Example 1: Complete refund (found a better hotel)
        guest = self.hotel.registerGuest("Refund Randy", "gimme@money.back", "555-BACK")
        room = self.hotel.rooms[201]  # Double room
        booking = self.hotel.makeBooking(guest, room, check_in, check_out)

        # Process payment then change mind
        payment = Payment(3, booking.totalPrice, date.today(), "Credit Card", "Pending")
        payment.processPayment()

        # Ask for refund with sad face
        result = payment.refund(booking.totalPrice)
        self.assertTrue(result)
        self.assertEqual(payment.status, "Refunded")

        # Example 2: Partial refund (didn't use minibar)
        guest2 = self.hotel.registerGuest("Half Refund", "some@money.back", "555-HALF")
        room2 = self.hotel.rooms[301]  # Suite room
        booking2 = self.hotel.makeBooking(guest2, room2, check_in, check_out)

        # Process payment
        payment2 = Payment(4, booking2.totalPrice, date.today(), "Dad's Credit Card", "Pending")
        payment2.processPayment()

        # Ask for half back
        partial_amount = booking2.totalPrice / 2
        result2 = payment2.refund(partial_amount)
        self.assertTrue(result2)
        self.assertEqual(payment2.status, "Partially Refunded")

    # 7. Displaying Reservation History Tests
    def test_view_reservation_history(self):
        """Testing if we can see past regrettable hotel choices"""
        # Create a guest who stays way too often
        guest = self.hotel.registerGuest("Hotel Addict", "nomad@nowhere.home", "555-MOVE")

        # Example 1: Check history when guest is new
        history = guest.viewReservationHistory()
        self.assertEqual(len(history), 0)  # Should be empty like my brain during finals

        # Create bookings from past, present, and future
        today = date.today()
        room1 = self.hotel.rooms[101]  # Single room

        # Booking 1 - past stay (regrettable decision)
        past_check_in = today - timedelta(days=10)
        past_check_out = today - timedelta(days=8)
        booking1 = self.hotel.makeBooking(guest, room1, past_check_in, past_check_out)
        booking1.complete()  # It's over now
        guest.bookingHistory.append(booking1)

        # Booking 2 - current stay (happening now, probably with loud neighbors)
        current_check_in = today - timedelta(days=1)
        current_check_out = today + timedelta(days=1)
        room2 = self.hotel.rooms[201]  # Double room
        booking2 = self.hotel.makeBooking(guest, room2, current_check_in, current_check_out)
        guest.bookingHistory.append(booking2)

        # Booking 3 - future stay (optimistic planning)
        future_check_in = today + timedelta(days=30)
        future_check_out = today + timedelta(days=35)
        room3 = self.hotel.rooms[301]  # Suite room
        booking3 = self.hotel.makeBooking(guest, room3, future_check_in, future_check_out)
        guest.bookingHistory.append(booking3)

        # Example 2: Check history now that it's full of stuff
        history = guest.viewReservationHistory()
        self.assertEqual(len(history), 3)

        # Make sure all bookings are there
        booking_ids = [booking.bookingId for booking in history]
        self.assertIn(booking1.bookingId, booking_ids)
        self.assertIn(booking2.bookingId, booking_ids)
        self.assertIn(booking3.bookingId, booking_ids)

    def test_filter_reservation_history(self):
        """Testing if we can filter out embarrassing past stays"""
        # Make a guest with messy booking history
        guest = self.hotel.registerGuest("Party Regret", "mistakes@were.made", "555-OOPS")

        today = date.today()

        # Example 1: Looking for completed stays
        # Add a past booking that's completed
        past_check_in = today - timedelta(days=20)
        past_check_out = today - timedelta(days=15)
        room1 = self.hotel.rooms[101]  # Single room
        booking1 = self.hotel.makeBooking(guest, room1, past_check_in, past_check_out)
        booking1.status = "Completed"  # It's over, finally
        guest.bookingHistory.append(booking1)

        # Add a canceled booking (changed mind after sobering up)
        room2 = self.hotel.rooms[201]  # Double room
        booking2 = self.hotel.makeBooking(guest, room2, past_check_in, past_check_out)
        booking2.cancel()
        guest.bookingHistory.append(booking2)

        # Find the completed ones
        completed_bookings = [b for b in guest.bookingHistory if b.status == "Completed"]
        self.assertEqual(len(completed_bookings), 1)
        self.assertEqual(completed_bookings[0].bookingId, booking1.bookingId)

        # Example 2: Looking for future bookings to maybe cancel
        # Add future booking for next party
        future_check_in = today + timedelta(days=10)
        future_check_out = today + timedelta(days=15)
        room3 = self.hotel.rooms[301]  # Suite room
        booking3 = self.hotel.makeBooking(guest, room3, future_check_in, future_check_out)
        guest.bookingHistory.append(booking3)

        # Find upcoming bookings (for planning escape routes)
        upcoming_bookings = [b for b in guest.bookingHistory if b.status == "Confirmed" and b.checkInDate > today]
        self.assertEqual(len(upcoming_bookings), 1)
        self.assertEqual(upcoming_bookings[0].bookingId, booking3.bookingId)

    # 8. Cancellation of a Reservation Tests
    def test_booking_cancellation(self):
        """Testing when people change their minds"""
        check_in = date.today() + timedelta(days=7)
        check_out = date.today() + timedelta(days=10)

        # Example 1: Normal cancellation (found a better deal)
        guest = self.hotel.registerGuest("Cheaper Elsewhere", "found@better.deal", "555-GONE")
        room = self.hotel.rooms[201]  # Double room
        booking = self.hotel.makeBooking(guest, room, check_in, check_out)

        # Room should be unavailable after booking
        self.assertFalse(room.isAvailable)

        # Cancel after finding Airbnb
        result = booking.cancel()
        self.assertTrue(result)
        self.assertEqual(booking.status, "Cancelled")

        # Room should be available again
        self.assertTrue(room.isAvailable)

        # Example 2: Cancellation with refund (mom said no)
        guest2 = self.hotel.registerGuest("Mom Said No", "grounded@home.now", "555-MOM")
        room2 = self.hotel.rooms[301]  # Suite room
        booking2 = self.hotel.makeBooking(guest2, room2, check_in, check_out)

        # Pay with mom's credit card
        payment = Payment(5, booking2.totalPrice, date.today(), "Mom's Credit Card", "Pending")
        payment.processPayment()

        # Cancel and beg for refund
        booking2.cancel()
        refund_result = payment.refund(booking2.totalPrice)

        self.assertTrue(refund_result)
        self.assertEqual(payment.status, "Refunded")
        self.assertEqual(booking2.status, "Cancelled")

    def test_cancellation_restrictions(self):
        """Testing if we can cancel at the last minute"""
        today = date.today()

        # Example 1: Cancel way ahead (should be fine)
        future_check_in = today + timedelta(days=30)
        future_check_out = today + timedelta(days=33)

        guest = self.hotel.registerGuest("Early Canceller", "plans@change.alot", "555-PLAN")
        room = self.hotel.rooms[201]  # Double room
        booking = self.hotel.makeBooking(guest, room, future_check_in, future_check_out)

        # Cancel long before
        result = booking.cancel()
        self.assertTrue(result)
        self.assertEqual(booking.status, "Cancelled")

        # Example 2: Try to cancel at last minute (after realizing how far hotel is)
        last_minute_check_in = today + timedelta(days=1)  # Tomorrow!
        last_minute_check_out = today + timedelta(days=3)

        guest2 = self.hotel.registerGuest("Last Minute Larry", "always@late.com", "555-LATE")
        room2 = self.hotel.rooms[301]  # Suite room
        booking2 = self.hotel.make