# Fyssion Media Server

This is the source code for my media/upload server.

This README isn't done and probably never will be.

## Installation

> Note: Python 3.7+ is required.

```sh
# Clone the repository from GitHub and enter the directory.
git clone https://github.com/Fyssion/FyssionMediaServer.git
cd FyssionMediaServer

# OPTIONAL: create a virtual env to house the requirements.
python3 -m venv venv

# Install the requirements.
python3 -m pip install -r requirements.txt

# Copy the example config
cp server/config/app.conf.example server/config/app.conf
# Edit the config to your liking.
# See the Configuration section below for more info.

# Note that you also may need to setup your chosen database.

# Run the server.
python3 -m server
```

## Configuration

### Config file options

> Note: none of these options are required.
However, it is still recommended that you take the time to configure the server properly.

|Option|Description|Default|
|------|-----------|-------|
|title|The title of the app.|Fyssion Media Server|
|host|The host/domain of the app.|localhost|
|port|The port to run the server on.|8080|
|debug|Whether to run the server in tornado's debug mode.|False|
|domain_override|Override the host:port combo with a domain.|None|
|url_length|Length of generated URLs for uploaded files.|4|
|ssl_enabled|Whether to enable ssl (https support).|False|
|ssl_override|Make the server return https urls in the API.|False|
|cookie_secret|The secure cookie secret.|uhyoushouldprobablysetthis|
|db_type|The type of database to use. See [database configuration](#database-configuration) for more info.|postgres|
|db_uri|The URI for your database. Only needed if your database needs it.|127.0.0.1|


### Database Configuration

Currently, the only database supported is postgresql.

To setup postgresql, use the following SQL statements in your database:
```sql
CREATE ROLE fyssionmediaserver WITH LOGIN PASSWORD 'whatever-you-want';
CREATE DATABASE fyssionmediaserver OWNER fyssionmediaserver;
```


### First Server Boot Configuration

On first boot, the server will create an Admin user with a pregenerated password.
The user's login details will be printed in the terminal.
You can login to this user to make other users and further configure the server.

The server will also create three roles: Admin, Trusted, and User.
The Admin role contains all the permissions enabled, and cannot be deleted or edited.
The Trusted role is able to upload, view, and manage files. It can also manage invites.
The User role is able to view and upload files. This is the default role can cannot be deleted.
You can create more roles to your liking.


