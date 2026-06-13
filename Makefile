# OptimAI node operator toolkit
PREFIX ?= /usr/local

install:
	install -m 0755 monitor.sh $(PREFIX)/bin/optimai-monitor
	install -m 0755 fleet.sh  $(PREFIX)/bin/optimai-fleet
	install -m 0755 rewards.py  $(PREFIX)/bin/optimai-rewards
	install -m 0755 healthcheck.py $(PREFIX)/bin/optimai-healthcheck
	install -m 0644 systemd/optimai-monitor.service /etc/systemd/system/optimai-monitor.service
	systemctl daemon-reload
	@echo "installed; enable with: systemctl enable --now optimai-monitor"

rewards:
	optimai-rewards --csv rewards.csv --plot rewards.png

clean:
	rm -f rewards.csv rewards.png
