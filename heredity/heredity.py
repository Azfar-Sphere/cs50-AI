import csv
import itertools
import sys
import math

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }
    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    joint_pb = 1
    for person in people:
        final_pb = 0
        gene_pb = 0
        trait_pb = 0

        father = people[person]["father"]
        mother = people[person]["mother"]

        if person in one_gene:
            if father:

                gets_father = 0.01
                c_father = 0.01
                gets_mother = 0.01
                c_mother = 0.01

                if father in one_gene:
                    gets_father = (0.5 * PROBS["mutation"]) + (0.5 * (1 - PROBS["mutation"]))
                elif father in two_genes:
                    gets_father = 1 - PROBS["mutation"]
                else:
                    gets_father = PROBS["mutation"]

                c_father = 1 - gets_father

                if mother in one_gene:
                    gets_mother = (0.5 * PROBS["mutation"]) + (0.5 * (1 - PROBS["mutation"]))
                elif mother in two_genes:
                    gets_mother = 1 - PROBS["mutation"]
                else:
                    gets_mother = PROBS["mutation"]

                c_mother = 1 - gets_mother

                s1 = math.fsum([(gets_father * c_mother)])
                s2 = math.fsum([(gets_mother * c_father)])
                gene_pb = math.fsum([s1 + s2])

            else:
                gene_pb = PROBS["gene"][1]

        elif person in two_genes:
            if father:
                gets_father = 0.01
                c_father = 0.01
                gets_mother = 0.01
                c_mother = 0.01

                if father in one_gene:
                    gets_father = (0.5 * PROBS["mutation"]) + (0.5 * (1 - PROBS["mutation"]))
                elif father in two_genes:
                    gets_father = 1 * (1 - PROBS["mutation"])
                else:
                    gets_father = PROBS["mutation"]

                c_father = 1 - gets_father

                if mother in one_gene:
                    gets_mother = (0.5 * PROBS["mutation"]) + (0.5 * (1 - PROBS["mutation"]))
                elif mother in two_genes:
                    gets_mother = 1 * (1 - PROBS["mutation"])
                else:
                    gets_mother = PROBS["mutation"]

                c_mother = 1 - gets_mother
                
                gene_pb = math.fsum([gets_father * gets_mother])

            else:
                gene_pb = PROBS["gene"][2]
            
        elif person not in one_gene and person not in two_genes:
            if father:
                gets_father = 0.01
                c_father = 0.01
                gets_mother = 0.01
                c_mother = 0.01

                if father in one_gene:
                    gets_father = (0.5 * PROBS["mutation"]) + (0.5 * (1 - PROBS["mutation"]))
                elif father in two_genes:
                    gets_father = 1 * (1 - PROBS["mutation"])
                else:
                    gets_father = PROBS["mutation"]

                c_father = 1 - gets_father

                if mother in one_gene:
                    gets_mother = (0.5 * PROBS["mutation"]) + (0.5 * (1 - PROBS["mutation"]))
                elif mother in two_genes:
                    gets_mother = 1 * (1 - PROBS["mutation"])
                else:
                    gets_mother = PROBS["mutation"]

                c_mother = 1 - gets_mother

                gene_pb = math.fsum([(c_father * c_mother)])

            else:
                gene_pb = PROBS["gene"][0]

        if person in have_trait:
            if person in two_genes:
                trait_pb = PROBS["trait"][2][True]
            elif person in one_gene:
                trait_pb = PROBS["trait"][1][True]
            elif person not in one_gene and person not in two_genes:
                trait_pb = PROBS["trait"][0][True]

        elif person not in have_trait:
            if person in two_genes:
                trait_pb = PROBS["trait"][2][False]
            elif person in one_gene:
                trait_pb = PROBS["trait"][1][False]
            elif person not in one_gene and person not in two_genes:
                trait_pb = PROBS["trait"][0][False]
        
        final_pb = math.fsum([gene_pb * trait_pb])
        joint_pb = joint_pb * final_pb

    return joint_pb


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:

        if person in one_gene:
            probabilities[person]["gene"][1] += p
            if person in have_trait:
                probabilities[person]["trait"][True] += p
            else:
                probabilities[person]["trait"][False] += p

        elif person in two_genes:
            probabilities[person]["gene"][2] += p
            if person in have_trait:
                probabilities[person]["trait"][True] += p
            else:
                probabilities[person]["trait"][False] += p
        
        else:
            probabilities[person]["gene"][0] += p
            if person in have_trait:
                probabilities[person]["trait"][True] += p
            else:
                probabilities[person]["trait"][False] += p
        

def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:

        sum_gene = 0
        sum_trait = 0

        for gene in probabilities[person]["gene"]:
            sum_gene += probabilities[person]["gene"][gene]

        for trait in probabilities[person]["trait"]:
            sum_trait += probabilities[person]["trait"][trait]
        
        g_factor = math.fsum([1 / sum_gene])
        t_factor = math.fsum([1 / sum_trait])

        for gene in probabilities[person]["gene"]:
            probabilities[person]["gene"][gene] *= g_factor

        for trait in probabilities[person]["trait"]:
            probabilities[person]["trait"][trait] *= t_factor
        

if __name__ == "__main__":
    main()
