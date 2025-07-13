.PHONY: build-json validate-json build-wasm website-src website-demo

build-json: extractor/main.py
	cd extractor && uv run main.py

validate-json: build-json extractor/classification-schema.json
	cue vet -c extractor/classification-schema.json \
						 extractor/acm_classification_1998.json \
						 extractor/acm_classification_2012.json \
						 extractor/acm_msc_2010.json


build-wasm: build-json
	cd ./classif-finder-wasm && wasm-pack build --target web

website-src: build-wasm
	cp -r ./classif-finder-wasm/pkg ./website/


website-demo: website-src
	cd ./website && uv run python -m http.server 8000


