# import random
import itertools

import pickle

import numpy as np
import pandas as pd
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# from scipy import sparse
# import random
import lightfm
from lightfm import LightFM, cross_validation
from lightfm.evaluation import precision_at_k, auc_score
# from sklearn.metrics.pairwise import cosine_similarity

# from collections import defaultdict

## Parameter Tuning
def sample_hyperparameters():
    """
    Yield possible hyperparameter choices.
    """

    while True:
        yield {
            "no_components": np.random.randint(16, 64),
            "learning_schedule": np.random.choice(["adagrad", "adadelta"]),
            "loss": np.random.choice(["bpr", "warp", "warp-kos"]),
            "learning_rate": np.random.exponential(0.05),
            "item_alpha": np.random.exponential(1e-8),
            "user_alpha": np.random.exponential(1e-8),
            "max_sampled": np.random.randint(5, 15),
            "num_epochs": np.random.randint(5, 50),
        }

# Creating an interaction matrix df from transactional type interactions
def create_interaction_matrix(df, user_col, item_col, rating_col, norm=False, threshold=None):
    interactions = df.groupby([user_col, item_col])[rating_col].sum().unstack().reset_index().fillna(0).set_index(user_col)
    if norm:
        interactions = interactions.applymap(lambda x: 1 if x > threshold else 0)
    return interactions

# Function to create a user dictionary based on their index and number in
# interaction dataset
def create_user_dict(interactions):
    user_id = list(interactions.index)
    user_dict = {}
    counter = 0 
    for i in user_id:
        user_dict[i] = counter
        counter += 1
    return user_dict

# Function to create an item dictionary based on their item_id and item name
def create_item_dict(df, id_col, name_col):
    item_dict = {}
    for i in range(df.shape[0]):
        item_dict[(df.loc[i,id_col])] = df.loc[i, name_col]
    return item_dict

# Runs the matrix factorization algorithm and returns the trained model
def runMF(interactions, n_components=30, loss='warp', k=15, epoch=30, n_jobs = 4):
#     x = sparse.csr_matrix(interactions.values)
    model = LightFM(no_components = n_components, loss=loss, k=k)
    model.fit(interactions, epochs=epoch, num_threads = n_jobs)
    return model

# Parameter Tuning
def random_search(train, test, num_samples=50, num_threads=4):
    for hyperparams in itertools.islice(sample_hyperparameters(), num_samples):
        num_epochs = hyperparams.pop("num_epochs")
        
        model = LightFM(**hyperparams)
        model.fit(train, epochs=num_epochs, num_threads=num_threads)
        
        test_auc = auc_score(model, test, train_interactions=train, num_threads=num_threads).mean()
        train_auc = auc_score(model, train, num_threads=num_threads).mean()
        
        hyperparams["num_epochs"] = num_epochs
        
        yield (test_auc, train_auc, hyperparams, model)

# Produces user recommendations, prints the list of items the user already 
# prefers, prints the list of N recommended items which user will hopefully 
# prefer.
def sample_recommendation_user(model, interactions, user_id, user_dict, item_dict, threshold = 0, nrec_items = 10, show = True):
    n_users, n_items = interactions.shape # indices
    user_x = user_dict[user_id] # getting the specific user
    scores = pd.Series(model.predict(user_x, np.arange(n_items))) # model prediction
    scores.index = interactions.columns
    scores = list(pd.Series(scores.sort_values(ascending=False).index))
    
    known_items = list(pd.Series(interactions.loc[user_id,:]
                                 [interactions.loc[user_id,:] > threshold].index).sort_values(ascending=False))
    
    scores = [x for x in scores if x not in known_items]
    return_score_list = scores[0:nrec_items]
    known_items = list(pd.Series(known_items).apply(lambda x: item_dict[x]))
    scores = list(pd.Series(return_score_list).apply(lambda x: item_dict[x]))

    return(known_items + scores)
    # if show == True:
    #     print("Known Likes:")
    #     counter = 1
    #     for i in known_items:
    #         print(str(counter) + '- ' + i)
    #         counter+=1

    #     print("\n Recommended Items:")
    #     counter = 1
    #     for i in scores:
    #         print(str(counter) + '- ' + i)
    #         counter+=1
    # return return_score_list

def import_pickle_model():
    file = open('cf_model.pickle', 'rb')
    pickled_model = pickle.load(file)
    file.close()
    return pickled_model;