# BizCardX-Extracting Business Card Data with OCR

## Introduction 

* BizCardX: Extracting Business Card Data with OCR Overview BizCardX is a Streamlit web application which extracts data from business cards using Optical Character Recognition (OCR). Users can upload an image of a business card and the application uses the easyOCR library to extract relevant information from the card. The extracted information is then displayed in a user-friendly format and can be stored in a MySQL database for future reference.

![Intro GUI](https://github.com/vishwasbasotra/BizCardX-Extracting-Business-Card-Data-with-OCR/blob/main/demo.png)
## Project Overview
* BizCardX is a user-friendly tool for extracting information from business cards. The tool uses OCR technology to recognize text on business cards and extracts the data into an SQL database after classification using regular expressions. Users can access the extracted information using a GUI built using Streamlit. The BizCardX application is a simple and intuitive user interface that guides users through uploading the business card image and extracting its information. The extracted information would be displayed clean and organised, and users could easily add it to the database with a click of a button. Further, the data stored in the database can be easily read, updated and deleted by the user as per the requirement.

## Developer Guide 

### 1. Tools install

* VS Code.
* Jupyter notebook.
* Python 3.11.0 or higher.
* MySQL
* Git

### 2. Requirement Libraries to Install

* pip install pandas numpy os json requests subprocess mysql.connector sqlalchemy pymysql streamlit plotly.express

### 3. Import Libraries
* import pandas as pd
* import easyocr
* import mysql.connector
* import sqlalchemy
* from sqlalchemy import create_engine

**Dashboard libraries**
* import streamlit as st
* import plotly.express as px
