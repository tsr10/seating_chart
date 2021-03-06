from django import forms
from django.forms import extras

from models import Person, Seating

from crispy_forms.helper import FormHelper

import datetime


# Controls the page where we add new people to an account
class _AddPersonForm(forms.Form):
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)

    def clean(self):
        super(_AddPersonForm, self).clean()

        first_name = self.cleaned_data.get('first_name', None)
        last_name = self.cleaned_data.get('last_name', None)

        if first_name and last_name:
            if Person.objects.filter(first_name__iexact=first_name, last_name__iexact=last_name, account=self._account).exists():
                raise forms.ValidationError('This person is already in your account')

        return self.cleaned_data


def add_person_form_factory(account):

    class Form(_AddPersonForm):
        _account = account

    return Form


# Controls the page where we add new dinners.
class _AddDinnerForm(forms.Form):
    date = forms.DateField(required=True,
                           label='Date of dinner',
                           widget=extras.SelectDateWidget(years=tuple(reversed(range(datetime.date.today().year, datetime.date.today().year + 2))),
                                                          attrs={'empty_label': ''})
                           )


def add_dinner_form_factory(account):

    class Form(_AddDinnerForm):
        _account = account

    return Form


# Controls the page where we add people to dinners.
class _AddSeatingForm(forms.Form):
    pass

    def clean(self):
        super(_AddSeatingForm, self).clean()

        person = self.cleaned_data.get('person', None)
        dinner = self._dinner

        if Seating.objects.filter(person=person, dinner=dinner).exists():
            raise forms.ValidationError("This person is already attached to this dinner!")

        return self.cleaned_data


def add_seating_form_factory(dinner, account):

    class Form(_AddSeatingForm):
        person = forms.ModelChoiceField(Person.objects.filter(account=account).exclude(seating__dinner=dinner))
        _dinner = dinner

    return Form


class _ArrangeSeatingChartForm(forms.Form):

    def clean(self):
        super(_ArrangeSeatingChartForm, self).clean()

        seat_list = []

        dinner = self._dinner

        for i in range(0, dinner.attendees()):
            seat = self.cleaned_data.get('seat__' + str(i), None)

            if seat:
                seating = seat
                seating.seat_number = i
                if i == 0:
                    seating.is_head = True
                elif (i == dinner.attendees() - 1):
                    seating.is_foot = True
                seat_list.append(seating)

        if len(seat_list) != len(set(seat_list)):
            raise forms.ValidationError('The same diner has been assigned to a seat twice. Please check your inputs.')

        for seating in seat_list:
            seating.manually_placed_diner = True
            seating.save()

        return self.cleaned_data


def arrange_seating_chart_form_factory(dinner):

    class Form(_ArrangeSeatingChartForm):
        def __init__(self, *args, **kwargs):
            self.helper = FormHelper()
            super(Form, self).__init__(*args, **kwargs)
            for i in dinner.get_seating_order():
                if i != "None":
                    self.fields['seat__' + str(i)] = forms.ModelChoiceField(Seating.objects.filter(dinner=dinner), required=False)

        _dinner = dinner

    return Form
