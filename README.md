poderocrawler
==========

poderocrawler is a Python module that implements a webcrawler for the [poderopedia website](http://www.poderopedia.org/).

If you'd like to get in touch, email me at gonzalo.huerta  _AT_ uai.cl or ping me [on Twitter](http://twitter.com/gohucan).

Regards,
Gonzalo

Features
--------

* Extracts persons, organizations and companies.
* Save the data to a mySQL database.

Installation
------------

* To install the requirements do

      $ pip install -r requirements.txt

* Now you need to create the mysql database. Run the sql/create.sql script to do so

      $ mysql -u YOUR_USERNAME -p < sql/create.sql

* That´s all but I do recommend to use this program inside a virtual environment. Please check [this document](http://docs.python-guide.org/en/latest/dev/virtualenvs/) for more information.

Running
--------

To run the samples first you need to copy the file env.sample to .env and modify it to reflect your mySQL database configuration.

Once done, simply run the following command:

    $ python main.py

License
-------

poderocrawler is using the standard [Apache license 2.](http://www.apache.org/licenses/LICENSE-2.0).
