"""kr2nltk.py is part of hunparse. It uses the readkr module (written by Daniel Varga) to parse KR-codes and then transforms them into the format required by NLTK parsers."""
import sys
import readkr
import ConfigParser

class Kr2NltkConverter():
    def __init__(self, defaultsFile='krDefaults.txt'):
        self.defaultValues = ConfigParser.SafeConfigParser()
        self.defaultValues.read(defaultsFile)


    def node2nltk(self, node, top=False, src=None):
        name = node.value
        children = [self.node2nltk(snode) for snode in node.children]
        if src:
            children.append(src)       
        if self.defaultValues.has_section(name):
            children += self.getDefaults(children, name)
        if children == []:
            
            if top: return name
            childrenString = '1'
        else:
            childrenString = '['+', '.join(children)+']'
        if top:
            return name+childrenString
        else:
            return name+'='+childrenString

    def getDefaults(self, children, name):
        childAttributes = set([child.split('=')[0] for child in children])
        newChildren = ['{0}={1}'.format(attr.upper(), val)
                       for attr, val in self.defaultValues.items(name)
                       if attr.upper() not in childAttributes]
        return newChildren

    def getSrcString(self, derivString, nodeString):
        if nodeString == '':
            return 'SRC=[DERIV={0}]'.format(derivString)
        return 'SRC=[DERIV={0}, STEM={1}]'.format(derivString, nodeString)

    def kr2nltk(self, krString):
        if krString == '<NO_KR>': return 'UNKNOWN'
        kr = readkr.analyze('dummystem/'+krString)[0]
        nodes, derivations = kr.krNodes, kr.kepzos
        lastSrc='SRC=0'
        if derivations!=[]:
            lastSrc = self.getSrcString(self.node2nltk(derivations[0][0],
                      top=True), 
                      nodes[0].value)    
            
            for deriv, node in zip(derivations[1:], nodes[1:-1]):
                nodeString = self.node2nltk(node, top=True, src=lastSrc)
                derivString = self.node2nltk(deriv[0], top=True)
                lastSrc = self.getSrcString(derivString, nodeString)
        return self.node2nltk(nodes[-1], top=True, src=lastSrc)

    def kr2termRule(self, krString):
        code = self.kr2nltk(krString)
        code = code.replace('-', '_')
        if len(code)>0:
            return code+" -> '"+krString+"'"


def main():
    for line in sys.stdin:
        krString = line.strip()
        rule = kr2termRule(krString)
        if rule:
            print rule

if __name__=='__main__':
    main()
