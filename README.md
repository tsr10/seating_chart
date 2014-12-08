seating_chart
=============
See the about.html for user instructions.

To run:
Open the virtualenv by running `workon seating_chart`.

Start the redis process by running `redis-stable/src/redis-server`.

In a separate window with the virtualenv activated, run the celery process by typing `celery -A seating_chart worker -l info`.

Once this process is running, you can run the site by running `./manage.py runserver`.

After this, navigate to localhost:8000 and you'll see the site.