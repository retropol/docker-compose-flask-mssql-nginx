FROM python:3.9

WORKDIR /flaskapp

# Install system dependencies
RUN apt-get update && apt-get install -y unixodbc-dev

RUN apt-get update \
    && apt-get install -y curl gnupg2 apt-transport-https
RUN apt-get install -y --no-install-recommends apt-utils

# apt-get and system utilities
RUN apt-get update && apt-get install -y \
	curl apt-transport-https debconf-utils gnupg2 


# Install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


COPY index.html /flaskapp/templates/index.html
#COPY js.js /flaskapp/templates/js.js
#COPY css.css /flaskapp/templates/css.css

COPY app.py /flaskapp/app.py

# Install Flask package
RUN pip install Flask
RUN pip install flask_sqlalchemy
# Install ODBC Driver
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18 mssql-tools18
RUN echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bashrc
RUN /bin/bash -c "source ~/.bashrc"
ENV MSSQL_CLI_TELEMETRY_OPTOUT=true


# Expose the container port

EXPOSE 5000

# Run the application
CMD ["python", "/flaskapp/app.py"]
