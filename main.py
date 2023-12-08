from enum import Enum


class Truth(Enum):
    FALSE = 0  # False
    TRUE = 1  # True
    UNKNOWN = 2  # The user doesn't know
    UNASKED = 3  # We have not asked about this feature yet

    # Return TRUE, FALSE, or UNKNOWN.
    def __str__(self):
        return self.name

    # Parse a Truth value from a string.
    @staticmethod
    def parse(string):
        return Truth[string.strip().upper()]
    # Represents the features of a particular animal.


class Animal:
    def __init__(self, name: str, features: dict[str, Truth]):
        self.name = name
        self.features = features
        self.why_not: str | None = None

    # Return the animal's value for this feature name.
    def feature_value(self, feature_name):
        return self.features[feature_name] if feature_name in self.features else Truth.UNKNOWN

    # Return 'a' or 'an' as appropriate for this animal's name.
    def article(self):
        if self.name[0] in 'aeiou':
            return f'an'
        return f'a'

    # Return the animal's name with an article.
    def full_name(self):
        return f'{self.article()} {self.name}'


class Eliminator:
    # Load the knowledge base.
    def __init__(self):
        self.all_features: dict[str, Truth] = dict()
        self.all_animals: list[Animal] = list()

    def load_knowledgebase(self):
        # Define the animals.
        self.all_animals = [
            Animal('platypus', {
                'has fur': Truth.TRUE,
                'scaled': Truth.FALSE,
                'breathes water': Truth.FALSE,
                'lays eggs': Truth.TRUE,
                'looks like experiment': Truth.TRUE,
                'arboreal': Truth.FALSE,
                'many arms': Truth.FALSE,
                'shelled': Truth.FALSE,
                'ridiculously long neck': Truth.FALSE,
                'striped': Truth.FALSE,
            }),
            Animal('squirrel', {
                'has fur': Truth.TRUE,
                'scaled': Truth.FALSE,
                'breathes water': Truth.FALSE,
                'looks like experiment': Truth.FALSE,
                'arboreal': Truth.TRUE,
                'shelled': Truth.FALSE,
                'ridiculously long neck': Truth.FALSE,
            }),
            Animal('coelacanth', {
                'has fur': Truth.FALSE,
                'scaled': Truth.TRUE,
                'breathes water': Truth.TRUE,
                'looks like experiment': Truth.FALSE,
                'arboreal': Truth.FALSE,
                'many arms': Truth.FALSE,
                'shelled': Truth.FALSE,
                'ridiculously long neck': Truth.FALSE,
                'striped': Truth.FALSE,
            }),
            Animal('alligator', {
                'has fur': Truth.FALSE,
                'scaled': Truth.TRUE,
                'breathes water': Truth.FALSE,
                'looks like experiment': Truth.FALSE,
                'arboreal': Truth.FALSE,
                'many arms': Truth.FALSE,
                'shelled': Truth.FALSE,
                'ridiculously long neck': Truth.FALSE,
                'carnivore': Truth.TRUE,
                'striped': Truth.FALSE,
            }),
            Animal('giraffe', {
                'has fur': Truth.TRUE,
                'scaled': Truth.FALSE,
                'breathes water': Truth.FALSE,
                'looks like experiment': Truth.FALSE,
                'arboreal': Truth.FALSE,
                'shelled': Truth.FALSE,
                'ridiculously long neck': Truth.TRUE,
                'striped': Truth.FALSE,
            }),
            Animal('squid', {
                'has fur': Truth.FALSE,
                'breathes water': Truth.TRUE,
                'arboreal': Truth.FALSE,
                'many arms': Truth.TRUE,
                'shelled': Truth.FALSE,
                'ridiculously long neck': Truth.FALSE,
                'striped': Truth.FALSE,
            }),
            Animal('tiger', {
                'has fur': Truth.TRUE,
                'scaled': Truth.FALSE,
                'breathes water': Truth.FALSE,
                'looks like experiment': Truth.FALSE,
                'arboreal': Truth.FALSE,
                'many arms': Truth.FALSE,
                'shelled': Truth.FALSE,
                'ridiculously long neck': Truth.FALSE,
                'carnivore': Truth.TRUE,
                'striped': Truth.TRUE,
            }),
            Animal('tortoise', {
                'has fur': Truth.FALSE,
                'scaled': Truth.TRUE,
                'breathes water': Truth.FALSE,
                'looks like experiment': Truth.FALSE,
                'arboreal': Truth.FALSE,
                'many arms': Truth.FALSE,
                'shelled': Truth.TRUE,
                'ridiculously long neck': Truth.FALSE,
                'striped': Truth.FALSE,
            })
        ]

        # Make a dictionary holding all feature names,
        # initially with truth values UNASKED.
        for animal in self.all_animals:
            for feature, _ in animal.features.items():
                self.all_features[feature] = Truth.UNASKED

    # Return the best feature to ask about next.
    def find_best_feature(self):
        # See which feature would eliminate the most animals.
        # Find the feature with max(min(TRUE animal count, FALSE animal count)).
        best_feature_name = None
        best_min_count = -1
        for feature_name in self.all_features:
            # Skip features that we have already used.
            if self.all_features[feature_name] != Truth.UNASKED:
                continue

            # Count the True and False animals for this feature.
            num_true = 0
            num_false = 0
            for animal in self.all_animals:
                # Skip animals that have already been eliminated.
                if animal.why_not is not None:
                    continue

                # Count the TRUE and FALSE values. Ignore UNKNOWN.
                animal_feature_truth = animal.feature_value(feature_name)
                if animal_feature_truth == Truth.TRUE:
                    num_true += 1
                elif animal_feature_truth == Truth.FALSE:
                    num_false += 1

            # Get the smallest of the TRUE and FALSE counts.
            min_count = min(num_true, num_false)

            # See if the new min_count is larger than the previous best.
            if min_count > best_min_count:
                best_feature_name = feature_name
                best_min_count = min_count

        # Return the best feature.
        return best_feature_name

    # Return a list holding all remaining animals.
    def remaining_animals(self):
        return [animal for animal in self.all_animals if animal.why_not is None]

    # Print all the animals that have not been eliminated.
    def print_remaining_animals(self):
        for animal in self.remaining_animals():
            print(f'    {animal.name}')

    # Explain our current reasoning.
    def explain(self):
        for feature_name, feature_value in self.all_features.items():
            if feature_value in [Truth.UNKNOWN, Truth.UNASKED]:
                continue
            print(f'has {feature_name} is {feature_value} so:')
            for animal in self.all_animals:
                if animal.why_not == feature_name:
                    print(f"    It's not {animal.full_name()}")
        print("It still could be:")
        self.print_remaining_animals()

    # Eliminate any animals that don't satisfy this feature.
    def eliminate_animals(self, feature_name, feature_truth):
        if feature_truth == Truth.UNKNOWN:
            return
        for animal in self.all_animals:
            if animal.why_not is not None:
                return
            feature_value = animal.feature_value(feature_name)
            if feature_value is Truth.UNKNOWN:
                continue
            if feature_value is not feature_truth:
                animal.why_not = feature_name
                print(f"Eliminated {animal.full_name()}")

    # If this feature has not been used before, and it cannot
    # differentiate among the remaining animals, set it to UNKNOWN.
    #
    # Return True if this feature can differentiate
    # among at least two of the remaining animals.
    def feature_can_differentiate(self, feature_name):
        # If this feature has already been used, it's no good.
        if self.all_features[feature_name] != Truth.UNASKED:
            return False

        # See if any animals have this feature as TRUE or FALSE.
        has_true = False
        has_false = False
        for animal in self.all_animals:
            # Skip animals that are already eliminated.
            if animal.why_not is not None:
                continue

            # Record this animal's feature value.
            animal_feature_value = animal.feature_value(feature_name)
            if animal_feature_value == Truth.TRUE:
                has_true = True
            if animal_feature_value == Truth.FALSE:
                has_false = True

        # If we didn't find both TRUE and FALSE values, then this
        # feature cannot differentiate among the remaining animals.
        if not (has_true and has_false):
            # This feature is no longer useful.
            self.all_features[feature_name] = Truth.UNKNOWN
            return False

        # The feature can still differentiate among the remaining animals.
        return True

    # Eliminate any features that cannot
    # differentiate among the remaining animals.
    def eliminate_features(self):
        for feature_name in self.all_features.keys():
            self.feature_can_differentiate(feature_name)

    # Return the number of remaining animals.
    def num_remaining_animals(self):
        return sum(1 for animal in self.all_animals if animal.why_not)

    # Return the number of unasked features.
    def num_unused_features(self):
        return sum(1 for value in self.all_features.values() if value == Truth.UNASKED)

    def solve(self):
        # Display instructions.
        print('Instructions:')
        print('    y for Yes')
        print('    n for No')
        print('    ? for Unknown')
        print('    e for Explain')
        print('    q for Quit\n')

        # Load the knowledge base.
        self.load_knowledgebase()

        # Ask questions forever (like a four-year-old).
        while True:
            # See which feature might eliminate the most animals.
            feature_name = self.find_best_feature()

            # See if we could not find a feature to use.
            if feature_name is None:
                print(f'\nSorry, I cannot tell what this animal is.😔\nIt could be:\n')
                self.print_remaining_animals()
                break  # Break out of the loop.

            # Ask about the chosen feature.
            answer = input(f'{feature_name}? ')
            if answer == 'q':
                # Quit.
                break
            elif answer == 'e':
                # Explain our current reasoning and continue
                # with a new question. (This will repeat the same question.)
                self.explain()
                continue
            elif answer == 'y':
                self.all_features[feature_name] = Truth.TRUE
            elif answer == 'n':
                self.all_features[feature_name] = Truth.FALSE
            elif answer == '?':
                self.all_features[feature_name] = Truth.UNKNOWN
            else:
                print(f"\nSorry, I don't know the command {answer}.\n")
                continue

            # Eliminate any invalid animals.
            self.eliminate_animals(feature_name, self.all_features[feature_name])

            # Eliminate any features that are not useful.
            self.eliminate_features()

            # See how many animals are still possibilities.
            num_animals = self.num_remaining_animals()
            if num_animals == 0:
                # We eliminated all the animals.
                print(f'\nSorry, I eliminated all of the possibilities.😔\n')
                break  # Break out of the loop.
            elif num_animals == 1:
                # We have only one remaining animal.
                animal = self.remaining_animals()[0]
                print(f'\nYou are probably looking at {animal.full_name()}')
                break  # Break out of the loop.
            elif self.num_unused_features() < 1:
                # We cannot differentiate among the remaining animals.
                print('\nSorry, I cannot differentiate among the remaining animals.😔')
                print('You are probably looking at one of the following:')
                self.print_remaining_animals()
                break  # Break out of the loop.


Eliminator().solve()
