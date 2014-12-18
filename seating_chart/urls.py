from django.conf.urls import patterns, url

urlpatterns = patterns('',
    # The view for manually placing diners before generating a new seating chart.
    url(r'^arrange_seating_chart/(?P<pk>\d+)$', 'seating_chart.views.arrange_seating_chart', name='arrange_seating_chart'),

    # The view that calls the celery task to arrange diners.
    url(r'^generate_seating_chart/(?P<pk>\d+)$', 'seating_chart.views.generate_seating_chart', name='generate_seating_chart'),

    # A view for adding a new person to the database.
    url(r'^add-person$', 'seating_chart.views.add_person', name='add_person'),

    # For adding a new dinner to the database.
    url(r'^add-dinner$', 'seating_chart.views.add_dinner', name='add_dinner'),

    # Deletes a dinner from the DB and redirects back to add_dinner.
    url(r'^delete-dinner/(?P<pk>\d+)$', 'seating_chart.views.delete_dinner', name='delete_dinner'),

    # For adding a new person to a dinner.
    url(r'^add-person-to-dinner/(?P<pk>\d+)$', 'seating_chart.views.add_person_to_dinner', name='add_person_to_dinner'),

    # The about page, for information about the website.
    url(r'^about$', 'seating_chart.views.about', name='about'),

)
