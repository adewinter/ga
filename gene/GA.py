'''
Created on Sep 1, 2012

@author: adewinter
'''
from gene.Gene import Gene
from pprint import pformat
import logging
import uuid
from spark import spark_string
import os

clear_console = 'clear' if os.name == 'posix' else 'CLS'

logger = logging.getLogger(__name__)
#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#handler = logging.StreamHandler()
#handler.setFormatter(formatter)
#foo = logger.handlers
##logger.addHandler(handler)
#logger.setLevel(logging.DEBUG)


class TestRunCoordinator(object):
    '''
    The TestRunCoordinator takes care of initializing a candidate pool, evaluating fitness, culling candidates and reproduction.
    '''
    
    MAX_RUNS = 200

    """A list of lists, showing top 5 scoring GENES of each round
    e.g.
    [ [<gene>,<gene>,...], [<gene>,<gene>,...] ]
    Shows the top 5 scoring genes for the first and second round runs of a trial.
    """
    top_five_scores = []
    
    """
    Average score per run
    """
    avg_scores = []
    
    """
    Top score from each run
    """
    top_scores = []
    
    """Useful Summary data about runs"""
    summary_data = None
        
    def __init__(self, num_starting_candidates):
        '''
        Constructor
        '''
        #Customize file logging output to make it easier to put things together in splunk
        guid = uuid.uuid4()
        formatter = logging.Formatter('ID=' + str(guid) + ',%(asctime)s [%(name)s][%(levelname)s] %(message)s')
        fh = logging.FileHandler('ga_trials.log')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        foo = logger.handlers
        
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
    
    def should_break(self, candidates, num_runs):
        """
        Decides if we should stop doing the round runs, because scores have stabilized or we've hit max runs.
        Updates Summary Data!
        Assumes Top Scores are already generated!
        """
        
        if num_runs >= self.MAX_RUNS:
            self.summary_data = "MAX_RUNS reached. Stopped."
            return True
        
        if candidates[0].score == 3:
            self.summary_data = "CANDIDATE WITH CORRECT SCORE FOUND! Gene: %s" % ''.join(candidates[0].DNA)
            return True
            
    def run_rounds(self):
        logger.info('Running rounds')
        _run=0
        
        
        while True:
            os.system(clear_console)
            logger.info('Evaluating Candidates.')
            ### YOU CAN OVERRIDE EVALUATE_CANDIDATE with your own Fitness Function
            
            raw_scores = map(self.evaluate_candidate, self.candidates)# Sort candidates by score.
            self.candidates.sort(key=lambda x: x.score, reverse=True)
            
            # Update Top Scorers tally
            self.top_five_scores.append(self.candidates[0:4]) #since we've already sorted.
            self.top_scores.append(self.candidates[0].score)
            
            #FOR DEBUG
#            str_scores = ','.join(map(lambda x: str(x.score), self.candidates))
#            logger.debug('Run #%s, Score_Summary=%s' % (_run, str_scores))
            avg_score = sum(raw_scores, 0.0) / len(raw_scores)
            self.avg_scores.append(avg_score)
            logger.info('Run #%s, Average_Score=%s' % (_run, avg_score))
            logger.info('Average scores over all last runs:: %s' % spark_string(self.avg_scores, True))
            logger.info('Top score over all last runs:: %s' % spark_string(self.top_scores, True))
            logger.info('Scores for this run:: %s' %spark_string(map(lambda x: x.score, self.candidates)))
         
            if self.should_break(self.candidates, _run):
                logger.info('=======================================')
                logger.info('Scores Stabilized.')
                logger.info('Summary Data: %s' % self.summary_data)
                logger.info('=======================================')
                logger.debug('Summary of each candidate in this pool:')
                for candidate in self.candidates:
                    logger.debug('%s' % candidate.__unicode__())
                logger.debug('=================================')
                logger.info('Top Five Candidates + scores %s' % self.top_five_scores[-1])
                logger.info('Best candidate DNA is: %s' % ''.join(self.top_five_scores[-1][0].DNA))
                logger.info('=================================')
                break
            
            logger.debug('Culling pool')
            self.cull_bad_candidates()
            logger.debug('Generating new generation')
            self.candidates = self.generate_new_pool()

            _run = _run+1
            
            
    def evaluate_candidate(self, gene):
        """
        Implement me based on what you're trying to do!
        Higher score is a more fit candidate!
        """
        raise NotImplementedError
