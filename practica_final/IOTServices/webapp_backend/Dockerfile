FROM python:3.7.3

COPY /app /etc/usr/src/app

WORKDIR /etc/usr/src/app

#Install any needed packages
RUN pip install Flask Flask-Cors requests

#Run python script when the container launches
ENTRYPOINT ["python"]
CMD ["webapp_backend_api_rest.py"]