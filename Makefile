.PHONY: validate convert render-html html build-cv

IN ?= ../profile-data/data/resume.json
OUT ?= output/rendercv_CV.yaml
HTML_OUT ?= output/index.html

validate:
	profilectl validate --in "$(IN)"

convert:
	profilectl convert --input "$(IN)" --output "$(OUT)"

render-html:
	profilectl render-html "$(OUT)" --output "$(HTML_OUT)"

html: validate convert render-html

build-cv: html
