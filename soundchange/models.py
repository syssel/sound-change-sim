import os
import re
import random
import numpy as np

import logging

from multiprocessing import Pool
from functools import partial

from pyconll import iter_from_file

class RuleException(object):
    def __init__(self, source, p):
        self.source = source
        self.p = p

    @classmethod
    def from_string(s):
        raise ValueError("Not implemented")

    def __str__(self):
        return "(source:{} p:{})".format(self.source, self.p)

class Rule(object):
    def __init__(self, source, target):
        self.source = source
        self.target = target

    @classmethod
    def from_string(s):
        raise ValueError("Not implemented")
    
    def __str__(self):
        return "(source:{} target:{})".format(self.source, self.target)


class RuleBook(object):
    def __init__(self, rules, exceptions):
        self.rules = rules
        self.exceptions = exceptions
    
    def transform(self, word, base_prob):
        # Check if word is an exception, and update change probability
        word = word.lower()

        prob=base_prob

        for e in self.exceptions:
            if re.match(e.source, word):
                prob*=e.p
                break

        if prob==0: return word

        for rule in self.rules:
            pre_sub = word
            
            # Apply rule till no match is found
            while True:
                sub = re.sub(rule.source, rule.target, pre_sub)
                
                if sub == pre_sub: break
                pre_sub = sub

            
            # Realise change with probability <prob>, or leave word unchanged <1-prob>
            transformed = np.random.choice([sub, word], p=(prob, 1-prob))
            if word != sub: logging.info("|".join((word, sub, str(base_prob), str(prob), str(transformed!=word), transformed)))
            word = transformed

        return transformed


class Corpus(object):
    def __init__(self, dpath, indices=None):
        self.dpath = dpath
        self.indices = indices

        if not indices:
            self.indices = range(sum(1 for _ in iter_from_file(dpath)))
        
    def create_subcorpora(self, n, random_seed=None):
        random.seed(random_seed)
        shuffled = random.sample(self.indices, len(self.indices))

        sub_indices = (shuffled[i::n] for i in range(n))

        return [Corpus(self.dpath, indices)
                for n, indices in enumerate(sub_indices)]
    
    def append_tokens_to_file(self, tokenlist, dest, writer, transform=None):
        if transform:
            tokenlist = transform(tokenlist)

        with open(dest, "a") as f:
            f.write(writer(tokenlist))

    def write_to_file(self, dest, writer, transform=None):
        open(dest, 'w').close()
        with Pool(os.cpu_count()+2) as pool:

            sentences = (tokens for i, tokens in enumerate(iter_from_file(self.dpath))
                                if i in self.indices)

            logging.info("="*84)
            logging.info("File:{}".format(self.dpath))
            logging.info("Indices:{}".format(self.indices))
            logging.info("="*84)
            

            for tokens in pool.imap_unordered(
                            partial(self.append_tokens_to_file, dest=dest, writer=writer, transform=transform),
                            sentences):
                continue                            

    def __len__(self):
        return len(self.indices)