from django.contrib import admin
from seating_chart.models import Account, Person, Dinner, PersonToDinner


class AccountAdmin(admin.ModelAdmin):
    pass


class PersonAdmin(admin.ModelAdmin):
    pass


class DinnerAdmin(admin.ModelAdmin):
    pass


class PersonToDinnerAdmin(admin.ModelAdmin):
    pass

admin.site.register(Account, AccountAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Dinner, DinnerAdmin)
admin.site.register(PersonToDinner, PersonToDinnerAdmin)
