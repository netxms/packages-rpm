.PHONY: all dist clean el8 el9 el10 fc43 fc44

TOPDIR := $(PWD)
DOCKER := docker run --rm -v $(TOPDIR):/drone/src -w /drone/src

DISTS := el8 el9 el10 fc43 fc44

IMAGE_el8  := ghcr.io/netxms/builder-rpm:epel8
IMAGE_el9  := ghcr.io/netxms/builder-rpm:epel9
IMAGE_el10 := ghcr.io/netxms/builder-rpm:epel10
IMAGE_fc43 := ghcr.io/netxms/builder-rpm:fedora43
IMAGE_fc44 := ghcr.io/netxms/builder-rpm:fedora44

all: dist $(DISTS)

dist:
	@mkdir -p SOURCES
	@V=$$(fgrep "Version:" SPECS/netxms.spec | cut -d: -f2 | tr -d "[:space:]"); \
	[ -n "$$V" ] || { echo "Cannot detect release, check spec file"; exit 1; }; \
	$(DOCKER) -v $(TOPDIR)/SOURCES:/dist ghcr.io/alkk/netxms-make-dist:latest release-$$V

define build_rule
$(1):
	mkdir -p cache/$(1)
	$$(DOCKER) -v $$(TOPDIR)/cache/$(1):/m2-repo $$(IMAGE_$(1)) sh -c '\
		dnf builddep -y SPECS/netxms.spec && \
		mkdir -p BUILD-$(1) && \
		rpmbuild --define "_topdir $$$$(pwd)" --define "_builddir $$$$(pwd)/BUILD-$(1)" -ba SPECS/netxms.spec && \
		rm -rf BUILD-$(1)'
endef

$(foreach d,$(DISTS),$(eval $(call build_rule,$(d))))

clean:
	rm -rf result/* BUILD-* RPMS SRPMS
