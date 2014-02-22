from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^generate_seating_chart/(?P<pk>\d+)$', 'seating_chart.views.generate_seating_chart', name='generate_seating_chart'),

    url(r'^add_person$', 'seating_chart.views.add_person', name='add_person'),

    url(r'^add_dinner$', 'seating_chart.views.add_dinner', name='add_dinner'),

    url(r'^add_person_to_dinner/(?P<pk>\d+)$', 'seating_chart.views.add_person_to_dinner', name='add_person_to_dinner'),

)
