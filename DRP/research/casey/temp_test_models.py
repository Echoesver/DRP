import os
import sys
full_path = os.path.dirname(os.path.realpath(__file__)) + "/"
django_path = full_path[:full_path.rfind("/DRP/")]
if django_path not in sys.path:
    sys.path = [django_path] + sys.path
    os.environ['DJANGO_SETTINGS_MODULE'] = 'DRP.settings'


from DRP.research.casey.retrievalFunctions import get_data_from_ref_file
from DRP.retrievalFunctions import get_valid_data
from DRP.retrievalFunctions import filter_by_date
data = get_valid_data()
date_data = filter_by_date(data, "04-02-2014", "before")

filename = "DRP/research/casey/raw/033115_model.txt"

# Used to grab the data .
pre_filtered = get_data_from_ref_file(filename)
filtered = [entry for entry in pre_filtered
            if "V" in entry.atoms and ("Te" in entry.atoms or "Se" in entry.atoms)]

all_data = list(filtered) + list(date_data)


from DRP.preprocessors import default_preprocessor as preprocessor
from DRP.postprocessors import default_postprocessor as postprocessor
from DRP.model_building.rxn_calculator import headers

filtered_set, _ = postprocessor(
    {"test": preprocessor([headers] + filtered)[1:]}, headers)
all_set, _ = postprocessor(
    {"all": preprocessor([headers] + all_data)[1:]}, headers)


from DRP.models import ModelStats
model = ModelStats.objects.get(id=2674)
model._test_model(filtered_set["test"],
                  all_set["all"],
                  debug=True)

if not model.load_confusion_table(table="train"):
    model.train_confusion_table = model.confusion_table
    print "WARNING: Replaced empty train-table with test-table!"

model.summary()
print "Test size: {}".format(model.total(table="test"))

print "Done!"
