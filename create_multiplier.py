'''
Created on Dec 2, 2012

@author: adewinter

App meant to create a generic multiplier of two numbers. Using home brewed Genetic Algorithm creator thing.
'''

from gene import *
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def evaluate_candidate(gene):
    """
    Returns the score of the candidate
    
    Here we're trying to evaluate for closest to 3 * 7 (i.e. 21)
    Give points for multiples of 3 or 7 as well
    Highest score is best. You get zero if your output is 21 on either output 1 or output 2
    
    We pick the highest score between the two outputs
    """
    def get_score(output):
        if output == None:
            output = 0
        s = 0;
        if output % 3 == 0:
            s += 1
        if output % 7 == 0:
            s += 1
        if output == 21:
            s += 1 
        return s
    
    out1,out2 = gene.run(3,7)
    
    s1 = get_score(out1)
    s2 = get_score(out2)
    
    if out1 == out2 == None: # or out1 == out2 == 0:
        s1 = 0
        s2 = 0
    
    gene.score = s1 if s1 <= s2 else s2
    
    return gene.score


def go():
    """
    Main init
    """
    ga = TestRunCoordinator(200)
    ga.MAX_RUNS = 200
    ga.evaluate_candidate = evaluate_candidate
    candidate = ga.run_rounds()
    if not candidate:
        print "###################"
        print "No candidate found!"
        print "###################"
    else:
        print "##############################"
        print "Succesfully found a candidate!"
        print "DNA: %s" % candidate
        print "##############################"


if __name__ == "__main__":
    go()