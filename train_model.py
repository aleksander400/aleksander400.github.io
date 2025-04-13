import json
import numpy as np
from sklearn.model_selection import train_test_split
from ml_model import AdvancedMalwareDetector

def load_data():
    """Ładowanie danych do treningu"""
    with open('training_data.json', 'r') as f:
        data = json.load(f)
    X = []
    y = []
    
    for item in data:
        features = item['features']
        label = item['label']
        X.append(features)
        y.append(label)
    
    return np.array(X), np.array(y)

def train_model(model_type='random_forest'):
    """
    Trenuje model z możliwością wyboru typu
    :param model_type: 'random_forest', 'gradient_boost' lub 'neural_net'
    """
    X, y = load_data()
    
    # Podział danych
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Inicjalizacja i trenowanie modelu
    detector = AdvancedMalwareDetector(model_type=model_type)
    detector.train_model(X_train, y_train)
    
    # Ewaluacja na zbiorze testowym
    print("\nWyniki na zbiorze testowym:")
    detector.evaluate_model(X_test, y_test)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default='random_forest',
                       choices=['random_forest', 'gradient_boost', 'neural_net'],
                       help='Typ modelu do trenowania')
    args = parser.parse_args()
    
    train_model(model_type=args.model)
