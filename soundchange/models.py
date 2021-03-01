import os
import re
import random
import numpy as np

from multiprocessing import Pool
from functools import partial

from pyconll import iter_from_file
from pyconll.unit.conll import Conll

class RuleException(object):
    def __init__(self, source, p):
        self.source = source
        self.p = p

    @classmethod
    def from_string(s):
        raise ValueError("Not implemented")


class Rule(object):
    def __init__(self, source, target):
        self.source = source
        self.target = target

    @classmethod
    def from_string(s):
        raise ValueError("Not implemented")


class RuleBook(object):
    def __init__(self, rules, exceptions):
        self.rules = rules
        self.exceptions = exceptions
    @profile
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

            import logging
            if word != sub: logging.info("|".join((word, sub, str(base_prob), str(prob))))
            
            # Realise change with probability <prob>, or leave word unchanged <1-prob>
            word = np.random.choice([sub, word], p=(prob, 1-prob))

        return word


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
    
    @profile
    def append_tokens_to_file(self, tokenlist, dest, transform=None):
        if transform:
            tokenlist = transform(tokenlist)

        with open(dest, "a") as f:
            f.write(tokenlist.conll()+"\n\n")

    @profile
    def write_to_file(self, dest, transform=None):
        open(dest, 'w').close()
        pool = Pool(os.cpu_count()+2)

        sentences = (tokens for i, tokens in enumerate(iter_from_file(self.dpath))
                            if i in self.indices)

        for tokens in pool.imap_unordered(
                        partial(self.append_tokens_to_file, dest=dest, transform=transform),
                        sentences):
            continue                            

    @profile
    def write_to_file_serial(self, dest, transform=None):
        open(dest, 'w').close()

        sentences = (tokens for i, tokens in enumerate(iter_from_file(self.dpath))
                            if i in self.indices)

        for tokens in sentences:
            self.append_tokens_to_file(tokens, dest, transform)

    def __len__(self):
        return len(self.indices)