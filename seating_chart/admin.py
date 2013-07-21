from django.contrib import admin
from seating_chart.models import Person, Dinner, PersonToDinner

class PersonAdmin(admin.ModelAdmin):
	pass

class DinnerAdmin(admin.ModelAdmin):
	pass

class PersonToDinnerAdmin(admin.ModelAdmin):
	pass

admin.site.register(Person, PersonAdmin)
admin.site.register(Dinner, DinnerAdmin)
admin.site.register(PersonToDinner, PersonToDinnerAdmin)