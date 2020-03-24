"""
    All the explanation of the labels are established as per the
    Stanford Dependencies documentation on:
    https://nlp.stanford.edu/software/dependencies_manual.pdf

    The labels were all mapped to the Universal Dependencies format
    as per table 2 of the documentation on:
    https://nlp.stanford.edu/pubs/USD_LREC14_paper_camera_ready.pdf
"""

SPEC_SPLIT = ":"

# A nominal subject is a noun phrase which is the syntactic subject of a clause
NSUBJ = "nsubj"
# A clausal subject is a clausal syntactic subject of a clause, i.e., the subject is itself a clause
CSUBJ = "csubj"
# The direct object of a VP is the noun phrase which is the (accusative) object of the verb
DOBJ = "dobj"
# A passive nominal subject is a noun phrase which is the syntactic subject of a passive clause
NSUBJPASS = "nsubjpass"
# A clausal passive subject is a clausal syntactic subject of a passive clause
CSUBJPASS = "csubjpass"
# An agent is the complement of a passive verb which is introduced by the preposition "by"
AGENT = "agent"
# A relative clause modifier of an NP is a relative clause modifying the NP
RCMOD = "relcl"
# A copula is the relation between the complement of a copular verb and the copular verb.
COP = "cop"
# A conjunct is the relation between two elements connected by a coordinating conjunction, such as "and", "or", etc.
CONJ = "conj"
# A prepositional modifier of a verb, adjective, or noun is any prepositional phrase that serves to modify the meaning of the verb, adjective, noun, or even another prepositon.
PREP = "case"
# An open clausal complement (xcomp) of a verb or an adjective is a predicative or clausal complement without its own subject.
XCOMP = "xcomp"
# A dependency is labeled as dep when the system is unable to determine a more precise dependency relation between two words.
DEP = "dep"
# A noun compound modifier of an NP is any noun that serves to modify the head noun.
NN = "compound"
AUX = "aux"
AUXPASS = "auxpass"
ADVMOD = "advmod"
ACOMP = "xcomp"
NEG = "neg"
PRT = "prt"
PREPC = "prepc"
ADJP = "adjp"
POSS = "poss"
DET = "det"
INFMOD = "nfincl"
PARTMOD = "nfincl"
NUM = "nummod"
AMOD = "amod"
NNAFTER = "nnafter"
CCOMP = "ccomp"
COMPLM = "mark"
PUNCT = "punct"
MARK = "mark"


"""
    TO-DO: write description
"""

ROOT = "ROOT"
NP = "NP"
VP = "VP"
S = "S"
SBAR = "SBAR"
SINV = "SINV"
PRN = "PRN"
PP = "PP"
ADVP = "ADVP"
CD = "CD"
IOBJ = "IOBJ"

"""
    TO-DO: write description
"""

f_realActorPPIndicators = []
f_sequenceIndicators = []
f_relativeResolutionTags = []
f_relativeResolutionWords = []
f_conditionIndicators = []
f_exampleIndicators = []
f_parallelIndicators = []

"""
    Conjunctions
    TO-DO: write description
"""

IF = "if"
OF = "of"
THAT = "that"
OR = "or"
AND = "and"
ANDOR = "and/or"
BUT = "but"
TO = "to"
NO = "no"
FOR = "for"
ABOUT = "about"
MIXED = "mixed"
WHILE = "while"
WHEREAS = "whereas"
OTHERWISE = "otherwise"
EXCEPT = "except"
IFCOMPLM = "if-complm"
THEN = "then"
ALSO = "also"

"""
    TO-DO: write description
"""

ANIMATE = "ANIMATE"
INANIMATE = "INANIMATE"
BOTH = "BOTH"

"""
    Flow type
    TO-DO: write description
"""

JUMP = "JUMP"
MULTIPLE_CHOICE = "MULTIPLE_CHOICE"
CHOICE = "CHOICE"
CONCURRENCY = "CONCURRENCY"
EXCEPTION = "EXCEPTION"
SEQUENCE = "SEQUENCE"

"""
    Conjunction status
    TO-DO: write description
"""

NOT_CONTAINED = "NOT_CONTAINED"
ACTION = "ACTION"
ACTOR_SUBJECT = "ACTOR_SUBJECT"
ACTOR_OBJECT = "ACTOR_OBJECT"
RESOURCE = "RESOURCE"

"""
    Link types
    TO-DO: write description
"""

FORWARD = "FORWARD"
JUMP = "JUMP"
LOOP = "LOOP"
NONE = "NONE"

"""
    Phrase types
    TO-DO: write description
"""

CORE = "CORE"
PERIPHERAL = "PERIPHERAL"
EXTRA_THEMATIC = "EXTRA_THEMATIC"
GENITIVE = "GENITIVE"
UNKNOWN = "UNKNOWN"

"""
    Flow direction
    TODO: write description
"""

SPLIT = "SPLIT"
JOIN = "JOIN"

"""
    TODO: write description
"""

SUBJECT_ROLE_SCORE = 10
OBJECT_ROLE_SCORE = 10
ROLE_MATCH_SCORE = 20
SENTENCE_DISTANCE_PENALTY = 15
