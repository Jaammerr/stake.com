## Information
This project is designed to collect all user bets on the site [stake.com](https://stake.com) and analyze them. Using the WEB GUI, you can set various filters and add telegram channels to receive information about bets. All data is saved to a database.

# Screenshots

<a href="https://imgbb.com/"><img src="https://i.ibb.co/YdwVdwF/1.png" alt="1" border="0" width=300 height=200></a>
<a href="https://ibb.co/5kWPW1W"><img src="https://i.ibb.co/m0C3CRC/2.png" alt="2" border="0" width=500></a>
<a href="https://ibb.co/3mXsM32"><img src="https://i.ibb.co/1GVndg1/3.png" alt="3" border="0" width=500></a>
<a href="https://ibb.co/PcW0r5b"><img src="https://i.ibb.co/pfK513s/4.png" alt="4" border="0" width=500></a>
<a href="https://ibb.co/DGB5Cbw"><img src="https://i.ibb.co/HNcnz2G/5.png" alt="5" border="0" width=500></a>




## Install 

-- Don't forget to set up config files in api and scraper folders (configuration/config.yaml)

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









