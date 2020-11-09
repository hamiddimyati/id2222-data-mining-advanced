import numpy as np
import pandas as pd
from nltk import ngrams
import glob
import time
from itertools import combinations

np.random.seed(0)

def jaccard_similarity(list1, list2):
    intersection = len(list(set(list1).intersection(list2)))
    union = (len(list1) + len(list2)) - intersection
    return float(intersection) / union


class shingling:

    def __init__(self, docs, k):
        self.docs = docs
        self.k = k
        self.characteristic_matrix = None

    def fit_transform(self):
        list_hashed = []
        for i in range(nrow):
            tokens = self.docs[i].split()
            list_hashed.append([hash(shingle) for shingle in ngrams(tokens, self.k)])

        # Create characteristic matrix
        global_hash = list(set(per_hash for per_doc in list_hashed for per_hash in per_doc))
        self.characteristic_matrix = {}
        for i in range(len(list_hashed)):
            binary_list = [ 1 if single_hash in list_hashed[i] else 0 for single_hash in global_hash ]
            self.characteristic_matrix['Doc'+str(i)] = binary_list
        self.characteristic_matrix = pd.DataFrame(self.characteristic_matrix, index=global_hash).reset_index(drop=True)
        
        # Calculate Jaccard similarity for each document
        jac_sim = pd.DataFrame(columns=['Doc1', 'Doc2', 'Jaccard_Score'])
        for i in range(nrow):
            for j in range(nrow):
                if i != j:
                    jac_score = jaccard_similarity(list_hashed[i], list_hashed[j])
                    jac_sim = jac_sim.append({'Doc1': 'Doc'+str(i), 'Doc2': 'Doc'+str(j), 'Jaccard_Score': jac_score}, ignore_index=True)
        
        return jac_sim

class minhashing:

    def __init__(self, characteristic_matrix, k_signature):
        self.characteristic_matrix = characteristic_matrix
        self.k_signature = k_signature
        self.signature_matrix = None

    def fit_transform(self):
        nrow_matrix = self.characteristic_matrix.shape[0]
        prime = nrow_matrix + 1
        coef_a = np.random.choice(nrow_matrix, size=self.k_signature, replace=False)
        coef_b = np.random.choice(nrow_matrix, size=self.k_signature, replace=False)

        cols0 = ['Hash'+str(j) for j in range(self.k_signature)]
        permutation_matrix = pd.DataFrame(columns=cols0)
        for i in range(nrow_matrix):
            dict_hash = {}
            for j in range(self.k_signature):
                dict_hash['Hash'+str(j)] = ( coef_a[j] * i + coef_b[j] ) % prime
            permutation_matrix = permutation_matrix.append(dict_hash, ignore_index=True)

        cols1 = ['Doc'+str(j) for j in range(nrow)]
        self.signature_matrix = pd.DataFrame(columns=cols1)
        for i in range(self.k_signature):
            dict_doc = {}
            idx = list(permutation_matrix[['Hash'+str(i)]].values.ravel())
            for j in range(nrow):
                dict_doc['Doc'+str(j)] = np.where(self.characteristic_matrix.reindex(idx)[['Doc'+str(j)]] == 1)[0].min()
            self.signature_matrix = self.signature_matrix.append(dict_doc, ignore_index=True)

        sign_sim = pd.DataFrame(columns=['Doc1', 'Doc2', 'Signature_Score'])
        for i in range(nrow):
            for j in range(nrow):
                if i != j:
                    sign_score = self.signature_matrix.loc[:,'Doc'+str(i)].eq(self.signature_matrix.loc[:,'Doc'+str(j)]).sum()/self.k_signature
                    sign_sim = sign_sim.append({'Doc1': 'Doc'+str(i), 'Doc2': 'Doc'+str(j), 'Signature_Score': sign_score}, ignore_index=True)
        
        return sign_sim

class lsh:

    def __init__(self, signature_matrix, bands, rows, threshold):
        self.signature_matrix = signature_matrix
        self.bands = bands
        self.rows = rows
        self.threshold = threshold

    def fit_transform(self):
        num_cols = self.signature_matrix.shape[1]
        candidates = set()

        for i in range(self.bands):
            for j in list(combinations(range(num_cols), 2)):
                col1 = self.signature_matrix.iloc[i * self.rows : (i + 1) * self.rows, j[0]]
                col2 = self.signature_matrix.iloc[i * self.rows : (i + 1) * self.rows, j[1]]
                sims = col1.eq(col2).sum()/self.rows
                if sims >= self.threshold:
                    candidates.add((j[0], j[1]))

        return candidates

if __name__ == "__main__":
    start_time = time.time()
    corpus = []

    file_list = glob.glob("data/corpus-20090418/*.txt")
    for file_path in file_list:
        with open(file_path, encoding="utf8", errors='ignore') as file_input:
            doc = file_input.read()
            doc = doc.replace('\n', ' ')
            doc = doc.replace('  ', ' ')
            corpus.append(doc)
    print("Load data success! in {} secs".format(round(time.time() - start_time, 2)))
    
    nrow = len(corpus)

    start_time = time.time()
    docs_shingling = shingling(corpus, 3)
    jaccard_similarity = docs_shingling.fit_transform()
    print("Shingling success! in {} secs".format(round(time.time() - start_time, 2)))

    start_time = time.time()
    docs_minhashing = minhashing(docs_shingling.characteristic_matrix, 9)
    signature_similarity = docs_minhashing.fit_transform()
    print("MinHashing success! in {} secs".format(round(time.time() - start_time, 2)))

    most_similar = pd.merge(jaccard_similarity, signature_similarity, on=['Doc1','Doc2']).sort_values(by='Signature_Score', ascending=False).reset_index(drop=True).loc[0]

    doc1 = int("".join(filter(str.isdigit, most_similar['Doc1'])))
    doc2 = int("".join(filter(str.isdigit, most_similar['Doc2'])))

    print("Most Similar Documents:")
    print("Jaccard Similairity: {}".format(most_similar['Jaccard_Score']))
    print("Signature Similarity: {}".format(most_similar['Signature_Score']))
    print("Document 1:")
    print(corpus[doc1])
    print("Document 2:")
    print(corpus[doc2])

    start_time = time.time()
    docs_lsh = lsh(docs_minhashing.signature_matrix, 25, 4, 0.8)
    pair_candidates = docs_lsh.fit_transform()
    print("Locality Sensitive Hashing success! in {} secs".format(round(time.time() - start_time, 2)))

    print("Sample Pair of Candidates:")
    print("Document 1:")
    print(corpus[next(iter(pair_candidates))[0]])
    print("Document 2:")
    print(corpus[next(iter(pair_candidates))[1]])
