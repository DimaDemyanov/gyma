# VDV-Backend

## DOCKER
docker build -t vdvsrv -f Dockerfile .
docker run -d -e "PROFILE=dev" -e "BUILD_NUMBER=33" -p 80:4201 --name vdvsrv vdvsrv


nohup python3.6 ./server.py --profile dev >/dev/null 2>/dev/null &

pgrep -af python | grep dev | awk '{print $1;}'

kill $(pgrep -af python | grep dev | awk '{print $1;}')
curl http://185.185.40.39:4201/vdv/swagger-ui/