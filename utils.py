def is_partial_match(s1, s2, threshold=0.9):
    comp1 = s1.lower().split()
    comp2 = s2.lower().split()
    common_words = [word for word in comp1 if word in comp2]
    match_ratio = 0
    if comp1:
        match_ratio = len(common_words) / len(comp1)
    return match_ratio >= threshold
