# Finding Similar Items: Textually Similar Documents

## implement the stages of finding textually similar documents based on Jaccard similarity using the shingling, minhashing, and locality-sensitive hashing (LSH) techniques and corresponding algorithms.

1. A class Shingling that constructs k–shingles of a given length k (e.g., 10) from a given document, computes a hash value for each unique shingle, and represents the document in the form of an ordered set of its hashed k-shingles.
2. A class CompareSets that computes the Jaccard similarity of two sets of integers – two sets of hashed shingles.
3. A class MinHashing that builds a minHash signature (in the form of a vector or a set) of a given length n from a given set of integers (a set of hashed shingles).
4. A class CompareSignatures that estimates similarity of two integer vectors – minhash signatures – as a fraction of components, in which they agree.
5. (Optional task for extra 2 bonus) A class LSH that implements the LSH technique: given a collection of minhash signatures (integer vectors) and a similarity threshold t, the LSH class (using banding and hashing) finds all candidate pairs of signatures that agree on at least fraction t of their components.

## How to run:

```
python3 lsh.py
```