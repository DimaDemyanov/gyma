# VDV-Backend

## DOCKER
docker build -t vdvsrv -f Dockerfile .
docker run -d -e "PROFILE=dev" -e "BUILD_NUMBER=33" -p 80:4201 --name vdvsrv vdvsrv
