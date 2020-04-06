#!/bin/bash
createdb "mercury"
psql -c 'create database mercury;' -U postgres