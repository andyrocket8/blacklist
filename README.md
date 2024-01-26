# Blacklist Project
## Intention
Blacklist is a tool for gathering and publish information about malicious IP addresses i.e. addresses used by attackers for various bad actions: IP flooding, brut force attacks etc.

Published lists can be used in network devices for blocking access to published IP addresses

Addresses information should be gathered by agents, agents provide actual information to addresses storage.
So we have always actual information about attackers and can block their activity on Interner connected devices with black listing.

Agent can add and delete records from application database with API calls.
IP addresses aggregate lists also might be obtained with API calls.
On DB modifications change history is gathered in background.

## Architecture
Language - Python 3.11

* API backbone - FastAPI framework
* Storage - Redis Database
* Background tasks - Celery
* Balancer - NGINX

### Example architecture with Fail2Ban source IP address info
IP Addresses information is gathered with blacklist-watcher application (https://github.com/andyrocket8/blacklist_watcher).
Banned IPs are pushed with external script or by router blacklisting feature (API call /addresses/banned/download)
![Blacklist architecture.png](Blacklist%20Architecture.png)

## Methods reference
Have a look on API methods with swagger URI (/api/openapi)

## OpenAPI description
You can publish API description based on OpenAPI (Swagger interface). Swagger URI is /api/openapi suffix after base service URI.
If you want to hide OpenAPI interface please use **SHOW_OPENAPI=false** in project .env file

## Securing application
Some methods changing database contents (.../add, .../delete) can be secured with API tokens.

Use **USE_AUTHORIZATION=true** option in .env file for securing your installation.
Tokens should also be created with **manage.py** script (see description below in **Deployment** section)

## Deployment

### Deploy with docker compose
Use docker-compose.yml for production depolyment

Please set ENV_FILE for valid configuration options. You can create .env file and pass it in ENV_FILE variable

Example of compose start
```
export ENV_FILE=./.env && docker compose up -d
```

With container force rebuild
```
export ENV_FILE=./.env && docker compose up -d --build
```
Don't forget to set **REDIS_HOST=redis** for using redis instance in compose bundle (name is set in compose file)

### Create application tokens
If you configure use of secure tokens (with **USE_AUTHORIZATION=true**) you should create at least one agent token for addresses management
Use manage.py script for token creation

#### Creation of agent token
Start **manage.py** with **tokens** option
Specify agent token with **--agent** parameter. It should be valid UUID value.

Example
```
source .venv/bin/activate
python manage.py --agent <some UUID value>
```
Don't forget activate virtual env if run inside deployed container
#### Creation of administrator token
Start **manage.py** with **tokens** option
Specify admin token with **--admin** parameter

Example
```
source .venv/bin/activate
python manage.py --admin <some UUID value>
```

## Configuration
Configuration file for Blacklist installation implemented by ENV file.
Default ENV file name is .env
Description of ENV file entries is in /src/core/config.py

Attention: lower cased names in config.py actually included in ENV file uppercase, i.e. redis_password should be REDIS_PASSWORD

### Securing redis
If redis deployed with authentication you should use ACL redis secure model, described here: https://redis.io/docs/management/security/acl/

If redis secured use the following configuration options
```
REDIS_USE_AUTHENTICATION=true
REDIS_USERNAME=<User name related to valid ACL>
REDIS_PASSWORD=<User password related to valid ACL>
```

If no redis authentication used set REDIS_USE_AUTHENTICATION to false

### Configuration boundaries
Not known

## Custom logging
Custom logging available by substitution of /src/core/logger.py file. Use dictionary logging config feature (https://docs.python.org/3/library/logging.config.html)
