import timeit
import pandas as pd
import numpy as np
from numpy.random.mtrand import randint
from Meal_PLanner_Scripts import PlanGoals as pg
import json

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)


# gender: 1 for MALE, 2 for FEMALE
# activity: range 1 to 5, (sedentary, lightly active, moderately active, very active, extra active)

def preprocessing():
    data = pd.read_csv("recipes.csv")
    # # Adding an index column
    # data.insert(0, 'index', range(1, 1 + len(data)))
    # # Replacing all empty cells with "Missing"
    # data.replace(np.nan, 'Missing', regex=True, inplace= True)
    #
    # # Replacing the booleans with numbers (1 for True, 0 for False)
    # data.replace(to_replace='Missing', value=0, inplace = True)
    # data.replace(to_replace=False, value=0, inplace = True)
    # data.replace(to_replace=True, value=1, inplace = True)
    # # Round all float numbers
    #
    # data['calories'] = data['calories'] * (data['grams_per_serving']/100)
    # data['carbs'] = data['carbs'] * (data['grams_per_serving']/100)
    # data['fats'] = data['fats'] * (data['grams_per_serving']/100)
    # data['proteins'] = data['proteins'] * (data['grams_per_serving']/100)
    # data['saturated_fats'] = data['saturated_fats'] * (data['grams_per_serving'] / 100)
    #
    # data.drop(['proteins_per_serving',
    #            'carbs_per_serving','is_snack',
    #            'calories_per_serving',
    #            'fats_per_serving', 'id',
    #            'is_basic_food', 'is_recipe',
    #            'servings', 'prep_time',
    #            'iron', 'ingredients','potassium',
    #            'grams_per_serving','calcium',
    #            'needs_blender','needs_food_processor',
    #            'needs_grill', 'needs_microwave',
    #            'needs_stove','needs_oven', 'needs_toaster'], axis=1, inplace=True)
    #
    # data['cookTime'] = data['cookTime'] / 60
    # data['num_favorites'] = (data['num_favorites'] - data['num_favorites'].min()) / (
    #             data['num_favorites'].max() - data['num_favorites'].min())
    # data['value_ser1'] = data['cookTime'].apply(lambda x: 1 if x >= 4 else x/4)
    # data['value_ser1'] = data['value_ser1'] + (0.5 * data['prep_day_before'])
    # data['value_ser1'] = data['value_ser1'] + data['num_favorites']
    #
    # data['value_ser2'] = data['value_ser1']
    #
    # data.drop(['cookTime','num_favorites',
    #            'prep_day_before','complexity'], axis=1, inplace=True)
    #
    # cols = ['index', 'name', 'type', 'breakfast', 'main_dish',
    #         'calories', 'carbs', 'fats', 'proteins', 'saturated_fats',
    #         'sugar', 'value_ser1', 'value_ser2']
    #
    # data = data[cols]
    #
    # data['avg_val'] = (data['value_ser1'] + data['value_ser2']) / 2

    # print(data.head())
    # breakfast_meals = data[data['breakfast'] == 1]
    # #print(breakfast_meals.head())
    # breakfast_meals.iloc[67]['name'] = 'shit'
    # print(data[data['index'] == 68])
    #
    # print(breakfast_meals.iloc[0])

    data['value_ser1'] = 0
    data['value_ser2'] = 0
    data['avg_val'] = 0

    data.to_csv("recipes.csv", index=False)


def test():
    ans = servingsTable(4)
    print(ans)
    print(ans.dtype)


def servingsTable(num_meals):
    table_length = pow(2, num_meals)
    serv_table = np.zeros(shape=(table_length, num_meals))
    padding = '000000'

    for x in range(0, table_length):
        binary = bin(x)[2:]
        binary = ('0' * (num_meals - len(binary))) + binary
        for y in range(0, num_meals):
            serv_table[x, y] = int(binary[y]) + 1

    return serv_table


def MonteCarlo_Meals(data, epsilon, episodes, alpha, plan_goals):
    breakfast_meals = data[data['breakfast'] == 1]
    lunch_dinner = data[data['main_dish'] == 1]
    inbetween_meals = data[(data['breakfast'] == 0) & (data['main_dish'] == 0)]
    meal_types = ['breakfast', 'lunch', 'dinner', 'inbetweener_1', 'inbetweener_2', 'inbetweener_3']
    nutrition_Val = ['calories', 'fats', 'proteins', 'carbs']
    good_episodes = []
    counter = 0

    ### Generate Servings table for the number of meals

    serv_table = servingsTable(plan_goals.meals)

    while counter == 0:
        print('Trial')
        for k in range(0, episodes):
            print(k)
            episode_run = []

            for i in range(0, plan_goals.meals):

                if i == 0:
                    meals = breakfast_meals
                elif i < 2:
                    meals = lunch_dinner
                else:
                    meals = inbetween_meals

                greedyselection = randint(1, 10)

                if greedyselection <= epsilon:
                    rand_selection = randint(low=0, high=len(meals.index))
                    episode_run = np.append(episode_run, meals.iloc[rand_selection]['index'])
                else:
                    maxOfV = meals[meals['avg_val'] == meals['avg_val'].max()]['index']
                    # If multiple max values, take first
                    maxOfV = maxOfV.values[0]
                    episode_run = np.append(episode_run, maxOfV)

                episode_run = episode_run.astype(int)

            for i in range(2, serv_table.shape[0]):

                episode = pd.DataFrame(
                    {'meal_type': meal_types[:len(episode_run)], 'meal_index': episode_run, 'serving': serv_table[i]})

                episode['meal_index'] = (episode['meal_index']).astype(int)
                data['index'] = (data['index']).astype(int)

                detailed_episode = episode.merge(data[['index', 'name', 'value_ser1', 'value_ser2'] + nutrition_Val],
                                                 left_on='meal_index',
                                                 right_on='index', how='inner')

                for col in nutrition_Val:
                    detailed_episode[col] = detailed_episode[col] * detailed_episode['serving']

                result = 0
                reward = -1
                # Total nutritional value in the entire plan

                total_protein = detailed_episode['proteins'].sum()
                total_fats = detailed_episode['fats'].sum()
                total_calories = detailed_episode['calories'].sum()
                total_carbs = detailed_episode['carbs'].sum()

                if (plan_goals.needed_proteins[0] < total_protein) & (plan_goals.needed_proteins[1] > total_protein):
                    result += 1
                if (plan_goals.needed_carbs[0] < total_carbs) & (plan_goals.needed_carbs[1] > total_carbs):
                    result += 1
                if (plan_goals.needed_fats[0] < total_fats) & (plan_goals.needed_fats[1] > total_fats):
                    result += 1
                if abs(plan_goals.needed_calories - total_calories) < 100:
                    result += 1

                if result == 4:
                    counter += 1
                    reward = 1
                    good_episodes.append(detailed_episode)

                detailed_episode['return'] = reward

                for v in range(0, len(detailed_episode)):
                    serv = detailed_episode.iloc[v]['serving']
                    int(serv)
                    if detailed_episode.iloc[v]['return'] != 0:
                        update = data[data['index'] == detailed_episode.iloc[v]['meal_index']][
                                     'value_ser' + str(serv)[0]] + alpha * \
                                 ((detailed_episode.iloc[v]['return'] / plan_goals.meals) -
                                  data[data['index'] == detailed_episode.iloc[v]['meal_index']][
                                      'value_ser' + str(serv)[0]])

                        data.loc[(data['index'] == detailed_episode.iloc[v]['meal_index']), (
                                    'value_ser' + str(serv)[0])] = update

                data['avg_val'] = data[['value_ser2', 'value_ser1']].values.max(1)

    return good_episodes[0]


def main():
    data = pd.read_csv("C:/Users/pc/Pycharm Projects/MealPlanner_Attempt 2/Meal_PLanner_Scripts/recipes.csv")

    epsilon = 5
    episodes = 50
    alpha = 0.03
    plan_goals = pg.PlanGoals(activity=1, age=22, height=183, weight=55, gender=1, goal=0, num_of_meals=3)

    ans = MonteCarlo_Meals(data, epsilon, episodes, alpha, plan_goals)

    ans = ans.drop(['index', 'meal_index', 'value_ser1', 'value_ser2', 'return'], axis=1)
    ans = ans.set_index('meal_type')
    ans = ans.to_json(orient='index')

    print(ans)


if __name__ == "__main__":
    main()
