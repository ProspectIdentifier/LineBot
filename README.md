# LineBot
[![Codeship Status for ProspectIdentifier/LineBot](https://app.codeship.com/projects/0e651fb0-f95e-0137-e981-0252b04994e7/status?branch=master)](https://app.codeship.com/projects/376962)<br />
This repository was created for IS DevOps Camp 2019

## Pre-Requisite
You need Python 3.6 or later to run Django.
We will deploy our bot webhook to heroku server and use Codeship CI/CD to automate the deployment process. You can use other server or deployment process if you want to

So basically you have to:

- Create [Codeship](https://codeship.com/) account
- Create [LINE Developers](https://developers.line.me/) channel
- Create [Heroku](https://dashboard.heroku.com/) app

## Run Django Project

- Install the requirements `pip3 install -r requirements.txt`

- Try the project by run `python3 manage.py runserver --settings=LineBot.settings.[environment variable]` and access it on **http://localhost:8000/**

  Environment Variable:

  - `production` - Production Server
  - `staging` - Staging server

  
