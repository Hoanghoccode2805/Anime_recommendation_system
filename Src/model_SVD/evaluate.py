from collections import defaultdict
import config 

def precision_recall_at_k(predictions, k=10, threshold=9):
    # uid = userID, iid = itemID, true_r = real rating, est = predicted rating
    user_est_true = defaultdict(list)
    for uid, iid, true_r, est, _ in predictions:
        user_est_true[uid].append((est,true_r))

    precisions = {}
    recalls = {}
    for uid, user_ratings in user_est_true.items():
        # lambda input: ouput
        # reverse = True --> from large to small value
        #         = False --> from small to large value
        user_ratings.sort(key = lambda x : x[0], reverse = True )

        # Number of anime that users actually like (real ratings >= threshold)
        n_rel = sum((true_r >= threshold) for (_,true_r) in user_ratings)

        # In top-K, the number of recommended anime models
        n_rec_k =  min(k,len(user_ratings))

        # In that top-K, the number of anime that are actually relevant
        n_rel_and_rec_k = sum(
            (true_r >= threshold) for (est, true_r) in user_ratings[:k]
        )

        precisions[uid] = n_rel_and_rec_k / n_rec_k if n_rec_k != 0 else 0
        recalls[uid] = n_rel_and_rec_k / n_rel if n_rel != 0 else 0

    return precisions, recalls

def average_precision_recall(predictions, k=10, threshold=9):
    precisions, recalls = precision_recall_at_k(predictions, k, threshold)
    avg_precision = sum(precisions.values()) / len(precisions)
    avg_recall = sum(recalls.values()) / len(recalls)
    return avg_precision, avg_recall
 
 
if __name__ == "__main__":
    from surprise.model_selection import train_test_split
    from train_model import load_cleaned_data, build_dataset, train_SVD
 
    df = load_cleaned_data()
    data = build_dataset(df)
    trainset, testset = train_test_split(data, test_size=config.TEST_SIZE, random_state=config.RANDOM_STATE)
 
    model = train_SVD(trainset)
    predictions = model.test(testset)
 
    avg_precision, avg_recall = average_precision_recall(predictions, k=config.TOP_K, threshold=config.THRESHOLD)
    print(f"Precision@{config.TOP_K}: {avg_precision:.4f}")
    print(f"Recall@{config.TOP_K}: {avg_recall:.4f}")

from surprise import NormalPredictor

random_model = NormalPredictor()
random_model.fit(trainset)
random_predictions = random_model.test(testset)

avg_p_random, avg_r_random = average_precision_recall(random_predictions, k=10, threshold=9)
print(f"Random baseline - Precision@10: {avg_p_random:.4f}, Recall@10: {avg_r_random:.4f}")