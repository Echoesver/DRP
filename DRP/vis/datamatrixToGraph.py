import json
from kdtree import *
from datamatrix import *

# This will need to be modified to reflect current data (recommendations, etc.)


class graphNode:

    def __init__(self, name, friendlist, pagerank, myID, purity, outcome, inorg1, inorg2, org1):
        self.name = name
        self.friendlist = friendlist
        self.pagerank = pagerank
        self.id = myID
        self.purity = purity
        self.outcome = outcome
        self.inorg1 = inorg1
        self.inorg2 = inorg2
        self.org1 = org1
        self.inNodes = []

    def getNumOut(self):
        return len(self.friendlist)

    def isEqual(self, otherNode):
        if (otherNode.name == self.name and otherNode.id == self.id):
            return True
        else:
            return False


class myGraph:
    # Creates a graph from a datamatrix object as long as csv has: First col == id, Sec col == name of experiments; 3rd == inorg1
    # 4th col == inorg2, 5th col == org1, 6th(last) == purity; in between are
    # fully numeric, filled in columns;

    def __init__(self, datamatrix):
        idCol = -1
        namesCol = 0
        inorg1Col = 1
        inorg2Col = 4
        org1Col = 10
        purityCol = -2
        outcomeCol = -2

        edgeList = []

        valuesArrs = []
        names = []
        ids = []
        inorg1s = []
        inorg2s = []
        org1s = []
        outcomes = []
        purities = []
        for r in range(datamatrix.num_rows):
            names.append(datamatrix.dataset[r][namesCol])
            inorg1s.append(datamatrix.dataset[r][inorg1Col])
            inorg2s.append(datamatrix.dataset[r][inorg2Col])
            org1s.append(datamatrix.dataset[r][org1Col])
            outcomes.append(datamatrix.dataset[r][outcomeCol])
            purities.append(datamatrix.dataset[r][purityCol])
            ids.append(datamatrix.dataset[r][idCol])

        pointList = datamatrix.createPointList()
        tree = KDTree(pointList)
        for point in pointList:
            nnors = tree.findkNearestNeighbors(point, 5)
            # Because of the way index method works, will find only the first
            # match (ignoring repeated elements)--hopefully not an issue
            myFriendList = [pointList.index(neighbor) for neighbor in nnors]
            edgeList.append(myFriendList)
        datamatrix.dataset = np.transpose(datamatrix.dataset)
        # edgeList should be a list of lists (one list per point/row).
        self.names = names
        self.edgeList = edgeList
        self.ids = ids
        self.nodes = []
        self.numNodes = len(names)
        for i in range(0, self.numNodes):
            self.nodes.append(graphNode(self.names[i], self.edgeList[
                              i], 1.0 / self.numNodes, self.ids[i], purities[i], outcomes[i], inorg1s[i], inorg2s[i], org1s[i]))

    def findNode(self, name):
        for node in self.nodes:
            if node.name == name:
                return node
        return -1

    def findNodebyID(self, testid):
        for node in self.nodes:
            if node.id == testid:
                return node
        return -1

    # formats node correctly for d3?
    def createDictForVis(self):
        nodes = []  # TODO: This could be just self.nodes if we want ALL the data?
        for node in self.nodes:
            nodes.append({
                "ref": node.name,
                "id": node.id,
                "pagerank": node.pagerank,
                "purity": node.purity,
                "outcome": node.outcome,
                "inorg1": node.inorg1,
                "inorg2": node.inorg2,
                "org1": node.org1
            }
            )
        dids = []
        for i in xrange(len(nodes)):
            dids.append({"id": node.id})

        links = []
        for i in xrange(len(nodes)):
            for target in self.edgeList[i]:
                links.append({
                    "source": i,
                    "target": target,
                    "value": 1
                }
                )

        return {
            "nodes": nodes,
            "links": links,
            "dids": dids,
        }

    def writeJson(self):
        import os
        from django.conf import settings
        self.setPageRanks()
        final_dict = self.createDictForVis()
        #f = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'vis/matrix_formatted_for_vis'), "w")
        #dump = json.dump(final_dict, f, indent = 2)
        return final_dict

    def sortNodesByPR(self):
        return sorted(self.nodes, key=lambda node: node.pagerank, reverse=True)

    def setInNodes(self):
        for node in self.nodes:
            node.inNodes = self.getInNodes(node)

    def getInNodes(self, node):
        inNodes = []
        for testnode in self.nodes:
            for testid in testnode.friendlist:
                if (testid == node.id):
                    inNodes.append(testnode.id)
        return inNodes

    def numInNodes(self, node):
        return len(node.inNodes)

    def setPageRanks(self):
        self.setInNodes()
        counter = 0
        damping = 0.85
        converged = False  # converges when sum of differences < .001
        while (not converged):
            ranklist = []
            for node in self.nodes:
                PR = (1 - damping) / float(len(self.nodes))
                tsum = 0.0
                for friend in node.inNodes:
                    currNode = self.findNodebyID(friend)
                    if (currNode == -1):
                        print "goddamnit..."
                    if (self.numInNodes(currNode) == 0):
                        tsum += currNode.pagerank / (len(self.nodes) - 1.0)
                    else:
                        tsum += (currNode.pagerank + 0.0) / \
                            (currNode.getNumOut() + 0.0)

                PR += tsum * damping
                ranklist.append(PR)

            rankdiff = 0
            for i in range(0, len(self.nodes)):
                diff = float(self.nodes[i].pagerank) - float(ranklist[i])
                rankdiff += diff
            self.updatePageRanks(ranklist)
            if (rankdiff < .000001):
                converged = True
            counter += 1

    def updatePageRanks(self, ranklist):
        for i in range(0, len(ranklist)):
            self.nodes[i].pagerank = ranklist[i]

    def getSinks(self):
        sinks = []
        for node in self.nodes:
            if len(node.friendlist) == 0:
                sinks.append(node)
        return sinks
