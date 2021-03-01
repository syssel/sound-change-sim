from soundchange import Corpus, RuleBook, Rule, RuleException
from soundchange.utils import apply_sound_change

import os
from functools import partial

import logging; logging.basicConfig(filename='example.log', level=logging.INFO)

os.system("""git clone https://github.com/UniversalDependencies/UD_Danish-DDT.git data""")
corpus = Corpus("data/da_ddt-ud-train.conllu")#, range(0,100))
subcorpora = corpus.create_subcorpora(3, random_seed=42)

vowels = "[aeoieuæøå]"
source = "g"
target = "k"

rule_patterns = ((r"({V}){S}({V})", r"\1{T}\2"),
                 (r"({V}){S}te", r"\1{T}te"),
                 (r"({V}){S}$", r"\1{T}"),
                 (r"i{S}t$", r"i{T}t"))

rules = [Rule(s.format(V=vowels, S=source), t.format(T=target))
            for (s, t) in rule_patterns]

exception_patterns = ((r"^({W})$", ("og",), 0.2),)
exceptions = [RuleException(s.format(W="|".join(words)), p)
                for (s, words, p) in exception_patterns]

sound_changes = RuleBook(rules, exceptions)
change_rates = [0, 0.5, 1]

for i, (subcorpus, change_rate) in enumerate(zip(subcorpora, change_rates)):
    transform = partial(apply_sound_change, rb=sound_changes, p=change_rate)
    subcorpus.write_to_file("da_ddt-ud-train_{}.conll".format(i+1), 
                            transform=transform)







