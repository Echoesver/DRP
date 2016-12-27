"""An example molecular descriptor plugin to demonstrate the 'shape' that the API requires."""
from .utils import setup
import DRP
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

calculatorSoftware = 'example_plugin'

_descriptorDict = {
    'length': {'type': 'num', 'name': 'Length of smiles string', 'calculatorSoftware': calculatorSoftware, 'calculatorSoftwareVersion': '1_5', 'minimum': 1},
    'fs': {'type': 'ord', 'name': 'Fake size', 'calculatorSoftware': calculatorSoftware, 'calculatorSoftwareVersion': '1_5', 'maximum': 3, 'minimum': 1},
    'N?': {'type': 'bool', 'name': 'Has Nitrogen', 'calculatorSoftware': calculatorSoftware, 'calculatorSoftwareVersion': '0'},
    'arb': {'type': 'cat', 'name': "Phil's arbitrary descriptor", 'calculatorSoftware': calculatorSoftware, 'calculatorSoftwareVersion': '0', 'permittedValues': ('fun', 'dull')}
}
"""A dictionary describing the descriptors available in this module. The key should always be the heading for the descriptor."""

descriptorDict = setup(_descriptorDict)


def fsValueCalc(num):
    """Calculate an ordinal fake size value."""
    if num < 5:
        return 1
    elif num < 10:
        return 2
    else:
        return 3


def arbValCalc(compound):
    """Calculate a completely arbitrary value as an example of a categorical descriptor."""
    if compound.pk % 2 == 0:
        return DRP.models.CategoricalDescriptorPermittedValue.objects.get(value='dull', descriptor=descriptorDict['arb'])
    else:
        return DRP.models.CategoricalDescriptorPermittedValue.objects.get(value='fun', descriptor=descriptorDict['arb'])


def calculate_many(compound_set, verbose=False, whitelist=None):
    """Batch calculation."""
    for i, compound in enumerate(compound_set):
        if verbose:
            logger.info("{}; Compound {} ({}/{})".format(compound,
                                                         compound.pk, i + 1, len(compound_set)))
        calculate(compound, verbose=verbose, whitelist=whitelist)


def calculate(compound, verbose=False, whitelist=None):
    """
    Calculate the descriptors from this plugin for a compound.

    This should fail silently if a descriptor cannot be calculated for a compound, storing a None value in the
    database as this happens.
    """
    if compound.smiles:
        nValue = ('n' in compound.smiles or 'N' in compound.smiles)
        lengthValue = len(compound.smiles)
        fsValue = fsValueCalc(lengthValue)
    else:
        fsValue = None
        nValue = None
        lengthValue = None

    arbValue = arbValCalc(compound)

    heading = 'length'
    if whitelist is None or heading in whitelist:
        v = DRP.models.NumMolDescriptorValue.objects.update_or_create(
            defaults={'value': lengthValue}, compound=compound, descriptor=descriptorDict[heading])[0]
        try:
            v.full_clean()
        except ValidationError as e:
            logger.warning('Value {} for compound {} and descriptor {} failed validation. Value set to None. Validation error message: {}'.format(
                v.value, v.compound, v.descriptor, e.message))
            v.value = None
        v.save()

    heading = 'fs'
    if whitelist is None or heading in whitelist:
        v = DRP.models.OrdMolDescriptorValue.objects.update_or_create(
            defaults={'value': fsValue}, compound=compound, descriptor=descriptorDict[heading])[0]
        try:
            v.full_clean()
        except ValidationError as e:
            logger.warning('Value {} for compound {} and descriptor {} failed validation. Value set to None. Validation error message: {}'.format(
                v.value, v.compound, v.descriptor, e.message))
            v.value = None
        v.save()

    heading = 'N?'
    if whitelist is None or heading in whitelist:
        v = DRP.models.BoolMolDescriptorValue.objects.update_or_create(
            defaults={'value': nValue}, compound=compound, descriptor=descriptorDict[heading])[0]
        try:
            v.full_clean()
        except ValidationError as e:
            logger.warning('Value {} for compound {} and descriptor {} failed validation. Value set to None. Validation error message: {}'.format(
                v.value, v.compound, v.descriptor, e.message))
            v.value = None
        v.save()

    heading = 'arb'
    if whitelist is None or heading in whitelist:
        v = DRP.models.CatMolDescriptorValue.objects.update_or_create(
            defaults={'value': arbValue}, compound=compound, descriptor=descriptorDict[heading])[0]
        try:
            v.full_clean()
        except ValidationError as e:
            logger.warning('Value {} for compound {} and descriptor {} failed validation. Value set to None. Validation error message: {}'.format(
                v.value, v.compound, v.descriptor, e.message))
            v.value = None
        v.save()
