FROM python:3.7.3
COPY /app /etc/usr/src/app
WORKDIR /etc/usr/src/app
# Install any needed packages specified in requirements.txt
# RUN pip install <packages>
# Run run.py when the container launches
RUN pip install paho-mqtt
RUN pip install requests
RUN pip install Flask Flask-Cors
#ENTRYPOINT ["python"]
CMD ["python", "message_router.py"]