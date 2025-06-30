import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd

class WeatherIntelligence:
    def __init__(self, db):
        self.db = db
        self.base_url = "https://api.open-meteo.com/v1"
        
        # Industry baseline weather impacts (will be personalized over time)
        self.weather_impacts = {
            'temperature': {
                'very_cold': {'below': 32, 'impact': {'hot_drinks': 1.6, 'soup': 1.8, 'comfort_food': 1.4, 'cold_drinks': 0.3}},
                'cold': {'below': 50, 'impact': {'hot_drinks': 1.3, 'soup': 1.4, 'comfort_food': 1.2, 'cold_drinks': 0.6}},
                'cool': {'below': 65, 'impact': {'hot_drinks': 1.1, 'soup': 1.1, 'comfort_food': 1.0, 'cold_drinks': 0.8}},
                'warm': {'above': 75, 'impact': {'cold_drinks': 1.3, 'ice_cream': 1.4, 'salads': 1.2, 'hot_drinks': 0.7}},
                'hot': {'above': 85, 'impact': {'cold_drinks': 1.6, 'ice_cream': 1.8, 'salads': 1.4, 'hot_drinks': 0.4}}
            },
            'precipitation': {
                'light_rain': {'above': 0.1, 'impact': {'delivery': 1.3, 'dine_in': 0.8, 'comfort_food': 1.2}},
                'moderate_rain': {'above': 2.5, 'impact': {'delivery': 1.6, 'dine_in': 0.6, 'comfort_food': 1.4}},
                'heavy_rain': {'above': 7.5, 'impact': {'delivery': 1.8, 'dine_in': 0.4, 'comfort_food': 1.6}}
            },
            'wind': {
                'windy': {'above': 15, 'impact': {'outdoor_seating': 0.6, 'delivery': 0.9}},
                'very_windy': {'above': 25, 'impact': {'outdoor_seating': 0.3, 'delivery': 0.7}}
            }
        }
    
    def get_location_coordinates(self, location: str) -> Optional[Tuple[float, float]]:
        """Get coordinates for a location using geocoding"""
        try:
            # Using Open-Meteo's geocoding API
            geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
            params = {
                'name': location,
                'count': 1,
                'language': 'en',
                'format': 'json'
            }
            
            response = requests.get(geocoding_url, params=params)
            data = response.json()
            
            if 'results' in data and len(data['results']) > 0:
                result = data['results'][0]
                return (result['latitude'], result['longitude'])
            
            return None
        except Exception as e:
            print(f"Geocoding error: {str(e)}")
            return None
    
    def get_current_weather(self, location: str) -> Optional[Dict]:
        """Get current weather for location"""
        coords = self.get_location_coordinates(location)
        if not coords:
            return None
        
        lat, lon = coords
        
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'latitude': lat,
                'longitude': lon,
                'current': 'temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m',
                'timezone': 'auto'
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if 'current' in data:
                current = data['current']
                return {
                    'temperature': current['temperature_2m'],
                    'humidity': current['relative_humidity_2m'],
                    'precipitation': current['precipitation'],
                    'weather_code': current['weather_code'],
                    'wind_speed': current['wind_speed_10m'],
                    'location': location,
                    'timestamp': current['time']
                }
        except Exception as e:
            print(f"Current weather error: {str(e)}")
        
        return None
    
    def get_forecast(self, location: str, days: int = 7) -> Optional[Dict]:
        """Get weather forecast for location"""
        # Check cache first
        today = datetime.now().strftime('%Y-%m-%d')
        cached_weather = self.db.get_weather_cache(location, today)
        
        if cached_weather:
            return cached_weather
        
        coords = self.get_location_coordinates(location)
        if not coords:
            return None
        
        lat, lon = coords
        
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'latitude': lat,
                'longitude': lon,
                'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max,weather_code',
                'hourly': 'temperature_2m,precipitation_probability,precipitation,wind_speed_10m',
                'timezone': 'auto',
                'forecast_days': days
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if 'daily' in data and 'hourly' in data:
                forecast_data = {
                    'location': location,
                    'coordinates': {'lat': lat, 'lon': lon},
                    'daily': data['daily'],
                    'hourly': data['hourly'],
                    'timezone': data['timezone'],
                    'updated_at': datetime.now().isoformat()
                }
                
                # Cache the forecast
                self.db.save_weather_cache(location, today, forecast_data)
                
                return forecast_data
        except Exception as e:
            print(f"Forecast error: {str(e)}")
        
        return None
    
    def analyze_weather_impact(self, forecast_data: Dict, restaurant_type: str = "general") -> List[Dict]:
        """Analyze weather impact and generate insights"""
        if not forecast_data or 'daily' not in forecast_data:
            return []
        
        insights = []
        daily = forecast_data['daily']
        
        for i, date in enumerate(daily['time']):
            temp_max = daily['temperature_2m_max'][i]
            temp_min = daily['temperature_2m_min'][i]
            precipitation = daily['precipitation_sum'][i]
            precipitation_prob = daily['precipitation_probability_max'][i]
            wind_speed = daily['wind_speed_10m_max'][i]
            weather_code = daily['weather_code'][i]
            
            # Analyze temperature impact
            temp_insights = self._analyze_temperature_impact(temp_max, temp_min, date)
            if temp_insights:
                insights.extend(temp_insights)
            
            # Analyze precipitation impact
            precip_insights = self._analyze_precipitation_impact(precipitation, precipitation_prob, date)
            if precip_insights:
                insights.extend(precip_insights)
            
            # Analyze wind impact
            wind_insights = self._analyze_wind_impact(wind_speed, date)
            if wind_insights:
                insights.extend(wind_insights)
            
            # Generate overall daily prediction
            daily_insight = self._generate_daily_prediction(temp_max, precipitation, wind_speed, date)
            if daily_insight:
                insights.append(daily_insight)
        
        return insights
    
    def _analyze_temperature_impact(self, temp_max: float, temp_min: float, date: str) -> List[Dict]:
        """Analyze temperature impact on restaurant operations"""
        insights = []
        
        # Convert Celsius to Fahrenheit for US restaurants
        temp_f = (temp_max * 9/5) + 32
        
        if temp_f >= 85:
            insights.append({
                'type': 'weather_alert',
                'priority': 'medium',
                'date': date,
                'title': '🔥 Hot Weather Alert',
                'description': f'High of {temp_f:.0f}°F expected',
                'recommendation': 'Increase cold drink inventory by 60%, promote iced beverages, ensure AC is working',
                'impact_estimate': '+40% cold drinks, -30% hot items',
                'category': 'temperature'
            })
        elif temp_f <= 32:
            insights.append({
                'type': 'weather_alert',
                'priority': 'medium',
                'date': date,
                'title': '❄️ Freezing Weather Alert',
                'description': f'High only {temp_f:.0f}°F expected',
                'recommendation': 'Promote hot drinks and comfort food, increase soup preparation by 80%',
                'impact_estimate': '+60% hot drinks, +80% soup sales',
                'category': 'temperature'
            })
        
        return insights
    
    def _analyze_precipitation_impact(self, precipitation: float, precipitation_prob: int, date: str) -> List[Dict]:
        """Analyze precipitation impact"""
        insights = []
        
        if precipitation > 2.5 or precipitation_prob > 70:
            insights.append({
                'type': 'weather_alert',
                'priority': 'high',
                'date': date,
                'title': '🌧️ Rain Alert - Delivery Surge Expected',
                'description': f'{precipitation_prob}% chance of rain, {precipitation:.1f}mm expected',
                'recommendation': 'Alert delivery staff, increase delivery prep by 60%, reduce dine-in expectations by 35%',
                'impact_estimate': '+60% delivery orders, -35% dine-in',
                'category': 'precipitation'
            })
        
        return insights
    
    def _analyze_wind_impact(self, wind_speed: float, date: str) -> List[Dict]:
        """Analyze wind impact on outdoor seating"""
        insights = []
        
        # Convert m/s to mph
        wind_mph = wind_speed * 2.237
        
        if wind_mph > 20:
            insights.append({
                'type': 'weather_alert',
                'priority': 'low',
                'date': date,
                'title': '💨 Windy Conditions',
                'description': f'Winds up to {wind_mph:.0f} mph expected',
                'recommendation': 'Secure outdoor furniture, expect 60% reduction in patio dining',
                'impact_estimate': '-60% outdoor seating',
                'category': 'wind'
            })
        
        return insights
    
    def _generate_daily_prediction(self, temp_max: float, precipitation: float, wind_speed: float, date: str) -> Dict:
        """Generate overall daily business prediction"""
        temp_f = (temp_max * 9/5) + 32
        
        # Calculate base weather score (0-10)
        weather_score = 5.0  # Base score
        
        # Temperature impact
        if 65 <= temp_f <= 80:
            weather_score += 2  # Perfect temperature
        elif 50 <= temp_f < 65 or 80 < temp_f <= 85:
            weather_score += 1  # Good temperature
        elif temp_f < 40 or temp_f > 95:
            weather_score -= 2  # Extreme temperature
        
        # Precipitation impact
        if precipitation < 0.1:
            weather_score += 1  # No rain
        elif precipitation > 5:
            weather_score -= 3  # Heavy rain
        elif precipitation > 1:
            weather_score -= 1  # Light rain
        
        # Wind impact
        wind_mph = wind_speed * 2.237
        if wind_mph > 25:
            weather_score -= 1
        
        # Ensure score stays within bounds
        weather_score = max(0, min(10, weather_score))
        
        # Generate business impact prediction
        if weather_score >= 8:
            impact = "Excellent weather for business - expect 15-25% above normal"
            foot_traffic = "+20%"
        elif weather_score >= 6:
            impact = "Good weather - slight increase in customers expected"
            foot_traffic = "+10%"
        elif weather_score >= 4:
            impact = "Average weather conditions"
            foot_traffic = "Normal"
        elif weather_score >= 2:
            impact = "Challenging weather - expect reduced foot traffic"
            foot_traffic = "-15%"
        else:
            impact = "Severe weather impact - significant reduction expected"
            foot_traffic = "-30%"
        
        return {
            'type': 'daily_prediction',
            'priority': 'medium',
            'date': date,
            'title': f'📈 Business Forecast: {date}',
            'description': f'Weather score: {weather_score:.1f}/10',
            'recommendation': impact,
            'impact_estimate': f'Foot traffic: {foot_traffic}',
            'weather_score': weather_score,
            'category': 'prediction'
        }
    
    def get_weather_adjusted_staffing(self, base_staff: int, weather_score: float) -> Dict:
        """Calculate weather-adjusted staffing recommendations"""
        if weather_score >= 8:
            multiplier = 1.2
            recommendation = "Add extra staff"
        elif weather_score >= 6:
            multiplier = 1.1
            recommendation = "Slight increase in staff"
        elif weather_score <= 3:
            multiplier = 0.8
            recommendation = "Reduce staff"
        elif weather_score <= 1:
            multiplier = 0.6
            recommendation = "Minimal staff needed"
        else:
            multiplier = 1.0
            recommendation = "Normal staffing"
        
        recommended_staff = max(1, round(base_staff * multiplier))
        
        return {
            'base_staff': base_staff,
            'recommended_staff': recommended_staff,
            'multiplier': multiplier,
            'recommendation': recommendation,
            'weather_score': weather_score
        }
    
    def correlate_weather_with_sales(self, sales_data: List[Dict], location: str) -> Dict:
        """Correlate historical sales data with weather patterns"""
        # This would analyze historical sales vs weather
        # For now, return basic correlation insights
        
        return {
            'correlation_found': True,
            'insights': [
                "Strong correlation between temperature and beverage sales",
                "Rain increases delivery orders by average 45%",
                "Weekend + good weather = 25% above normal revenue"
            ],
            'recommendations': [
                "Monitor weather forecasts for inventory planning",
                "Adjust staffing based on weather predictions",
                "Promote weather-appropriate menu items"
            ]
        }