from itertools import combinations
from collections import Counter
import time

def loadTransactions(filename):
    transactions = []
    with open(filename) as f:
        lines = f.readlines()
        for line in lines:
            transaction = line.rstrip().split(" ")
            items = [int(item) for item in transaction]
            transactions.append(items)
            
    return transactions

class frequentItemsets:

    def __init__(self, min_support):
        self.min_support = min_support

    def getItemsets(self, transactions):
        Cs_k = Counter(item for items in transactions for item in set(items))
        Ls_k = {key: Cs_k[key] for key in Cs_k if Cs_k[key] > self.min_support}
        L_k = [key for key in Ls_k]
        
        return Ls_k, L_k

    def filterPairs(self, pair, k, L_k):
        subset = set([p if k > 2 else p[0] for p in combinations(pair, k-1)])
        superset = set(L_k)
        
        return subset.issubset(superset)

    def newTransactions(self, transactions_master, k, L_k):
        transactions_k = []
        for transaction in transactions_master:
            pairs = list(combinations(transaction, k))
            candidates = [pair for pair in pairs if self.filterPairs(pair, k, L_k)]
            transactions_k.append(candidates)
        
        return transactions_k

    def fitTransform(self, transactions_master):
        start = time.time()
        final_itemsets = {}
        non_singleton = []
        Ls_1, L_1 = self.getItemsets(transactions_master)
        print("There are {} 1-itemsets (singleton) in {} s".format(len(L_1), round(time.time() - start, 3)))
        Ls_1 = sorted(Ls_1.items())
        # UPDATE: Here we filter the original transactions/basket by removing items that not selected in the L_1 (singleton)
        new_transactions_master = [[item for item in trx if item in L_1] for trx in transactions_master]
        final_itemsets.update(Ls_1)
        L_k = L_1
        k = 2
        while len(L_k) > 1: # UPDATE: here we change the loop condition by setting minimum element in the L_k to be more than 1
            start = time.time()
            transactions_k = self.newTransactions(new_transactions_master, k, L_k)
            Ls_k, L_k = self.getItemsets(transactions_k)
            Ls_k = sorted(Ls_k.items())
            print("There are {} {}-itemsets in {} s".format(len(L_k), k, round(time.time() - start, 3)))
            final_itemsets.update(Ls_k)
            non_singleton.append(Ls_k)
            k += 1

        return final_itemsets, non_singleton

class associationRules:

    def __init__(self, min_confidence):
        self.min_confidence = min_confidence

    def fitTransform(self, final_itemsets, non_singleton):
        rules = []
        for l in non_singleton :
            for itemset, support in l:
                k = len(itemset)
                for i in range(1,k):
                    subsets = list(combinations(set(itemset), i))
                    
                    for a in subsets :
                        if len(a)==1:
                            key = a[0]
                        else: 
                            key = tuple(sorted(a))

                        support_a = final_itemsets[key]
                        confidence = support / support_a
                        if confidence >= self.min_confidence :
                            rules.append((set(a),set(itemset).difference(set(a)),confidence))
        
        return rules

if __name__ == "__main__":
    # Load data
    filename = 'data/T10I4D100K.dat'
    transactions = loadTransactions(filename)

    min_support = 1000
    min_confidence = 0.5
    
    print("Finding the frequent itemsets with minimum support {}:".format(min_support))
    # Frequent Itemset
    start = time.time()
    FIS = frequentItemsets(min_support)
    itemsets, non_singleton = FIS.fitTransform(transactions)
    print('TIME TOTAL: {} s'.format(round(time.time() - start, 3)))

    print("Finding the available association rules with minimum confidence {}:".format(min_confidence))
    # Association Rules
    start = time.time()
    AR = associationRules(min_confidence)
    rules = AR.fitTransform(itemsets, non_singleton)
    print('TIME TOTAL: {} s'.format(round(time.time() - start, 3)))

    SHOW = 15
    n_rules = len(rules)
    rules.sort(key=lambda tup: tup[2], reverse=True)
    print("Found {} rules, showing {}".format(n_rules, min(SHOW, n_rules)))
    for i in range(min(SHOW, n_rules)):
        antecedent, consequent, confidence = rules[i]
        print("{} -> {} (confidence: {})".format(antecedent, consequent, round(confidence, 3)))