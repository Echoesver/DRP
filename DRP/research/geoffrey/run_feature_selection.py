#!/usr/bin/env python

import django
from DRP.models import PerformedReaction, FeatureSelectionContainer, Descriptor, rxnDescriptorValues, DataSet
import argparse
import build_model
import ast


def prepare_build_model(predictor_headers=None, response_headers=None, featureVisitorLibrary=None, featureVisitorTool=None, training_set_name=None,
                        output_file=None, description="", visitor_options=None, verbose=False):
    """
    Do feature selection with the specified tools
    """

    predictors = Descriptor.objects.filter(heading__in=predictor_headers)
    responses = Descriptor.objects.filter(heading__in=response_headers)

    if predictors.count() != len(predictor_headers):
        raise KeyError("Could not find all predictors. Missing: {}".format(
            build_model.missing_descriptors(predictor_headers)))
    if responses.count() != len(response_headers):
        raise KeyError("Could not find all responses. Missing: {}".format(
            build_model.missing_descriptors(response_headers)))

    if verbose:
        print "Found {} matching predictors and {} matching responses".format(predictors.count(), responses.count())

    if training_set_name:
        trainingSet = DataSet.objects.get(name=training_set_name)
        reactions = None
    else:
        reactions = PerformedReaction.objects.filter(valid=True)
        reactions = reactions.exclude(ordrxndescriptorvalue__in=rxnDescriptorValues.OrdRxnDescriptorValue.objects.filter(
            descriptor__heading__in=response_headers, value=None))
        reactions = reactions.exclude(boolrxndescriptorvalue__in=rxnDescriptorValues.BoolRxnDescriptorValue.objects.filter(
            descriptor__heading__in=response_headers, value=None))
        reactions = reactions.exclude(catrxndescriptorvalue__in=rxnDescriptorValues.CatRxnDescriptorValue.objects.filter(
            descriptor__heading__in=response_headers, value=None))
        trainingSet = None
        testSet = None

    visitorOptions = ast.literal_eval(
        visitor_options) if visitor_options is not None else None
    container = FeatureSelectionContainer.create(featureVisitorLibrary, featureVisitorTool, predictors, responses, description=description, reactions=reactions,
                                                 trainingSet=trainingSet, featureVisitorOptions=visitorOptions)

    container.save()
    container.full_clean()
    container.build(verbose=verbose)
    container.save()
    container.full_clean()

    if output_file is not None:
        with open(output_file, 'wb') as f:
            f.write(
                '\n'.join([d.heading for d in container.chosenDescriptors]))

    return container


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
    parser.add_argument('-vl', '--feature-visitor-library', default="weka",
                        help='Feature visitor library to use. (default: %(default)s)')
    parser.add_argument('-vt', '--feature-visitor-tool', default="CFS",
                        help='Feature visitor tool from library to use. (default: %(default)s)')
    parser.add_argument('-v', dest='verbose', action='store_true',
                        help='Activate verbose mode.')
    parser.add_argument('-d', '--description', default="",
                        help='Description of model. (default: %(default)s)')
    parser.add_argument('-o', '--output-file', default=None,
                        help='Output file for descriptors.')
    parser.add_argument('-trs', '--training-set-name', default="",
                        help='The name of the training set to use. (default: %(default)s)')
    parser.add_argument('-vo', '--visitor-options', default=None,
                        help='Options for the feature visitor in JSON dictionary format')
    args = parser.parse_args()

    prepare_build_model(predictor_headers=args.predictor_headers, response_headers=args.response_headers, featureVisitorLibrary=args.feature_visitor_library, featureVisitorTool=args.feature_visitor_tool,
                        training_set_name=args.training_set_name, output_file=args.output_file, description=args.description, verbose=args.verbose, visitor_options=args.visitor_options)
