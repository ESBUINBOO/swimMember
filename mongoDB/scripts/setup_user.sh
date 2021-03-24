#!/bin/bash

echo "************************************************************"
echo "Setting up users..."
echo "************************************************************"

# create root user
nohup gosu mongodb mongo sm-dev --eval "db.createUser({user: 'root', pwd: 'toor', roles:[{ role: 'root', db: 'sm-dev' }, { role: 'read', db: 'local' }]});"

# create app user/database
nohup gosu mongodb mongo sm-dev --eval "db.createUser({ user: 'unicorn_user', pwd: 'magical_password', roles: [{ role: 'readWrite', db: 'sm-dev' }, { role: 'read', db: 'local' }]});"

echo "************************************************************"
echo "Shutting down"
echo "************************************************************"
nohup gosu mongodb mongo admin --eval "db.shutdownServer();"