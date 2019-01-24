default:

reproduce-standardization:
	rm -rf data/standardized
	mkdir data/standardized
	nbexec notebooks/standardize

reproduce-analysis:
	rm -rf outputs
	mkdir outputs
	nbexec notebooks/analyze

data/standardized/nibrs-victims.csv.zip: data/standardized/nibrs-victims.csv
	rm -f $@
	cd data/standardized/; zip -r -s 50m nibrs-victims.csv.zip nibrs-victims.csv

data/standardized/reta-annual-counts.csv.zip: data/standardized/nibrs-victims.csv
	rm -f $@
	cd data/standardized/; zip -r -s 50m reta-annual-counts.csv.zip reta-annual-counts.csv

zipfiles: data/standardized/nibrs-victims.csv.zip data/standardized/reta-annual-counts.csv.zip
