'''
Created on Sep 1, 2012

@author: adewinter
'''
import random

class Gene(object):
    '''
    classdocs
    '''
    #A list of functions that map to DNA characters
    DNA_LIST = {
        'A': add,
        'B': subtract,
        'C': remember
    }
    
    """ Max number of genes that can be used """
    DNA_SPACE_MAX_LEN = 200
    
    DNA = []
    
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

    def __init__(self, DNA=None, full_random=True, mutation_rate=0.1):
        '''
        Constructor
        '''
        self.mutation_rate = mutation_rate
        if full_random:
            self._configure_full_random()
            return
        else:
            if DNA:
                self.DNA = DNA
            else:
                raise Exception('You need to specify some DNA when trying to create a new Gene')
                
    
    @staticmethod
    def make_child_genes(parent1=None, parent2=None, mutation_rate=0.1):
        """
        Generates 2 new Genes.  Should specify at *least* one parent (will clone the parent
        if only one is specified), combine at random, throw in mutation as specified (or use default)
        Returns a TUPLE of the two genes!
        """
        return Gene._mutate_one_or_both(parent1, parent2, mutation_rate)
    
    @staticmethod
    def add (a, b):
        return a+b
    
    @staticmethod
    def subtract (a,b):
        return a-b
    
    global remember_holder
    @staticmethod
    def remember (a,b):
        """
        "Remembers" value 'a'.  Does nothing with 'b'.
        If !a, return remember_holder
        if a, set remember_holder = a and return a
        """
        if a:
            remember_holder = a
            return a
        else:
            return remember_holder
        
        
    def __len__(self):
        return len(self.DNA)