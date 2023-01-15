============
Installation
============

NASAaccess can be installed in production manually .

Docker
~~~~~~
Docker Image: `byuhydro/wde <https://hub.docker.com/r/byuhydro/wde>`_

The WDE docker image installation has support for different types of architectures:

Two Images: one PostgreSQL image and WDE image.

  - Using a `docker-compose.yml <https://github.com/BYU-Hydroinformatics/water-data-explorer-whos/blob/inmet-WDE/docker_files/docker-compose.yml>`_ to run both containers declaring environment variables::

       docker-compose up

  - Running two different containers with a file containing the environment variables::

       docker run --name postgres -e POSTGRES_PASSWORD=passpass -p 5432:5432 -d postgres

       docker run -it --env-file env.txt -p 80:80 byuhydro/wde

One Image: one WDE image connected to a local instance of PostgreSQL or an Amazon RSD postgreSQL database.

  - Using local instance of PostgreSQL with a file containing the environment variables::

      docker run -it --env-file env.txt -p 80:80 byuhydro/wde

  - Using an Amazon RSD postgreSQL database with a file containing the environment variables::

      docker run -it --env-file env.txt -p 80:80 byuhydro/wde

.. note::
   Currently there is only support for AWS if an cloud based database is used.

.. note::
   env.txt sample files can be found in `here <https://github.com/BYU-Hydroinformatics/water-data-explorer-whos/tree/master/docker_files/helpful_files>`_

Regular Production Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When installing WDE using the regular installation process in a production env, you will need to install the Tethys Platform first and
then install WDE app. Follow this `guide <http://docs.tethysplatform.org/en/stable/installation/production.html>`_ for an
step by step process.

Regular Development Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

WDE can also be installed in your local computer without the need to do a production installation in any server. You will need
to install the Tethys Platform first and then WDE app.

  - Use this `guide <http://docs.tethysplatform.org/en/stable/installation.html>`_ to install the Tethys Platform.
  - Use this `guide <http://docs.tethysplatform.org/en/stable/installation/application.html>`_ to install WDE in the Tethys Platform.
