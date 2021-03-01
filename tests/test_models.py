from soundchange.models import *

rs = 42
n = 9
corpus = Corpus("", range(0,10000))

class TestIndices:
    def test_random(self):
        subcorp = corpus.create_subcorpora(n)
        subcorp2 = corpus.create_subcorpora(n)

        get_indices = lambda x: getattr(x, "indices")
        
        assert list(map(get_indices, subcorp)) != list(map(get_indices, subcorp2))

    def test_random_seed(self):
        subcorp = corpus.create_subcorpora(n, rs)
        subcorp2 = corpus.create_subcorpora(n, rs)

        get_indices = lambda x: getattr(x, "indices")
        
        assert list(map(get_indices, subcorp)) == list(map(get_indices, subcorp2))



    
