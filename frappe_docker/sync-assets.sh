#!/bin/bash
docker cp frappe_docker-backend-1:/home/frappe/frappe-bench/sites/assets/edu_theme /tmp/
docker cp /tmp/edu_theme frappe_docker-frontend-1:/home/frappe/frappe-bench/sites/assets/
docker cp frappe_docker-backend-1:/home/frappe/frappe-bench/sites/assets/education /tmp/
docker cp /tmp/education frappe_docker-frontend-1:/home/frappe/frappe-bench/sites/assets/
docker cp frappe_docker-backend-1:/home/frappe/frappe-bench/sites/assets/library_management /tmp/
docker cp /tmp/library_management frappe_docker-frontend-1:/home/frappe/frappe-bench/sites/assets/
rm -rf /tmp/edu_theme /tmp/education /tmp/library_management
