FROM python:3

WORKDIR /usr/src/app
RUN mkdir ./gyma

COPY Requirements.txt ./
RUN pip install --no-cache-dir -r Requirements.txt

COPY vdv/ ./gyma/vdv/
COPY swagger-ui/ ./gyma/swagger-ui/

COPY setup.py       ./setup.py
COPY server.py 		./gyma/server.py
COPY config.json 	./gyma/config.json
COPY swagger.json 	./gyma/swagger.json
COPY VERSION 		./gyma/VERSION
COPY startup.sh     ./gyma/startup.sh

RUN chmod 777 ./gyma/startup.sh && \
    sed -i 's/\r//' ./gyma/startup.sh

RUN pip install -e .

RUN mkdir -p ./gyma/logs
RUN chmod 777 ./gyma/logs
VOLUME ./gyma/logs

RUN mkdir -p ./gyma/images
RUN chmod 777 ./gyma/images
VOLUME ./gyma/images

EXPOSE 4201
 
CMD ["./gyma/startup.sh"]