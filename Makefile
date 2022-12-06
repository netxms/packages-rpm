.PHONY: all build_image clean

IMAGE_REVISION = $(shell git rev-parse --short HEAD)

all: build
	docker run --cap-add=SYS_ADMIN -it --rm -v ${PWD}/cache:/var/cache/mock -v ${PWD}:/build -v ${PWD}/dist:/dist ghcr.io/netxms/rpm-builder:$(IMAGE_REVISION)

build:
	docker build -t ghcr.io/netxms/rpm-builder:$(IMAGE_REVISION) docker

push:
	docker tag ghcr.io/netxms/rpm-builder:$(IMAGE_REVISION) ghcr.io/netxms/rpm-builder:latest
	docker push ghcr.io/netxms/rpm-builder:$(IMAGE_REVISION)
	docker push ghcr.io/netxms/rpm-builder:latest

clean:
	rm -rf dist/*
	docker rmi -f ghcr.io/netxms/rpm-builder:$(IMAGE_REVISION)
	docker rmi -f ghcr.io/netxms/rpm-builder:latest
