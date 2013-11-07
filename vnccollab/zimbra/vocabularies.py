from vnccollab.common.vocabularies import SimpleVocabularyFactory \
    as SimpleVocabFact


ZIMBRA_STATUS_VOCAB = [
    ('NEED', 'Not initiated'),
    ('INPR', 'In process'),
    ('COMP', 'Complete'),
    ('WAITING', 'Waiting'),
    ('DEFERRED', 'Deferred')
]

ZIMBRA_PRIORITIES_VOCAB = [
    ('1', 'High'),
    ('5', 'Normal'),
    ('9', 'Low')
]

ZIMBRA_PERCENTAGE_VOCAB = [(str(x), str(x)+'%') for x in range(0, 100, 10)]

StatusZimbraTaskVocabulary = SimpleVocabFact(ZIMBRA_STATUS_VOCAB)
PrioritiesZimbraTaskVocabulary = SimpleVocabFact(ZIMBRA_PRIORITIES_VOCAB)
PercentageZimbraTaskVocabulary = SimpleVocabFact(ZIMBRA_PERCENTAGE_VOCAB)
