'''
Created on Sep 1, 2012

@author: adewinter
'''
from gene.Gene import Gene
from pprint import pformat
import logging

logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class GA_MUL(object):
    '''
    classdocs
    '''

    def __init__(self, num_starting_candidates):
        '''
        Constructor
        '''
        self.candidates = []
        #generate the initial number of candidates
        logger.info('Initiating Candidate Pool')
        for i in range(num_starting_candidates):
            g = Gene(full_random=True)
            logging.debug('Candidate DNA: %s' % g.DNA)
            self.candidates.append(g) #initially assign a score of -1
    
    def cull_bad_candidates(self):
        """
        Removes all but the top 50% scoring candidates
        """
        
    
    def run_rounds(self):
        logger.info('Running rounds')
#        while True:
        for candidate in self.candidates:
            self.evaluate_candidate(candidate)
            
        logger.debug('Here are the results from a pool run')
        a = pformat(self.candidates)
        logger.debug(a)
            
            
            
    def evaluate_candidate(self, gene):
        """
        Returns the score of the candidate
        
        Here we're trying to evaluate for closest to 3 * 7 (i.e. 21)
        Give points for multiples of 3 or 7 as well
        Closest to 0 score is best. You get zero if your output is 21 on either output 1 or output 2
        
        We pick the highest score between the two outputs
        """
        def get_score(output):
            if output == None:
                output = 0
            s = abs(21 - output)
            if output % 3 == 0:
                s = s/2
            if output % 7 == 0:
                s = s/2
            return s
        
        out1,out2 = gene.run(3,7)
        
        if out1 == 21 or out2 == 21:
            return 0,out1,out2 #you won the game
        
        s1 = get_score(out1)
        s2 = get_score(out2)
        
        if out1 == out2 == None: # or out1 == out2 == 0:
            s1 = s1+50
            s2 = s2+50
        
        gene.score = s1 if s1 <= s2 else s2
    