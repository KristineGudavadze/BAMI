import numpy as np


def cosine_similarity(list1, list2):
    intersection = set(list1) & set(list2)
    numerator = len(intersection)
    denominator = np.sqrt(len(list1)) * np.sqrt(len(list2))
    return numerator / denominator if denominator != 0 else 0


def jaccard_similarity(list1, list2):
    intersection = set(list1) & set(list2)
    union = set(list1) | set(list2)
    return len(intersection) / len(union) if union != 0 else 0
