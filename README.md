# Databse

```bash
$ sudo su - postgres
$ psql

CREATE DATABASE plefe_base;
CREATE USER plefe_user WITH PASSWORD 'plefe';
ALTER ROLE plefe_user SET client_encoding TO 'utf8';
ALTER ROLE plefe_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE plefe_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE plefe_base TO plefe_user;
\q

exit;
```

```bash
$ sudo su - postgres
$ psql

CREATE DATABASE plefe_test;
CREATE USER plefe_user_test WITH PASSWORD 'plefe';
ALTER ROLE plefe_user_test SET client_encoding TO 'utf8';
ALTER ROLE plefe_user_test SET default_transaction_isolation TO 'read committed';
ALTER ROLE plefe_user_test SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE plefe_test TO plefe_user_test;
ALTER USER plefe_user_test WITH SUPERUSER;

\q

exit;
```
