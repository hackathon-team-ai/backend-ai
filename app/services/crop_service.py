from datetime import datetime
from typing import List
from app.schemas.crop import CropRecommendationInput, RecommendedCrop, CropRecommendationResponse

CROP_DATABASE = [
    {
        "crop_name": "Paddy / Rice (High Yield Hybrid)",
        "category": "Cereals",
        "suitable_seasons": ["Kharif"],
        "suitable_soils": ["Alluvial", "Clay", "Loamy"],
        "water_req": "High",
        "duration_days": 120,
        "est_cost_per_acre": 22000.0,
        "yield_per_acre": "25 - 30 Quintals",
        "price_per_quintal": 2200.0,
        "advantages": ["High government MSP support", "Assured market demand", "Excellent yield stability"],
        "market_demand": "Very High"
    },
    {
        "crop_name": "Soybean (JS 335 / JS 9560)",
        "category": "Oilseeds",
        "suitable_seasons": ["Kharif"],
        "suitable_soils": ["Black", "Loamy"],
        "water_req": "Medium",
        "duration_days": 95,
        "est_cost_per_acre": 14500.0,
        "yield_per_acre": "10 - 12 Quintals",
        "price_per_quintal": 4800.0,
        "advantages": ["Enriches soil nitrogen naturally", "Short crop duration", "Low water consumption"],
        "market_demand": "High"
    },
    {
        "crop_name": "Bt Cotton (Bollgard II)",
        "category": "Cash Crops",
        "suitable_seasons": ["Kharif"],
        "suitable_soils": ["Black", "Deep Alluvial"],
        "water_req": "Medium",
        "duration_days": 160,
        "est_cost_per_acre": 28000.0,
        "yield_per_acre": "12 - 15 Quintals",
        "price_per_quintal": 7200.0,
        "advantages": ["High profit margin per acre", "Resistance to bollworms", "Extensive industrial demand"],
        "market_demand": "High"
    },
    {
        "crop_name": "Chickpea / Bengal Gram (Kabuli)",
        "category": "Pulses",
        "suitable_seasons": ["Rabi"],
        "suitable_soils": ["Black", "Sandy", "Loamy"],
        "water_req": "Rainfed / Low",
        "duration_days": 110,
        "est_cost_per_acre": 12000.0,
        "yield_per_acre": "8 - 10 Quintals",
        "price_per_quintal": 5600.0,
        "advantages": ["Minimal irrigation requirement", "High pulse market prices", "Improves soil health"],
        "market_demand": "High"
    },
    {
        "crop_name": "Wheat (HD 2967 / PBW 550)",
        "category": "Cereals",
        "suitable_seasons": ["Rabi"],
        "suitable_soils": ["Alluvial", "Clay", "Loamy"],
        "water_req": "Medium",
        "duration_days": 135,
        "est_cost_per_acre": 18000.0,
        "yield_per_acre": "20 - 24 Quintals",
        "price_per_quintal": 2275.0,
        "advantages": ["Staple food crop with guaranteed MSP purchase", "Stover used as livestock fodder"],
        "market_demand": "Very High"
    },
    {
        "crop_name": "Maize / Corn (Pioneer Hybrid)",
        "category": "Cereals / Fodder",
        "suitable_seasons": ["Kharif", "Rabi", "Zaid"],
        "suitable_soils": ["Alluvial", "Red", "Loamy"],
        "water_req": "Medium",
        "duration_days": 100,
        "est_cost_per_acre": 16000.0,
        "yield_per_acre": "22 - 26 Quintals",
        "price_per_quintal": 2090.0,
        "advantages": ["Poultry feed industrial demand", "Multiple cropping seasons possible", "Fast growth cycle"],
        "market_demand": "High"
    },
    {
        "crop_name": "Red Gram / Tur (Arhar)",
        "category": "Pulses",
        "suitable_seasons": ["Kharif"],
        "suitable_soils": ["Black", "Red", "Loamy"],
        "water_req": "Rainfed / Low",
        "duration_days": 170,
        "est_cost_per_acre": 13500.0,
        "yield_per_acre": "7 - 9 Quintals",
        "price_per_quintal": 7000.0,
        "advantages": ["Drought resistant", "Premium market prices", "Inter-cropping friendly with soybean"],
        "market_demand": "Very High"
    }
]

class CropRecommendationService:
    def recommend_crops(self, req: CropRecommendationInput) -> CropRecommendationResponse:
        scored_crops = []
        
        for crop in CROP_DATABASE:
            score = 70.0
            
            # Season match
            if req.season in crop["suitable_seasons"] or "Year-round" in crop["suitable_seasons"]:
                score += 15.0
            
            # Soil match
            if req.soil_type in crop["suitable_soils"]:
                score += 10.0
                
            # Water availability match
            if req.water_availability == crop["water_req"]:
                score += 5.0

            # Calculate financial metrics
            total_cost = crop["est_cost_per_acre"] * req.farm_size_acres
            
            # Calculate yield upper bound estimation
            yield_qty = float(crop["yield_per_acre"].split("-")[1].split()[0])
            est_revenue_per_acre = yield_qty * crop["price_per_quintal"]
            est_profit_per_acre = est_revenue_per_acre - crop["est_cost_per_acre"]

            scored_crops.append((score, crop, est_profit_per_acre))

        # Sort by score and profit
        scored_crops.sort(key=lambda x: (x[0], x[2]), reverse=True)

        top_5 = []
        for idx, (score, crop, profit) in enumerate(scored_crops[:5]):
            top_5.append(RecommendedCrop(
                rank=idx + 1,
                crop_name=crop["crop_name"],
                category=crop["category"],
                suitability_score=min(99.0, round(score, 1)),
                duration_days=crop["duration_days"],
                est_cost_per_acre=crop["est_cost_per_acre"],
                expected_yield_per_acre=crop["yield_per_acre"],
                est_profit_per_acre=round(profit, 2),
                key_advantages=crop["advantages"],
                water_requirement=crop["water_req"],
                market_demand=crop["market_demand"]
            ))

        return CropRecommendationResponse(
            input_summary=req,
            top_crops=top_5,
            generated_at=datetime.utcnow()
        )

crop_service = CropRecommendationService()
