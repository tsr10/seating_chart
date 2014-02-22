from django import forms
from django.forms import extras

from models import Person, Dinner

import datetime

class _AddPersonForm(forms.Form):
	first_name = forms.CharField(max_length=100, required=True)
	last_name = forms.CharField(max_length=100, required=True)

	def clean(self):
		super(_AddPersonForm, self).clean()

		self.person = None

		first_name = self.cleaned_data.get('first_name', None)
		last_name = self.cleaned_data.get('last_name', None)

		if Person.objects.filter(first_name__iexact=first_name, last_name__iexact=last_name, account=self._account).exists():
			raise forms.ValidationError('This person is already in your account')

		return self.cleaned_data

def add_person_form_factory(account):

	class Form(_AddPersonForm):
		_account = account

	return Form


class _AddDinnerForm(forms.Form):
    date = forms.DateField(required=True, label='Date of dinner',
        widget=extras.SelectDateWidget(
            years=tuple(reversed(range(1900, datetime.date.today().year + 1))),
            attrs={'empty_label': ''}
        )
    )
    attendees = forms.ChoiceField(choices=zip(range(5,50), range(5, 50)), initial=5)

def add_dinner_form_factory(account):

	class Form(_AddDinnerForm):
		_account = account

	return Form