import django
django.setup()
from DRP.models import PerformedReaction, DataSet, Descriptor, Compound, Reaction, CompoundQuantity, NumRxnDescriptorValue, CatMolDescriptorValue, OrdMolDescriptorValue, BoolMolDescriptorValue, NumMolDescriptorValue, CatMolDescriptor, OrdMolDescriptor, BoolMolDescriptor, NumMolDescriptor, BoolRxnDescriptorValue
import argparse


def dump_csv(file_name, descriptor_headers, reaction_set_name=None):
    if reaction_set_name is None:
        rxns = PerformedReaction.objects.all()
    else:
        rxns = DataSet.objects.get(name=reaction_set_name).reactions.all()

    descriptors = Descriptor.objects.filter(heading__in=descriptor_headers)

    if descriptors.count() != len(descriptor_headers):
        raise KeyError("Could not find all descriptors")

    whitelist = [d.csvHeader for d in descriptors]

    whitelist += ['id', 'notes', 'labGroup', 'user', 'performedBy', 'reference', 'valid', 'compound_0', 'compound_0_role', 'compound_0_amount', 'compound_1', 'compound_1_role',
                  'compound_1_amount', 'compound_2', 'compound_2_role', 'compound_2_amount', 'compound_3', 'compound_3_role', 'compound_3_amount', 'compound_4', 'compound_4_role', 'compound_4_amount']

    with open(file_name, 'wb') as f:
        rxns.toCsv(f, whitelistHeaders=whitelist, expanded=True)

if __name__ == '__main__':
    django.setup()
    parser = argparse.ArgumentParser(description='Dumps reactions to csv', fromfile_prefix_chars='@',
                                     epilog="Prefix arguments with '@' to specify a file containing newline"
                                     "-separated values for that argument. e.g.'-p @predictor_headers.txt'"
                                     " to pass multiple descriptors from a file as predictors")
    parser.add_argument('-f', '--file-name',
                        help='Name of file to dump to.', required=True)
    parser.add_argument('-d', '--descriptor-headers', nargs='+',
                        help='One or more descriptors to use as predictors.', required=True)
    parser.add_argument('-rxn', '--reaction-set-name', default=None,
                        help='The name of the reactions to use as a whole dataset')
    args = parser.parse_args()

    dump_csv(args.file_name, args.descriptor_headers, args.reaction_set_name)
