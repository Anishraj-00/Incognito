import numpy as np

def estimate_confidence(model, X, predicted_value):
    """
    Estimates prediction confidence using the variance of predictions
    from individual trees in a Random Forest.
    """
    if not hasattr(model, 'estimators_'):
        return 50.0, 0.0 # Default fallback if not a random forest
        
    # Get predictions from all trees
    # X needs to be a 2D array, so if it's a pandas series, reshape it
    if hasattr(X, 'values'):
        X_arr = X.values.reshape(1, -1)
    else:
        X_arr = np.array(X).reshape(1, -1)
        
    tree_preds = []
    for tree in model.estimators_:
        tree_preds.append(tree.predict(X_arr)[0])
        
    std_dev = np.std(tree_preds)
    
    # Heuristic for confidence: 
    # High standard deviation relative to prediction -> lower confidence
    # Assuming standard deviation / prediction > 0.3 is very uncertain (0%)
    
    if predicted_value == 0:
        cv = 0 # Coefficient of variation
    else:
        cv = std_dev / predicted_value
        
    # Map cv to a confidence score 0-100
    # cv = 0 -> 100% confidence
    # cv = 0.25 -> 0% confidence
    confidence = max(0, min(100, 100 * (1 - (cv / 0.25))))
    
    return float(confidence), float(std_dev)
