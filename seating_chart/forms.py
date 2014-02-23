from django import forms
from django.forms import extras

from models import Person, Dinner, PersonToDinner

import datetime

#Controls the page where we add new people to an account
class _AddPersonForm(forms.Form):
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)

    def clean(self):
        super(_AddPersonForm, self).clean()

        first_name = self.cleaned_data.get('first_name', None)
        last_name = self.cleaned_data.get('last_name', None)

        if Person.objects.filter(first_name__iexact=first_name, last_name__iexact=last_name, account=self._account).exists():
            raise forms.ValidationError('This person is already in your account')

        return self.cleaned_data

def add_person_form_factory(account):

    class Form(_AddPersonForm):
        _account = account

    return Form

#Controls the page where we add new dinners.
class _AddDinnerForm(forms.Form):
    date = forms.DateField(required=True, label='Date of dinner',
        widget=extras.SelectDateWidget(
            years=tuple(reversed(range(datetime.date.today().year, datetime.date.today().year + 2))),
            attrs={'empty_label': ''}
        )
    )

def add_dinner_form_factory(account):

    class Form(_AddDinnerForm):
        _account = account

    return Form

#Controls the page where we add people to dinners.
class _AddPersonToDinnerForm(forms.Form):
    pass

    def clean(self):
        super(_AddPersonToDinnerForm, self).clean()

        person = self.cleaned_data.get('person', None)
        dinner = self._dinner

        if PersonToDinner.objects.filter(person=person, dinner=dinner).exists():
            raise forms.ValidationError("This person is already attached to this dinner!")

        return self.cleaned_data

def add_person_to_dinner_form_factory(dinner, account):

    class Form(_AddPersonToDinnerForm):
        person = forms.ModelChoiceField(Person.objects.filter(account=account))
        _dinner = dinner

    return Form

class _GenerateSeatingChartForm(forms.Form):
    pass

def generate_seating_chart_form_factory(dinner):

    class Form(_GenerateSeatingChartForm):
        def __init__(self, *args, **kwargs):
            super(Form, self).__init__(*args, **kwargs)
            for i in range(0, dinner.number_of_pairs()):
                self.fields['seat__' + str(i) + '__left'] = forms.ModelChoiceField(PersonToDinner.objects.filter(dinner=dinner), required=True)
                self.fields['seat__' + str(i) + '__right'] = forms.ModelChoiceField(PersonToDinner.objects.filter(dinner=dinner), required=True)

        _dinner = dinner
        head = forms.ModelChoiceField(PersonToDinner.objects.filter(dinner=dinner), required=True)
        foot = forms.ModelChoiceField(PersonToDinner.objects.filter(dinner=dinner), required=True)

    return Form







