from AbstractSplitter import AbstractSplitter
import random


class Splitter(AbstractSplitter):

    def __init__(self, namingStub, test_percent=0.33, num_splits=1):
        super(Splitter, self).__init__(namingStub)
        self.test_percent = test_percent
        self.num_splits = num_splits

    def split(self, reactions, verbose=False):
        super(Splitter, self).split(reactions, verbose=verbose)
        splits = [self._single_split(reactions, verbose) for i in xrange(self.num_splits)]
        return splits

    def _single_split(self, reactions, verbose=False):
        num_rxns = reactions.count()
        test_size = int(self.test_percent * num_rxns)

        # Split the reactions' IDs into two randomly-organized buckets.
        rxn_ids = [reaction.id for reaction in reactions]
        random.shuffle(rxn_ids)

        test = reactions.filter(id__in=rxn_ids[:test_size])
        train = reactions.filter(id__in=rxn_ids[test_size:])

        if verbose:
            print "Split into train ({}), test ({})".format(train.count(), test.count())

        return (self.package(train), self.package(test))
