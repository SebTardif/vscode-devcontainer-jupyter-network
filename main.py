# Return an indefinite article "a" or "an" for the animal name.
def article(name):
    if name[0].lower() in "aeiou":
        return "an"
    else:
        return "a"


from enum import Enum
from functools import total_ordering


class Truth(Enum):
    FALSE = 0
    TRUE = 1
    UNKNOWN = 2

    # Return TRUE, FALSE, or UNKNOWN.
    def __str__(self):
        return self.name


class Operator(Enum):
    NONE = 5
    FACT = 4
    PAREN = 3
    NOT = 2
    AND = 1
    OR = 0


# Operator precedence.
# A higher number means a greater precedence.
class Precedence(Enum):
    NONE = 5
    FACT = 4
    PAREN = 3
    NOT = 2
    AND = 1
    OR = 1

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


# Return the enum values for the operator and its precedence.
def parse_operator(operator):
    if operator == "!":
        return Operator.NOT, Precedence.NOT
    if operator == "&":
        return Operator.AND, Precedence.AND
    if operator == "|":
        return Operator.OR, Precedence.OR
    return Operator.NONE, Precedence.NONE


# Represents a complete rule of the form 'antecedent -> consequent'.
# The antecedent is a BoolExpression and the consequent is a fact.
class Rule:
    def __init__(self, rule_string):
        ...

    # Return the truth of the rule's consequent.
    def truth(self, facts):
        return facts[self.consequent]

    # Return a set holding this rule's facts. That includes
    # the consequent and the facts in the antecedent.
    def list_facts(self):
        return self.antecedent.list_facts().union({self.consequent})

    # Evaluate the antecedent. If it's now TRUE,
    # then set the consequent's value.
    def evaluate(self, facts, explain):
        ...

    # Return a string that explains the reason why this rule's value changed.
    def explain(self, facts):
        ...


# Represents a Boolean expression.
class BoolExpression:
    # Parse the expression.
    def __init__(self, expression):
        ...

    # Return a set holding the facts that this expression needs for evaluation.
    def list_facts(self):
        ...

    # Evaluate the expression given the current facts.
    def evaluate(self, facts):
        ...


class Truthifier:
    def __init__(self, rule_strings):
        self.load_rules(rule_strings)
        self.load_facts()
        self.load_questions()
        self.goals_reached = []

    # Build the rules list.
    def load_rules(self, rule_strings):
        self.rules = []
        for rule_string in rule_strings:
            self.rules.append(Rule(rule_string))

    # Build the facts dictionary.
    def load_facts(self):
        self.facts = {}
        for rule in self.rules:
            for fact in rule.list_facts():
                self.facts[fact] = Truth.UNKNOWN

    # Build the questions list.
    # This includes all facts that are not consequents.
    def load_questions(self):
        # Build a list of consequents.
        consequents = set()
        for rule in self.rules:
            consequents.add(rule.consequent)

        # Make the list of questions.
        self.questions = []
        for rule in self.rules:
            for fact in rule.antecedent.list_facts():
                if fact not in consequents:
                    if fact not in self.questions:
                        self.questions.append(fact)

    # Display the questions.
    def dump_questions(self):
        print("\n*** QUESTIONS ***")
        for question in self.questions:
            print(f"    {question} = {self.facts[question]}")

    # Display the rules.
    def dump_rules(self):
        print("\n*** RULES ***")
        for rule in self.rules:
            print(f"    {rule.rule_string} = {self.facts[rule.consequent]}")

    # Display the facts.
    def dump_facts(self):
        print("\n*** FACTS ***")
        for key, value in self.facts.items():
            print(f"    {key}: {value}")

    # Ask questions until we reach a goal.
    def solve(self):
        EXPLAIN = True

        # Print instructions.
        print("Instructions:")
        print("    y = Yes")
        print("    n = No")
        print("    ? = Unknown")
        print("    d = Dump data")
        print("    q = Quit")
        print()
        self.asdf()

        # Ask questions.
        for question in self.questions:
            # Only ask about UNKNOWN questions.
            if self.facts[question] == Truth.UNKNOWN:
                # Ask about this question.
                while True:
                    answer = input(f"{question}? ").lower()
                    if answer == "q":
                        print("Quitting")
                        return
                    elif answer == "y":
                        self.facts[question] = Truth.TRUE
                        break
                    elif answer == "n":
                        self.facts[question] = Truth.FALSE
                        break
                    elif answer == "?":
                        break
                    elif answer == "d":
                        # Dump data.
                        self.dump_questions()
                        self.dump_rules()
                        self.dump_facts()
                        print()

                # Try solving again.
                self.evaluate_rules(EXPLAIN)

                # If we reached a goal, break out of the input loop.
                if len(self.goals_reached) > 0:
                    break

    # Evaluate UNKNOWN rules as long as something changes.
    def evaluate_rules(self, explain):
        had_change = True
        while had_change:
            # Assume nothing will change during this pass.
            had_change = False

            # Evaluate the rules.
            for rule in self.rules:
                # Only evaluate rules that are UNKNOWN.
                if rule.truth(self.facts) == Truth.UNKNOWN:
                    truth = rule.evaluate(self.facts, explain)
                    if truth != Truth.UNKNOWN:
                        # This rule now has a value.
                        self.facts[rule.consequent] = truth
                        had_change = True

                        # If this is a goal, and it's true,
                        # and it's not already in goals_reached,
                        # then add it to goals_reached.
                        if (
                            rule.is_goal
                            and (truth == Truth.TRUE)
                            and (rule not in self.goals_reached)
                        ):
                            self.goals_reached.append(rule)


# The main program.

# Animals:
#       platypus
#       squirrel
#       coelacanth
#       alligator
#       giraffe
#       squid
#       tiger
#       tortoise

# Load the rule base.
rule_strings = [
    "has fur -> mammal",
    "mammal -> !reptile",
    "scaled & breathes water -> fish",
    "scaled & !breathes water -> reptile",
    "mammal & lays eggs -> $platypus",
    "mammal & looks like a mad scientist experiment -> $platypus",
    "mammal & arboreal -> $squirrel",
    "fish & !many arms -> $coelacanth",
    "reptile & !shelled -> $alligator",
    "mammal & ridiculously long neck -> $giraffe",
    "breathes water & many arms -> $squid",
    "(mammal & carnivore) | (mammal & striped) -> $tiger",
    "scaled & !breathes water & shelled -> $tortoise",
]

# Make the expert.
expert = Truthifier(rule_strings)

# Solve the system.
expert.solve()

# See if we have reached any goals.
if len(expert.goals_reached) == 0:
    # We're doomed!
    print("Sorry, I was unable to identify the animal.")
elif len(expert.goals_reached) == 1:
    # We reached one goal.
    rule_name = expert.goals_reached[0].consequent
    print(f"You are probably looking at {article(rule_name)} {rule_name}")
else:
    # We reached multiple goals.
    print(f"You are probably looking at one of the following animals:")
    for rule in expert.goals_reached:
        rule_name = rule.consequent
        print(f"{article(rule_name)} {rule_name}")
