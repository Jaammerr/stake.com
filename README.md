## Install 

Install [Docker](https://docs.docker.com/install/) and [Docker Compose](https://docs.docker.com/compose/install/).

Then, clone this repository and run:

```bash
docker-compose up -d --build
```

After that, check if the web application is running correct:
    
```bash
docker-compose logs -f CONTAINER_ID
```

If errors are shown, simply restart the web container:

```bash
docker-compose restart CONTAINER_ID
```


## Database

To change the database configuration, edit the file `api/database/settings.py`.

It is possible to use a different database engine, such as MySQL or PostgreSQL. To do that, change the `ENGINE` parameter in the `api/database/settings.py` file.


## Scraper:

Scraper is not running by default. To run it, execute the following command:

Dir: `scraper/` (Don't forget to install the requirements)

```bash
python3 main.py
```

It's recommended to run the scraper in a linux "demon" or "screen". 









