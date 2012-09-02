'''
Created on Sep 1, 2012

@author: adewinter
'''
import random
import logging


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
#logger.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
logger.setLevel(logging.INFO)

class Gene(object):
    '''
    classdocs
    '''
    class DIRECTION(object):
        LEFT=1
        RIGHT=2
        BOTH=3

    
    """ Max number of genes that can be used """
    DNA_SPACE_MAX_LEN = 200
    def __unicode__(self):
        return "Gene -- Score: %s, Output1: %s, Output2: %s" % (self.score, self.output1, self.output2)
    
    def __repr__(self):
        return self.__unicode__()
    
    def __str__(self):
#        return "foo"
        return self.__unicode__()
    def __init__(self, DNA=None, full_random=True, mutation_rate=0.1):
        '''
        Constructor
        '''
        self.mutation_rate = mutation_rate
        self.memory_holder = {}
        self.DNA = []
        #A list of functions that map to DNA characters
        self.DNA_LIST = {}
        self.score = -1
        self.output1 = None
        self.output2 = None
        #Figure out DNA components
        #This bit generates the mapping of "genes" (e.g. 'a' or 'C') to methods that do things.
        dna_methods = []
        for k in Gene.__dict__.keys():
            if k.startswith('D__'):
                dna_methods.append(Gene.__dict__.get(k))
        dna_char = '0'
        for method in dna_methods:
            self.DNA_LIST[dna_char] = method
            dna_char = chr(ord(dna_char) + 1)
            
        #Spawn a Random DNA strand
        if full_random:
            self._configure_full_random()
            return
        else:
            if DNA:
                self.DNA = DNA
            else:
                raise Exception('You need to specify some DNA when trying to create a new Gene')
                
    @staticmethod
    def _mutate_DNA(DNA,mutation_rate):
        """
        Does the actual mutation.
        uses mutation_rate as a probability (normal distribution) of a mutation happeing.
        A mutation is where one of the following ops is decided and called:
        adding a gene, deleting a gene, 'flipping' a gene
        """
        
        def ADD_GENE(g):
            """
            Pick a random gene and return it as a list
            """
            return [g, random.choice(Gene.DNA_LIST.keys())]
        
        def DEL_GENE(g):
            return []
        
        def FLIP_GENE(g):
            return [random.choice(Gene.DNA_LIST.keys())]
        
        _OPS = [ADD_GENE,DEL_GENE,FLIP_GENE]
        new_DNA = []
        for k,i in enumerate(DNA):
            if random.random() < mutation_rate:
                #we have to mutate!
                mute = random.choice(_OPS)(i)
                
            else:
                #no mutation here!
                mute = [i]
                
            new_DNA = new_DNA + mute
            
        return new_DNA
    
    @staticmethod
    def _create_dna(parent1,parent2,mutation_rate):
        if (bool(parent1) == bool(parent2)) and bool(parent1) == False:
            raise Exception('Need to specify at least one parent gene set!')
        
        if parent1 and not parent2:
            parent2 = parent1
        elif parent2 and not parent1:
            parent1 = parent2
            
        #Ok, we have both parent slots 'filled'
        
        #find the shortest parent
        shortest = parent1 if len(parent1) <= len(parent2) else parent2
        
        #pick a random join point along shortest dna
        join_index = random.randint(0,len(shortest))
        
        #slice and dice
        DNA1A = parent1.DNA[:join_index]
        DNA1B = parent1.DNA[join_index:]
        
        DNA2A = parent2.DNA[:join_index]
        DNA2B = parent2.DNA[join_index:]
        
        #now recombine
        DNAC1 = DNA1A + DNA2B
        DNAC2 = DNA2A + DNA1B
        
        DNAC1 = Gene._mutate_DNA(DNAC1,mutation_rate)
        DNAC2 = Gene._mutate_DNA(DNAC2,mutation_rate)
        
        return (Gene(DNA=DNAC1, mutation_rate=mutation_rate), Gene(DNA=DNAC2, mutation_rate=mutation_rate))
        
    def _configure_full_random(self):
        DNA_LEN = random.randint(1,self.DNA_SPACE_MAX_LEN)
        for i in range(DNA_LEN):
            self.DNA.append(random.choice(self.DNA_LIST.keys()))

    def run(self,input1, input2):
        """
        The meat of the algo: Use the genes to process the inputs
        """
        logger.debug('inputs', input1, input2)
        tres1 = input1
        tres2 = input2
        for gene in self.DNA:
            dmeth = self.DNA_LIST[gene]
            logger.debug('Dmeth is: %s' % dmeth)
            logger.debug('tres1, tres2::', tres1, tres2)
            (tres1, tres2) = self.DNA_LIST[gene](self,tres1, tres2)
        self.output1 = tres1
        self.output2 = tres2
        return (self.output1, self.output2)
        
    @staticmethod
    def make_child_genes(parent1=None, parent2=None, mutation_rate=0.1):
        """
        Generates 2 new Genes.  Should specify at *least* one parent (will clone the parent
        if only one is specified), combine at random, throw in mutation as specified (or use default)
        Returns a TUPLE of the two genes!
        """
        return Gene._mutate_one_or_both(parent1, parent2, mutation_rate)
    
    def add (self, a, b):
        if a==None:
            a=0
        if b==None:
            b=0
        return a+b
    
    def D__ADD_LEFT (self,a,b):
        return (self.add(a,b), b)
    
    def D__ADD_RIGHT (self, a, b):
        return (a, self.add(a,b))
    
    def subtract (self, a, b):
        if a==None:
            a=0
        if b==None:
            b=0
        return a-b
    
    def D__SUBTRACT_LEFT(self, a, b):
        return (self.subtract(a,b), b)
    
    def D__SUBTRACT_RIGHT(self, a, b):
        return (a, self.subtract(a,b))
    
    def D__EQUALIZE_LEFT(self, a, b):
        return (a, a)
    
    def D__EQUALIZE_RIGHT(self, a, b):
        return (b, b)
    
    def D__AVERAGE_LEFT(self, a, b):
        if a==None:
            a=0
        if b==None:
            b=0
        return ((a+b)/2, b)
    
    def D__AVERAGE_RIGHT(self, a, b):
        if a==None:
            a=0
        if b==None:
            b=0
        return (a, (a+b)/2)
    
    def remember_recall(self, idx, a=None):
        """
        "Remembers" value 'a' and places it at location idx
        "Recalls" when only idx is specified or returns None
        """
        if not a:
            return self.memory_holder.get(idx)
        else:
            self.memory_holder[idx] = a
        
    def D__REMEMEBER_RECALL_RIGHT(self, a, b):
        return (a, self.remember_recall(a, b))
    
    def D__REMEMBER_RECALL_LEFT(self, a, b):
        return (self.remember_recall(a, b), b)
    
    def D__REV_REMEMEBER_RECALL_RIGHT(self, a, b):
        return (a, self.remember_recall(b, a))
    
    def D__REV_REMEMBER_RECALL_LEFT(self, a, b):
        return (self.remember_recall(b, a), b)
    

    def __len__(self):
        return len(self.DNA)