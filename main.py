# Return an indefinite article "a" or "an" for the animal name.
from typing import Any


def article(name):
    if name[0].lower() in "aeiou":
        return "an"
    else:
        return "a"


from enum import Enum


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


# Represents a Boolean expression.
class BoolExpression:
    # Parse the expression.
    def __init__(self, expression):
        # Remove whitespace and save the expression string.
        expression = expression.strip()
        self.expression = expression

        # The goal is to set these properties.
        self.operator = None
        self.operand1 = None
        self.operand2 = None

        # Find the lowest precedence operator that
        # is not inside parentheses.
        # Initially we have no operator.
        best_prec = Precedence.NONE
        best_i = -1
        best_op = Operator.NONE

        # Loop through the expression.
        open_parens = 0
        for i in range(len(expression)):
            ch = expression[i]
            if ch == '(':
                open_parens += 1
            elif ch == ')':
                open_parens -= 1
                if open_parens < 0:
                    raise Exception(f'Extra close paren ")" in "{expression}" at position {i}')
            elif open_parens == 0:
                # No parens are currently open.
                # If this is an operator, see if it is an improvement.
                new_op, new_prec = parse_operator(ch)
                if new_prec < best_prec:
                    best_prec = new_prec
                    best_i = i
                    best_op = new_op

        # See if all parens were closed.
        if open_parens > 0:
            raise Exception(f'Unclosed open paren "(" in "{expression}"')

        # If we still have no operator, then either:
        #    - The expression has the form "(subexpression)"
        #    - The expression is a question like 'breathes water'
        if best_i < 0:
            # See if it's (subexpression).
            if expression[0] == '(':
                # Remove the parentheses.
                expression = expression.strip()[1:-1]

                # Evaluate whatever was inside the parentheses.
                self.operator = Operator.PAREN
                self.operand1 = BoolExpression(expression)
                self.operand2 = None
                return
            else:
                # It's a question.
                self.operator = Operator.FACT
                self.operand1 = expression
                self.operand2 = None
                return

        # We have an operator.
        self.operator = best_op

        # Split the expression at the operator.
        if best_op == Operator.NOT:
            # NOT.
            # Remove the !.
            self.operand1 = BoolExpression(expression[1:])
        else:
            # AND and OR.
            # Split at the operator (removing the operator).
            self.operand1 = BoolExpression(expression[:best_i])
            self.operand2 = BoolExpression(expression[best_i + 1:])

    # Return a set holding the facts that this expression needs for evaluation.
    def list_facts(self):
        # FACT
        if self.operator == Operator.FACT:
            return {self.operand1}

        # PAREN or NOT
        if self.operator == Operator.PAREN or self.operator == Operator.NOT:
            return self.operand1.list_facts()

        # AND or OR
        if self.operator == Operator.AND or self.operator == Operator.OR:
            return self.operand1.list_facts().union(self.operand2.list_facts())

    # Evaluate the expression given the current facts.
    def evaluate(self, facts):
        # FACT
        if self.operator == Operator.FACT:
            # Just return whatever is in facts.
            return facts[self.operand1]

        # PAREN
        if self.operator == Operator.PAREN:
            # Evaluate operand1 and return its value.
            return self.operand1.evaluate(facts)

        # NOT
        if self.operator == Operator.NOT:
            # If the value is TRUE or FALSE, negate it.
            truth1 = self.operand1.evaluate(facts)
            if truth1 == Truth.TRUE:
                return Truth.FALSE
            if truth1 == Truth.FALSE:
                return Truth.TRUE
            return Truth.UNKNOWN

        # AND
        if self.operator == Operator.AND:
            # If both values are TRUE, return TRUE.
            # If either value is FALSE, return FALSE.
            # Otherwise, return UNKNOWN.
            truth1 = self.operand1.evaluate(facts)
            truth2 = self.operand2.evaluate(facts)
            if truth1 == Truth.TRUE and truth2 == Truth.TRUE:
                return Truth.TRUE
            if truth1 == Truth.FALSE or truth2 == Truth.FALSE:
                return Truth.FALSE
            return Truth.UNKNOWN

        # OR
        if self.operator == Operator.OR:
            # If either value is TRUE, return TRUE.
            # If both values are FALSE, return FALSE.
            # Otherwise, return UNKNOWN.
            truth1 = self.operand1.evaluate(facts)
            truth2 = self.operand2.evaluate(facts)
            if truth1 == Truth.TRUE or truth2 == Truth.TRUE:
                return Truth.TRUE
            if truth1 == Truth.FALSE and truth2 == Truth.FALSE:
                return Truth.FALSE
            return Truth.UNKNOWN


# Represents a complete rule of the form 'antecedent -> consequent'.
# The antecedent is a BoolExpression and the consequent is a fact.
class Rule:
    antecedent: BoolExpression
    is_goal: bool
    is_negated: bool
    rule_string: str
    antecedent_truth: Truth
    antecedent_string: str
    consequent_string: str

    def __init__(self, rule_string):
        self.antecedent_truth = Truth.UNKNOWN
        self.rule_string = rule_string.strip()
        self.antecedent_string, self.consequent_string = rule_string.strip().split("->")
        self.is_negated = '!' in self.consequent_string
        self.is_goal = '$' in self.consequent_string
        self.consequent = self.consequent_string.replace('!', '').replace('$', '').strip()
        self.antecedent = BoolExpression(self.antecedent_string)

    # Return the truth of the rule's consequent.
    def truth(self, facts):
        return facts[self.consequent]

    # Return a set holding this rule's facts. That includes
    # the consequent and the facts in the antecedent.
    def list_facts(self):
        return self.antecedent.list_facts().union({self.consequent})

    # Evaluate the antecedent. If it's now TRUE,
    # then set the consequent's value.
    def evaluate(self, facts, explain: bool):
        # If the consequent's truth is known, return it.
        if facts[self.consequent] != Truth.UNKNOWN:
            return facts[self.consequent]

        # If we have previously set the antecedent's truth,
        # return the consequent's current truth.
        if self.antecedent_truth != Truth.UNKNOWN:
            return facts[self.consequent]  # has to be UNKNOWN

        # Otherwise evaluate the antecedent.
        truth = self.antecedent.evaluate(facts)

        # See if the antecedent is now TRUE.
        if truth == Truth.TRUE:
            # It's true. Set the consequent's truth value.
            # Negate if necessary.
            if self.is_negated:
                facts[self.consequent] = Truth.FALSE
            else:
                facts[self.consequent] = Truth.TRUE

            # If we should explain, do so.
            if explain:
                print(self.explain(facts))

        # Return the result in the fact's dictionary.
        return facts[self.consequent]

    # Return a string that explains the reason why this rule's value changed.
    def explain(self, facts):
        if self.is_goal:
            result = f'    GOAL {self.consequent} is {facts[self.consequent]} because:'
        else:
            result = f'    RULE {self.consequent} is {facts[self.consequent]} because:'
        result += f'\n        it follows from '

        # If we're negated, add "not."
        if self.is_negated:
            result += 'NOT '

        # Add the antecedent expression.
        result += f'"{self.antecedent_string}" and:'

        # Add the facts that go into the evaluation.
        for fact_name in self.antecedent.list_facts():
            # Only list facts that are not UNKNOWN.
            if facts[fact_name] != Truth.UNKNOWN:
                result += f'\n            {fact_name} = {facts[fact_name]}'
        return result


class Truthifier:
    facts: dict[Any, Truth]
    goals_reached: list[Any]

    def __init__(self, rule_strings):
        self.rules = None
        self.facts = dict[Any, Truth]
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
