.PHONY: all clean

all:
	docker run --cap-add=SYS_ADMIN -it --rm -v ${PWD}/cache:/var/cache/mock -v ${PWD}:/drone/src -v ${PWD}/result:/result ghcr.io/netxms/builder-rpm:latest

clean:
	rm -rf result/*
