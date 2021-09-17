# Deployment instructions

1. Setup config via variables in `.env` file:\
``$ vi .env``
2. First run with auto date migration:\
`$ docker-compose up --build -d`
3. Login at site: [http://localhost/admin/](http://localhost/admin/)
4. Explore API at site: [http://localhost/api/v1/movies/](http://localhost/api/v1/movies/)
5. To stop app run:\
`$ docker-compose stop`
6. To star app again run:\
`$ docker-compose start`
7. To restart app run:
`$ docker-compose restart`
8. To remove app run:
`$ docker-compose down -v`