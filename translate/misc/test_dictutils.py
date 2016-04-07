from translate.misc import dictutils


def test_cidict_has_key():
    cid = dictutils.cidict()
    cid['lower'] = 'lowercase'
    assert 'lower' in cid
    assert 'Lower' in cid
    assert 'LOWER' in cid
    assert 'upper' not in cid
