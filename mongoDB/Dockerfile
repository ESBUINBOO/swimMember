FROM mongo:3.6.2-jessie
COPY scripts /home/mongodb/scripts
COPY mongod.conf /home/mongodb
WORKDIR /home/mongodb
RUN ["chmod", "-R", "+x", "/home/mongodb/scripts/"]
CMD ["/home/mongodb/scripts/run.sh"]