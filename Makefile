.PHONY: all build_image clean

all: build_image
	docker run --cap-add=SYS_ADMIN -it --rm -v ${PWD}/cache:/var/cache/mock -v ${PWD}:/build -v ${PWD}/result:/result netxms-rpm-builder
	docker image rm netxms-rpm-builder

build_image:
	docker build -t netxms-rpm-builder docker

clean:
	rm -f result/*
	docker image rm netxms-rpm-builder || true
