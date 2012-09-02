'''
Created on Sep 1, 2012

@author: adewinter
'''
from gene.Gene import Gene
from pprint import pformat
import logging
import uuid

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
    
    MAX_RUNS = 200

    def __init__(self, num_starting_candidates):
        '''
        Constructor
        '''
        #Customize file logging output to make it easier to put things together in splunk
        guid = uuid.uuid4()
        formatter = logging.Formatter('ID=' + str(guid) + ' - %(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh = logging.FileHandler('ga_trials.log')
        fh.setLevel(logging.INFO)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        
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
        
        #NOTE candidates are already sorted from best to worst score in main loop!
        pool_len = len(self.candidates)
        self.candidates = self.candidates[:pool_len/2]
        logger.debug('Pool culled to: %s (old length:%s)' % (pool_len/2, pool_len))
    
    def generate_new_pool(self):
        """
        """
        new_pool = []
        for idx in range(0, len(self.candidates),2): #skip one on every increment
            candidate = self.candidates[idx]
            if idx == len(self.candidates) - 1:
                next_candidate = candidate #for odd numbered pools, we have a little self-reproduction going on
            else:
                next_candidate = self.candidates[idx+1]
            child1, child2 = Gene.make_child_genes(candidate, next_candidate)
            child3, child4 = Gene.make_child_genes(candidate, next_candidate)
#            logger.debug('New Child1: %s' % child1.DNA)
#            logger.debug('New Child2: %s' % child2.DNA)
#            logger.debug('New Child3: %s' % child3.DNA)
#            logger.debug('New Child4: %s' % child4.DNA)
            new_pool.append(child1)
            new_pool.append(child2)
            new_pool.append(child3)
            new_pool.append(child4)
        return new_pool
    
    def run_rounds(self):
        logger.info('Running rounds')
        _run=0
        
        while True:
            for candidate in self.candidates:
                found_candidate = self.evaluate_candidate(candidate)
                if found_candidate:
                    break
            self.candidates.sort(key=lambda x: x.score, reverse=False)
            str_scores = ','.join(map(lambda x: str(x.score), self.candidates))
            logger.info('Run #%s, Score_Summary=%s' % (_run, str_scores))
            int_scores = map(lambda x: x.score, self.candidates)
            avg_score = sum(int_scores, 0.0) / len(int_scores)
            logger.info('Run #%s, Average_Score=%s' % (_run, avg_score))
            if found_candidate:
                logger.info('=======================================')
                logger.info('Summary of each candidate in this pool:')
                for candidate in self.candidates:
                    logger.info('%s' % candidate.__unicode__())
                logger.info('=================================')
                logger.info('Found a candidate! %s' % found_candidate)
                logger.info('Best candidate DNA is: %s' % ''.join(found_candidate.DNA))
                logger.info('=================================')
                return candidate #break the loop
            
            logger.debug('Culling')
            self.cull_bad_candidates()
            logger.debug('Generating new generation')
            self.candidates = self.generate_new_pool()
            if _run == self.MAX_RUNS:
                logger.info('MAXIMUM NUMBER OF ITERATIONS REACHED. EXITING')
                return
            _run = _run+1
            
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
        
        s1 = get_score(out1)
        s2 = get_score(out2)
        
        if out1 == out2 == None: # or out1 == out2 == 0:
            s1 = s1+50
            s2 = s2+50
        
        gene.score = s1 if s1 <= s2 else s2
        
        if gene.score == 0:
            return gene