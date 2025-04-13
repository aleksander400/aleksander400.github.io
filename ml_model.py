import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
import warnings

class AdvancedMalwareDetector:
    def __init__(self, model_type='random_forest'):
        """
        Inicjalizacja detektora malware z możliwością wyboru typu modelu
        :param model_type: 'random_forest', 'gradient_boost' lub 'neural_net'
        """
        self.model = None
        self.model_type = model_type
        try:
            self.model = joblib.load('malware_model.pkl')
        except FileNotFoundError:
            warnings.warn("Model nie znaleziony, należy go wytrenować")
        
    def predict(self, features, return_prob=False):
        """
        Przewiduje, czy plik jest złośliwy
        :param features: lista cech pliku
        :param return_prob: czy zwrócić prawdopodobieństwo zamiast klasy
        :return: predykcja (0/1) lub prawdopodobieństwo
        """
        features = np.array(features).reshape(1, -1)
        
        if return_prob and hasattr(self.model, "predict_proba"):
            return self.model.predict_proba(features)[0][1]  # Prawdopodobieństwo klasy 1
        return self.model.predict(features)[0]

    def train_model(self, X_train, y_train, cv_folds=None):
        """
        Trenuje model z walidacją krzyżową
        :param X_train: dane treningowe
        :param y_train: etykiety
        :param cv_folds: liczba foldów do walidacji (None dla auto-dostosowania)
        """
        # Auto-dostosowanie liczby foldów dla małych zbiorów danych
        if cv_folds is None:
            class_counts = np.bincount(y_train)
            min_samples = min(class_counts) if len(class_counts) > 1 else len(y_train)
            cv_folds = min(3, min_samples)  # Maksymalnie 3 foldy dla małych zbiorów
            print(f"Auto-dostosowano liczbę foldów walidacji do: {cv_folds}")
        if self.model_type == 'random_forest':
            self.model = RandomForestClassifier(n_estimators=100, max_depth=10)
        elif self.model_type == 'gradient_boost':
            self.model = GradientBoostingClassifier(n_estimators=100)
        elif self.model_type == 'neural_net':
            self.model = MLPClassifier(hidden_layer_sizes=(50,), max_iter=500)
            
        # Walidacja krzyżowa
        scores = cross_val_score(self.model, X_train, y_train, cv=cv_folds)
        print(f"Średnia dokładność walidacji krzyżowej: {scores.mean():.2f} (+/- {scores.std():.2f})")
        
        # Trenowanie finalnego modelu
        self.model.fit(X_train, y_train)
        joblib.dump(self.model, 'malware_model.pkl')
        
        # Raport klasyfikacji
        y_pred = self.model.predict(X_train)
        print("\nRaport klasyfikacji:\n", classification_report(y_train, y_pred))
        print("\nMacierz pomyłek:\n", confusion_matrix(y_train, y_pred))

    def evaluate_model(self, X_test, y_test):
        """Ewaluacja modelu na zbiorze testowym"""
        if self.model is None:
            raise ValueError("Model nie został wytrenowany")
            
        y_pred = self.model.predict(X_test)
        print("\nWyniki ewaluacji:\n", classification_report(y_test, y_pred))
        print("\nMacierz pomyłek:\n", confusion_matrix(y_test, y_pred))
        return classification_report(y_test, y_pred, output_dict=True)

if __name__ == "__main__":
    # Przykładowe użycie
    detector = AdvancedMalwareDetector(model_type='random_forest')
    
    # Przykładowe dane
    features = [1000, 0.5, 10, 0.2]
    result = detector.predict(features, return_prob=True)
    print(f"Wynik detekcji: {result:.2f} (prawdopodobieństwo)")
