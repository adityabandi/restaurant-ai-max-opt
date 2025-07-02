import pandas as pd
from typing import Dict, List

class MenuEngineering:
    def __init__(self):
        pass

    def analyze(self, menu_items: List[Dict]) -> Dict:
        """
        Analyzes menu items and classifies them into Stars, Plow-horses, Puzzles, and Dogs.
        """
        if not menu_items:
            return {}

        df = pd.DataFrame(menu_items)
        
        # Calculate popularity and margin
        df['popularity'] = df['quantity_sold'] / df['quantity_sold'].sum()
        df['margin_per_item'] = df['unit_price'] - df['total_cost_per_item']
        
        # Calculate average popularity and margin
        avg_popularity = df['popularity'].mean()
        avg_margin = df['margin_per_item'].mean()

        # Classify items
        df['classification'] = df.apply(
            lambda row: self._classify_item(row, avg_popularity, avg_margin),
            axis=1
        )

        return df.to_dict(orient='records')

    def _classify_item(self, row: pd.Series, avg_popularity: float, avg_margin: float) -> str:
        if row['popularity'] > avg_popularity and row['margin_per_item'] > avg_margin:
            return 'Star'
        elif row['popularity'] > avg_popularity and row['margin_per_item'] <= avg_margin:
            return 'Plow-horse'
        elif row['popularity'] <= avg_popularity and row['margin_per_item'] > avg_margin:
            return 'Puzzle'
        else:
            return 'Dog'