import build_model
import parse_model_results
import argparse
import django
from DRP.models import DataSet, BoolRxnDescriptor, BoolRxnDescriptorValue, NumRxnDescriptor, NumRxnDescriptorValue, OrdRxnDescriptor, OrdRxnDescriptorValue, CatRxnDescriptor, CatRxnDescriptorValue
import uuid

from cStringIO import StringIO
import sys


# from
# http://stackoverflow.com/questions/16571150/how-to-capture-stdout-output-from-a-python-function-call
class Capturing(list):

    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        sys.stdout = self._stdout


def filter_reactions(reactions, response_header, verbose=False):
    # filter out reactions with undefined values for the response_descriptor
    initial_num = reactions.count()
    if BoolRxnDescriptor.objects.filter(heading=response_header).exists():
        reactions = reactions.exclude(boolrxndescriptorvalue__in=BoolRxnDescriptorValue.objects.filter(
            descriptor__heading=response_header, value=None))
        reactions = reactions.filter(boolrxndescriptorvalue__in=BoolRxnDescriptorValue.objects.filter(
            descriptor__heading=response_header))
    elif NumRxnDescriptor.objects.filter(heading=response_header).exists():
        reactions = reactions.exclude(numrxndescriptorvalue__in=NumRxnDescriptorValue.objects.filter(
            descriptor__heading=response_header, value=None))
        reactions = reactions.filter(numrxndescriptorvalue__in=NumRxnDescriptorValue.objects.filter(
            descriptor__heading=response_header))
    elif OrdRxnDescriptor.objects.filter(heading=response_header).exists():
        reactions = reactions.exclude(ordrxndescriptorvalue__in=OrdRxnDescriptorValue.objects.filter(
            descriptor__heading=response_header, value=None))
        reactions = reactions.filter(ordrxndescriptorvalue__in=OrdRxnDescriptorValue.objects.filter(
            descriptor__heading=response_header))
    elif CatRxnDescriptor.objects.filter(heading=response_header).exists():
        reactions = reactions.exclude(catrxndescriptorvalue__in=CatRxnDescriptorValue.objects.filter(
            descriptor__heading=response_header, value=None))
        reactions = reactions.filter(catrxndescriptorvalue__in=CatRxnDescriptorValue.objects.filter(
            descriptor__heading=response_header))
    else:
        raise ValueError("Descriptor header does not match any known type")

    if verbose:
        print "Filtered out {}/{} reactions with no value for {}".format(initial_num - reactions.count(), initial_num, response_header)

    return reactions


def build_many_models(predictor_headers=None, response_headers=None, modelVisitorLibrary=None, modelVisitorTool=None, splitter=None, training_set_name=None, test_set_name=None,
                      reaction_set_name=None, description="", verbose=False):

    results = [('header', 'BCR', 'ACC')]
    for response_header in response_headers:
        if training_set_name is not None:
            trainingSet = DataSet.objects.get(name=training_set_name)
            testSet = DataSet.objects.get(name=test_set_name)

            mod_training_set_name = '_'.join(
                [training_set_name, response_header, str(uuid.uuid4())])
            trainingSetRxns = filter_reactions(
                trainingSet.reactions.all(), response_header, verbose=verbose)
            DataSet.create(mod_training_set_name, trainingSetRxns)

            mod_test_set_name = '_'.join(
                [test_set_name, response_header, str(uuid.uuid4())])
            testSetRxns = filter_reactions(
                testSet.reactions.all(), response_header)
            DataSet.create(mod_test_set_name, testSetRxns)
        else:
            mod_training_set_name = None
            mod_test_set_name = None

        container = build_model.prepare_build_model(predictor_headers=predictor_headers, response_headers=[response_header], modelVisitorLibrary=modelVisitorLibrary, modelVisitorTool=modelVisitorTool,
                                                    splitter=splitter, training_set_name=mod_training_set_name, test_set_name=mod_test_set_name, reaction_set_name=reaction_set_name, description=description,
                                                    verbose=verbose)

        conf_mtrcs = container.getConfusionMatrices()

        _, overall_conf_mtrx = conf_mtrcs[0][0]
        ACC = build_model.accuracy(overall_conf_mtrx)
        BCR = build_model.BCR(overall_conf_mtrx)
        for model_mtrcs in conf_mtrcs:
            for descriptor_header, conf_mtrx in model_mtrcs:
                ACC = build_model.accuracy(conf_mtrx)
                BCR = build_model.BCR(conf_mtrx)
                print "Confusion matrix for {}:".format(descriptor_header)
                print build_model.confusionMatrixString(conf_mtrx)
                print "Accuracy: {:.3}".format(ACC)
                print "BCR: {:.3}".format(BCR)

        results.append((response_header, BCR, ACC))

    print '\n'.join(['\t'.join(map(str, res)) for res in results])


if __name__ == '__main__':
    django.setup()
    parser = argparse.ArgumentParser(description='Builds a model', fromfile_prefix_chars='@',
                                     epilog="Prefix arguments with '@' to specify a file containing newline"
                                     "-separated values for that argument. e.g.'-p @predictor_headers.txt'"
                                     " to pass multiple descriptors from a file as predictors")
    parser.add_argument('-p', '--predictor-headers', nargs='+',
                        help='One or more descriptors to use as predictors.', required=True)
    parser.add_argument('-r', '--response-headers', nargs='+', default=["boolean_crystallisation_outcome"],
                        help='One or more descriptors to predict. '
                        'Note that most models can only handle one response variable (default: %(default)s)')
    parser.add_argument('-ml', '--model-library', default="weka",
                        help='Model visitor library to use. (default: %(default)s)')
    parser.add_argument('-mt', '--model-tool', default="SVM_PUK_basic",
                        help='Model visitor tool from library to use. (default: %(default)s)')
    parser.add_argument('-s', '--splitter', default="KFoldSplitter",
                        help='Splitter to use. (default: %(default)s)')
    parser.add_argument('-v', dest='verbose', action='store_true',
                        help='Activate verbose mode.')
    parser.add_argument('-d', '--description', default="",
                        help='Description of model. (default: %(default)s)')
    parser.add_argument('-trs', '--training-set-name', default=None,
                        help='The name of the training set to use. (default: %(default)s)')
    parser.add_argument('-tes', '--test-set-name', default=None,
                        help='The name of the test set to use. (default: %(default)s)')
    # parser.add_argument('-rxn', '--reaction-set-name', default=None,
    # help='The name of the reactions to use as a whole dataset')
    args = parser.parse_args()

    build_many_models(predictor_headers=args.predictor_headers, response_headers=args.response_headers, modelVisitorLibrary=args.model_library, modelVisitorTool=args.model_tool,
                      splitter=args.splitter, training_set_name=args.training_set_name, test_set_name=args.test_set_name, description=args.description, verbose=args.verbose)
