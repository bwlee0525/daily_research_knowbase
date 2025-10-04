.PHONY: bootstrap dev run build sample local-archive

bootstrap:
	python -m pip install -U pip
	pip install -r backend/requirements.txt

dev:
	uvicorn backend.app:app --host 0.0.0.0 --port 8080 --reload

run:
	python -m backend.app

build:
	docker build -t research-pipeline:dev -f backend/Dockerfile .

sample:
	python -c "from backend.app import create_report; from backend.models import ReportRequest as RR; print(create_report(RR(topic='sample report', tags=['demo'])))"

local-archive:
	mkdir -p out
	python -c "from backend.app import rebuild_archive; print(rebuild_archive())"

clean:
	rm -rf out
