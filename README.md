# The Arbitron-3001

The Arbitron-3001 is a project born out of a fascination with options trading and arbitrage, inspired by one of my mathematics courses at The City College of New York. While not a gambler myself, I had enough knowledge to see the parallels between making multiple bets on a single spotting event, and trading options on the stock market. Thus, The Arbitron-3001 was created.

## Introduction

The Arbitron-3001 is a real-time tool designed to identify arbitrage betting opportunities in professional and college sports. Currently covering the NBA, NHL, MLB, and NCAA men’s basketball, it leverages Python with Flask and SQLAlchemy for backend processing, React.js for frontend presentation, and incorporates proven methods of data analysis and visualization.

## Current Progress as of April 15, 2024

The ETL process created for this project works on the backend, however, I have thus far been unsuccessful in automating this process, or in giving it the ability to run unsupervised. This is the biggest issue that this project continues to face. Once I am able to automate the process and start aggregating data, I believe I will also then have a better idea of how I would like to display the data I've collected.

The frontend still needs to be built out. This is in large part due to needing some time to figure out how to manage the demands of my job search while very much needing employment. I don't forsee the frontend being particularly complicated to design, but I have found that the data collection aspect of the project is currently inhibiting me fromn making progress on the frontend.

## Usage

To use The Arbitron-3001, simply execute the program. It will automatically scan for arbitrage opportunities and present them in an organized manner for further analysis or action.

## Features

### Real-time Identification

Upon execution, The Arbitron-3001 scans for arbitrage betting opportunities across multiple sports.

### Comprehensive Coverage

It tracks major professional leagues including the NBA, NHL, and the MLB, as well as NCAA men's basketball.

### Custom ETL Processes

Utilizes web scraping to extract money-line odds from various Bookkeepers, transforming them into usable data. It then organizes relevant information into a Flask-SQL database for easy access and analysis.

## Technologies Used and Implementation

The Arbitron-3001 project incorporates various technologies for its development and functionality:

### Python

The core programming language used for backend development, providing robustness and versatility.

### Flask

A micro web framework for Python, utilized to develop the backend of the application. Flask handles routing, request handling, and responses.

### SQLAlchemy

A Python SQL toolkit and Object-Relational Mapping (ORM) library employed for database interactions. SQLAlchemy simplifies database management and querying.

### Requests

A Python library for making HTTP requests, utilized to fetch data from external websites.

### BeautifulSoup (bs4)

A Python library for web scraping, used to parse HTML content obtained from external websites.

### React.js

A JavaScript library for building user interfaces, employed for the frontend presentation of the application. React.js enables dynamic and responsive user experiences.

### Flask-Migrate

A Flask extension utilized for handling database migrations, simplifying the management of database schema changes.

### Flask-Bcrypt

A Flask extension for password hashing, securely hashing user passwords before storing them in the database.

### Flask-CORS

A Flask extension for Cross-Origin Resource Sharing (CORS) support, enabling communication between frontend and backend components hosted on different domains.

### SQLAlchemy MetaData

SQLAlchemy's MetaData is used for naming conventions and configuration.

## Future Developments

### User Interface Improvements

I will build, and continue to enhance the frontend interface over time for better user experience. Semantic UI will be utilized in combination to React.js for a seamless user experience.

### Scheduled Scraper

A timer is being implemented to run the scraper every 15 minutes, enhancing data accuracy and sample size, as well as continued refinement of the scraper to improve accuracy and efficiency.

### Data Visualization and Advanced Analysis

A rigorous analysis of collected data is planned to uncover any emerging patterns related to arbitrage in sports betting. These will mainly be related to the percentage profit each team, league, and Bookkeeper generate per arbitrage opportunity. React.js will be used as the backbone, and data visualization tools (TBD) will display any discovered patterns effectively.

## Acknowledgments

Special thanks to Professor Eli Amzallag at The City College of New York for sparking the initial inspiration for this project.

## License

This project is licensed under the MIT License. Feel free to modify and distribute it as needed.

## Contributions

Contributions to The Arbitron-3001 project are welcome. Feel free to submit pull requests or reach out with suggestions for improvements.

## Disclaimer

The Arbitron-3001 is intended for educational and informational purposes only. Users are responsible for their own betting decisions, and the creators of this project do not endorse or encourage gambling.

## If you or a loved one has a gambling addiction please call 1-800-GAMBLER
