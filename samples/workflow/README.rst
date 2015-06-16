Sample Project for Workflow Builder
-----------------------------------

django project framework for the `workflow builder` challenge.


Contents
~~~~~~~~

Custom design for the `workflow builder` should be placed in ``templates/workflow.html``. The template already contains sample code for loading recipe through AJAX (AJAJ) call to the RESTful API.

.. code-block::

    workflow
    ├── README.rst
    ├── datagator
    │   ├── __init__.py
    │   ├── settings.py
    │   ├── templates
    │   │   └── workflow.html
    │   ├── urls.py
    │   ├── views.py
    │   └── wsgi.py
    ├── db.sqlite3
    └── manage.py


Launch development web server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block::

    $ python manage.py runserver 127.0.0.1:8000

More information on django project management can be found at `<https://docs.djangoproject.com/en/1.8/ref/django-admin/>`_.


Open the stub WorkFlowView
~~~~~~~~~~~~~~~~~~~~~~~~~~

Open a web browser and visit `<http://127.0.0.1:8000/Pardee/Workflow_Sample/IGO_Weighted_Membership.recipe>`_.
