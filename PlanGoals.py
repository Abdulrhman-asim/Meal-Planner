# gender: 1 for MALE, 2 for FEMALE
# activity: range 1 to 5, (sedentary, lightly active, moderately active, very active, extra active) respectively
# goal: 0 to maintain, 1 to gain, -1 to lose weight. We multiply it by 500 because you should add or
# remove around 500 calories from your normal calorie intake for a average paced progression towards your goal.


class PlanGoals:
    needed_proteins = []
    needed_calories = 0
    needed_carbs = []
    needed_fats = []
    meals = 0

    def __init__(self, activity, age, height, weight, gender, goal, num_of_meals):


        s = 5
        if gender == 2:
            s = -161

        if activity == 1:
            activity = 1.2
        if activity == 2:
            activity = 1.375
        if activity == 3:
            activity = 1.55
        if activity == 4:
            activity = 1.725
        if activity == 5:
            activity = 1.9

        bmr = (10 * weight) + (6.25 * height) - (5 * age) + s

        self.needed_calories = (bmr * activity) + (goal * 500)

        self.needed_fats.append((self.needed_calories * 0.20) / 9)
        self.needed_fats.append((self.needed_calories * 0.35) / 9)

        self.needed_carbs.append((self.needed_calories * 0.45) / 4)
        self.needed_carbs.append((self.needed_calories * 0.65) / 4)

        self.needed_proteins.append((self.needed_calories * 0.10) / 4)
        self.needed_proteins.append((self.needed_calories * 0.35) / 4)

        self.meals = num_of_meals
