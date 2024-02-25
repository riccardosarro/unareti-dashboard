# Unareti Dashboard

This is the README file for the Unareti Dashboard project.

## Description

The Unareti Dashboard is a web application built using Python and Flask framework. It provides a user-friendly interface to visualize and analyze data coming from lectures of Unareti electric meter. The dashboard is designed to be used by Unareti's customers to monitor their energy consumption and to help them make informed decisions about their energy usage.

## Installation

1. Clone the repository:

  ```bash
  git clone https://github.com/unareti-dashboard.git
  ```

2. Install the required dependencies:

  ```bash
  pip install -r requirements.txt
  ```

3. Run the application:

  ```bash
  python app.py
  ```

## Usage

#### Configuration

Put the data files in the `data` directory. The data files should be in CSV format and the following columns are expected and used:
- **`DATA`**: Date of the reading
- **`ORA`**: Time of the reading
- **`CONSUMO_ATTIVA_PRELEVATA`**: Active consumption

The following columns instead will be expected and used in later versions:
- **`POD`**: Point of delivery
    *To allow the user to select different PODs*
- **`TIPO_DATO`**: Type of data (`E` as for effective data, `S` as for estimated data)
    *To allow the user to know if the data is estimated or effective*
- **`ATTIVA_IMMESSA`**: Active production
    *To allow the user to monitor the active production*

**Note:** It is highly recommended to rename the data files to a meaningful name, such as the year and month of the data, to allow the user to select the data to visualize. For example, `2021-01.csv` for the data of January 2021.

#### Running
To run the Unareti Dashboard, execute the following command:
  ```bash
  python app.py
  ```
