from django.tests import TestCase
from seating_chart.models import Person, Dinner, PersonToDinner
from seating_chart.utils import get_placed_seats

class SeatingChartUtilsTests(TestCase):

	def setUp(self):
		pass

	def test_get_placed_seats(self):
		ted = Person(name='Ted')
		ted.save()
		brett = Person(name='Brett')
		brett.save()
		request_dict = {'1' : 'Ted',
		'2' : 'Brett'}
		placed_seats = get_placed_seats(request_dict=request_dict)
		self.assertEqual(placed_seats, '')