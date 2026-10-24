# DPS970 Activity 2: Logic

## Q2: Valid, unsatisfiable, or neither

### a) Smoke ⇒ Fire

| Smoke | Fire | Smoke ⇒ Fire |
|-------|------|---------------|
|   T   |   T  |       T       |
|   T   |   F  |       F       |
|   F   |   T  |       T       |
|   F   |   F  |       T       |


Final column: mixed

Decision: neither, because the whole is a mixed result
        It’s true when Smoke = T, Fire = T, so it isn’t unsatisfiable. It’s false when Smoke = T, Fire = F, so it isn’t valid. So it’s neither.

#### Check with equivalence rules:


Smoke ⇒ Fire ≡ ¬Smoke ∨ Fire

    ==> ¬Smoke ∨ Fire is false only when both parts are false. 
        This is only true when smoke is true nd fire is false, 
        which matches the row in the table.

### b) ((Smoke ∧ Heat) ⇒ Fire) ⇔ ((Smoke ⇒ Fire) ∨ (Heat ⇒ Fire))

| Smoke | Heat | Fire | Smoke∧Heat | (Smoke∧Heat)⇒Fire | Smoke⇒Fire | Heat⇒Fire | (Smoke⇒Fire)∨(Heat⇒Fire) | Whole ⇔ |
|-------|------|------|------------|--------------------|------------|------------|---------------------------|----------|
|   T   |   T  |   T  |     T      |          T         |      T     |     T      |              T            |     T    |
|   T   |   T  |   F  |     T      |          F         |      F     |     F      |              F            |     T    |
|   T   |   F  |   T  |     F      |          T         |      T     |     T      |              T            |     T    |
|   T   |   F  |   F  |     F      |          T         |      F     |     T      |              T            |     T    |
|   F   |   T  |   T  |     F      |          T         |      T     |     T      |              T            |     T    |
|   F   |   T  |   F  |     F      |          T         |      T     |     F      |              T            |     T    |
|   F   |   F  |   T  |     F      |          T         |      T     |     T      |              T            |     T    |
|   F   |   F  |   F  |     F      |          T         |      T     |     T      |              T            |     T    |


Final column: all T
Decision: valid

Check with equivalence rules (left side, then right side, then compare):
1. Left side: (Smoke ∧ Heat) ⇒ Fire

   ≡ ¬(Smoke ∧ Heat) ∨ Fire        (implication elimination)

   ≡ (¬Smoke ∨ ¬Heat) ∨ Fire       (De Morgan)

   ≡ ¬Smoke ∨ ¬Heat ∨ Fire         (associativity)


2. Right side: (Smoke ⇒ Fire) ∨ (Heat ⇒ Fire)

   ≡ (¬Smoke ∨ Fire) ∨ (¬Heat ∨ Fire)   (implication elimination on each part)

   ≡ ¬Smoke ∨ ¬Heat ∨ Fire ∨ Fire       (associativity, commutativity)

   ≡ ¬Smoke ∨ ¬Heat ∨ Fire              (a ∨ a ≡ a)


3. Compare: Both sides become the same expression: ¬Smoke ∨ ¬Heat ∨ Fire.
    So, the sentence has the form X ⇔ X, and X ⇔ X is always true.
    This matches the truth table, where the two columns were identical 
    in every row. So the sentence is valid.

## Q3: Number of models

Vocabulary: A, B, C, D. Total models = 2^4 = _16_

### a) B ∨ C
- Models where B ∨ C is false: _4_
- Models where it is true: _16_ − _4_ = _12_
- Answer: _12_

### b) (A ⇒ B) ∧ A ∧ ¬B ∧ C ∧ D
- Simplification / reasoning: Negation of B needing to be true means B is false, that would make the implication false since A needs to be true. 
- Answer: _0_

## Q4: [(Food ⇒ Party) ∨ (Drinks ⇒ Party)] ⇒ [(Food ∧ Drinks) ⇒ Party]

### a) Enumeration

| Food | Drinks | Party | Food⇒Party | Drinks⇒Party | LHS | Food∧Drinks | RHS | LHS ⇒ RHS |
|------|--------|-------|------------|--------------|-----|-------------|-----|-----------|
|  T   |   T    |   T   |     T      |      T       |  T  |      T      |  T  |     T     |
|  T   |   T    |   F   |     F      |      F       |  F  |      T      |  F  |     T     |
|  T   |   F    |   T   |     T      |      T       |  T  |      F      |  T  |     T     |
|  T   |   F    |   F   |     F      |      T       |  T  |      F      |  T  |     T     |
|  F   |   T    |   T   |     T      |      T       |  T  |      F      |  T  |     T     |
|  F   |   T    |   F   |     T      |      F       |  T  |      F      |  T  |     T     |
|  F   |   F    |   T   |     T      |      T       |  T  |      F      |  T  |     T     |
|  F   |   F    |   F   |     T      |      T       |  T  |      F      |  T  |     T     |

Final column: all T
Decision: valid. The sentence is true in all 8 rows, so it is true in every
model. (Whenever LHS is true, RHS is also true. The only row where RHS is
false is row 2, and LHS is false there too.)

### b) CNF conversion

Left-hand side: (Food ⇒ Party) ∨ (Drinks ⇒ Party)
1. Eliminate ⇒:           (¬Food ∨ Party) ∨ (¬Drinks ∨ Party)
2. Move ¬ inward:         nothing to do (no negation sits outside a bracket)
3. Distribute ∨ over ∧:   nothing to do (there is no ∧)
4. Remove duplicates:     ¬Food ∨ ¬Drinks ∨ Party ∨ Party  →  ¬Food ∨ ¬Drinks ∨ Party
LHS in CNF: (¬Food ∨ ¬Drinks ∨ Party)

Right-hand side: (Food ∧ Drinks) ⇒ Party
1. Eliminate ⇒:           ¬(Food ∧ Drinks) ∨ Party
2. Move ¬ inward (De Morgan):  (¬Food ∨ ¬Drinks) ∨ Party
3. Distribute ∨ over ∧:   nothing to do
4. Remove duplicates:     none
RHS in CNF: (¬Food ∨ ¬Drinks ∨ Party)

How this confirms (a): both sides become the same single clause,
(¬Food ∨ ¬Drinks ∨ Party). So LHS ≡ RHS, and the main sentence has the form
X ⇒ X ≡ ¬X ∨ X, which is true in every model. That matches the truth table,
where the sentence is true in all 8 rows, so it is valid.

### c) Resolution proof

To prove the sentence is valid, we need to assume its negation and derive a contradiction.

Negation: ¬(LHS ⇒ RHS)

    ≡ ¬(¬LHS ∨ RHS)      (implication elimination)

    ≡ LHS ∧ ¬RHS         (De Morgan, double negation)

LHS in CNF is the clause from (b). For ¬RHS:

    ¬((Food ∧ Drinks) ⇒ Party)

    ≡ ¬(¬(Food ∧ Drinks) ∨ Party)

    ≡ (Food ∧ Drinks) ∧ ¬Party

  which gives three separate clauses: Food, Drinks, ¬Party.

Clauses:
1. ¬Food ∨ ¬Drinks ∨ Party
2. Food
3. Drinks
4. ¬Party

Resolution steps:

5. ¬Drinks ∨ Party    (resolve 1 and 2 on Food)
6. Party              (resolve 5 and 3 on Drinks)
7. empty clause       (resolve 6 and 4 on Party)

Conclusion: the negation of the sentence leads to the empty clause, so the
negation is unsatisfiable. Therefore the original sentence is valid, which
agrees with (a) and (b).