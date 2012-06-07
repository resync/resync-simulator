#!/bin/bash

echo "### Will run tests on local machine with files in /tmp"
rm -rf /tmp/rs_test
mkdir /tmp/rs_test
mkdir /tmp/rs_test/src
echo "I am file_a" > /tmp/rs_test/src/file_a
echo "I am file_b, bigger than file_a" > /tmp/rs_test/src/file_b
mkdir /tmp/rs_test/dst
echo "### Make sitemap for this local collection"
./resync-client -s /tmp/rs_test/src=/tmp/rs_test/src > /tmp/rs_test/src/sitemap.xml
ls -l /tmp/rs_test/src
echo "### Do resync... (should copy 2 new resources)"
./resync-client /tmp/rs_test/src/sitemap.xml /tmp/rs_test/dst
ls -l /tmp/rs_test/src /tmp/rs_test/dst
echo "### Do resync again, no changes"
./resync-client /tmp/rs_test/src/sitemap.xml /tmp/rs_test/dst
echo "### Updating file_a on src"
echo "I am the new version of file_a" > /tmp/rs_test/src/file_a
./resync-client -s /tmp/rs_test/src=/tmp/rs_test/src > /tmp/rs_test/src/sitemap.xml
ls -l /tmp/rs_test/src /tmp/rs_test/dst
echo "### Do resync... (should report 1 changed resource)"
./resync-client /tmp/rs_test/src/sitemap.xml /tmp/rs_test/dst
ls -l /tmp/rs_test/src /tmp/rs_test/dst
echo "### Delete file_a on src"
rm /tmp/rs_test/src/file_a
./resync-client -s /tmp/rs_test/src=/tmp/rs_test/src > /tmp/rs_test/src/sitemap.xml
ls -l /tmp/rs_test/src /tmp/rs_test/dst
echo "### Do resync... (should report 1 deleted resource, but no update)"
./resync-client /tmp/rs_test/src/sitemap.xml /tmp/rs_test/dst
ls -l /tmp/rs_test/src /tmp/rs_test/dst
echo "### Do resync... (should report 1 deleted resource, now actually deletes)"
./resync-client --delete /tmp/rs_test/src/sitemap.xml /tmp/rs_test/dst
ls -l /tmp/rs_test/src /tmp/rs_test/dst
