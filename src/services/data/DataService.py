import pandas as pd
import os
from typing import Dict, Any, Optional

class DataService:
    def __init__(self):
        self._cache = {}
        self._data = None

    def get_donor_data(self, filters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Récupère les données des donneurs avec filtres optionnels
        """
        if self._data is None:
            self._load_data()

        if filters:
            cache_key = str(filters)
            if cache_key in self._cache:
                return self._cache[cache_key]

            filtered_data = self._apply_filters(self._data, filters)
            self._cache[cache_key] = filtered_data
            return filtered_data

        return self._data

    def _load_data(self):
        """
        Charge les données depuis le fichier CSV
        """
        try:
            current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            file_path = os.path.join(current_dir, 'data', 'processed_data.csv')
            self._data = pd.read_csv(file_path)
            self._data['date_de_remplissage'] = pd.to_datetime(self._data['date_de_remplissage'])
            if 'si_oui_preciser_la_date_du_dernier_don' in self._data.columns:
                self._data['si_oui_preciser_la_date_du_dernier_don'] = pd.to_datetime(self._data['si_oui_preciser_la_date_du_dernier_don'])
        except Exception as e:
            print(f"Erreur lors du chargement des données : {str(e)}")
            print(f"Chemin tenté : {file_path}")
            print(f"Dossier courant : {os.getcwd()}")
            self._data = pd.DataFrame()

    def _apply_filters(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """
        Applique les filtres aux données
        """
        filtered_df = df.copy()
        
        for column, value in filters.items():
            if value is not None:
                if isinstance(value, (list, tuple)):
                    filtered_df = filtered_df[filtered_df[column].isin(value)]
                else:
                    filtered_df = filtered_df[filtered_df[column] == value]
        
        return filtered_df

    def get_summary_stats(self) -> Dict[str, Any]:
        """
        Calcule les statistiques résumées des données
        """
        if self._data is None:
            self._load_data()

        return {
            'total_donors': len(self._data),
            'avg_age': self._data['age'].mean(),
            'eligible_donors': len(self._data[self._data['eligibilite_au_don'] == 'eligible']),
            'last_donation_date': self._data['date_de_remplissage'].max()
        }

    def get_unique_professions(self) -> list:
        """
        Récupère la liste des professions uniques
        """
        if self._data is None:
            self._load_data()
        professions = self._data['profession'].dropna().unique()
        return sorted([p for p in professions if str(p).strip() != ''])

    def get_unique_values(self, column: str) -> list:
        """
        Récupère les valeurs uniques d'une colonne
        """
        if self._data is None:
            self._load_data()
        values = self._data[column].dropna().unique()
        return sorted([v for v in values if str(v).strip() != ''])
