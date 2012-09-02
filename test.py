'''
Created on Sep 1, 2012

@author: adewinter
'''
from gene.Gene import Gene
from gene.GA import GA_MUL
import pprint
if __name__ == '__main__':
#    ga = GA_MUL(200)
#    ga.run_rounds()

    g = Gene(DNA=list('3140475359578:03:9573595297628:4:543990;1478624304838:008:6:88:00575030'), full_random=False)
    g.run(3,7)
    
