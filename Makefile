.PHONY: validate convert build-cv

validate:
	profilectl validate examples/resume.example.json

convert:
	profilectl convert examples/resume.example.json -o out.yaml

build-cv: validate convert