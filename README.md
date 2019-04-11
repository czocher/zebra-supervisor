[![Build Status](https://travis-ci.org/Czocher/zebra-supervisor.svg?branch=master)](https://travis-ci.org/Czocher/zebra-supervisor)
[![Coverage Status](https://coveralls.io/repos/github/Czocher/zebra-supervisor/badge.svg?branch=master)](https://coveralls.io/github/Czocher/zebra-supervisor?branch=master)

zebra-supervisor
=====

Zebra Evaluates a Basic Review of Algorithms

Running
====

To run the software install `docker` and `docker-compose`, edit the
`docker-compose.yml` file and set the `SECRET_KEY` to some random value.
The value can be generated with: `cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1`

Afterwards run:

```
docker-compose up --build
```

to start the software on port `80`.
