from datetime import datetime
from typing import List
from app.schemas.crop import CropRecommendationInput, RecommendedCrop, CropRecommendationResponse

CROP_DATABASE = [
    # ── KHARIF CEREALS ──────────────────────────────────────────────────────────
    {
        "crop_name": "Paddy / Rice (Swarna Sub1)",
        "category": "Cereals",
        "suitable_seasons": ["Kharif"],
        "suitable_soils": ["Alluvial", "Clay", "Loamy"],
        "water_req": "High",
        "duration_days": 125,
        "est_cost_per_acre": 23000.0,
        "yield_per_acre": "26 - 32 Quintals",
        "price_per_quintal": 2300.0,
        "advantages": ["Flood-tolerant variety", "High MSP guaranteed", "Strong demand in Maharashtra APMC"],
        "market_demand": "Very High"
    },
    {
        "crop_name": "Sorghum / Jowar (CSV 216R)",
        "category": "Cereals",
        "suitable_seasons": ["Kharif", "Rabi"],
        "suitable_soils": ["Black", "Red", "Loamy"],
        "water_req": "Rainfed / Low",
        "duration_days": 105,
        "est_cost_per_acre": 9500.0,
        "yield_per_acre": "14 - 18 Quintals",
        "price_per_quintal": 3180.0,
        "advantages": ["Drought hardy", "Dual purpose grain + fodder", "Low input cost"],
        "market_demand": "High"
    },
    {
        "crop_name": "Pearl Millet / Bajra (HHB 67)",
        "category": "Cereals",
        "suitable_seasons": ["Kharif"],
        "suitable_soils": ["Sandy", "Red", "Loamy"],
        "water_req": "Rainfed / Low",
        "duration_days": 80,
        "est_cost_per_acre": 7500.0,
        "yield_per_acre": "12 - 16 Quintals",
        "price_per_quintal": 2500.0,
        "advantages": ["Fastest growing cereal", "Thrives in low-rainfall areas", "Ready market in poultry sector"],
        "market_demand": "High"
    },
    {
        "crop_name": "Maize / Corn (DKC 9144 Hybrid)",
        "category": "Cereals",
        "suitable_seasons": ["Kharif", "Rabi", "Zaid"],
        "suitable_soils": ["Alluvial", "Red", "Loamy"],
        "water_req": "Medium",
        "duration_days": 95,
        "est_cost_per_acre": 16000.0,
        "yield_per_acre": "24 - 30 Quintals",
        "price_per_quintal": 2090.0,
        "advantages": ["Poultry & starch industry demand", "Triple season crop", "Fast turnover"],
        "market_demand": "High"
    },
    # ── RABI CEREALS ────────────────────────────────────────────────────────────
    {
        "crop_name": "Wheat (GW 322 / HD 3086)",
        "category": "Cereals",
        "suitable_seasons": ["Rabi"],
        "suitable_soils": ["Alluvial", "Clay", "Loamy"],
        "water_req": "Medium",
        "duration_days": 130,
        "est_cost_per_acre": 18000.0,
        "yield_per_acre": "20 - 25 Quintals",
        "price_per_quintal": 2275.0,
        "advantages": ["Guaranteed MSP procurement", "Stover doubles as cattle fodder", "Stable price every year"],
        "market_demand": "Very High"
    },
    {
        "crop_name": "Barley (K 572 / RD 2786)",
        "category": "Cereals",
        "suitable_seasons": ["Rabi"],
        "suitable_soils": ["Sandy", "Loamy", "Alluvial"],
        "water_req": "Rainfed / Low",
        "duration_days": 110,
        "est_cost_per_acre": 10000.0,
        "yield_per_acre": "14 - 18 Quintals",
        "price_per_quintal": 1800.0,
        "advantages": ["Low irrigation demand", "Malt brewery & animal feed demand", "Cold tolerant"],
        "market_demand": "Medium"
    },
    # ── OILSEEDS ─────────────────────────────────────────────────────────────────
    {
        "crop_name": "Soybean (MAUS 162 / NRC 37)",
        "category": "Oilseeds",
        "suitable_seasons": ["Kharif"],
        "suitable_soils": ["Black", "Loamy"],
        "water_req": "Medium",
        "duration_days": 95,
        "est_cost_per_acre": 14500.0,
        "yield_per_acre": "10 - 14 Quintals",
        "price_per_quintal": 4800.0,
        "advantages": ["Nitrogen fixing — improves soil fertility", "Short season crop", "Strong export demand"],
        "market_demand": "High"
    },
    {
        "crop_name": "Groundnut / Peanut (TAG 24 Bold)",
        "category": "Oilseeds",
        "suitable_seasons": ["Kharif", "Rabi"],
        "suitable_soils": ["Sandy", "Red", "Loamy"],
        "water_req": "Medium",
        "duration_days": 115,
        "est_cost_per_acre": 17000.0,
        "yield_per_acre": "10 - 14 Quintals",
        "price_per_quintal": 5850.0,
        "advantages": ["High oil content fetches premium price", "Haulm used as nutritious fodder", "Suitable for light soils"],
        "market_demand": "High"
    },
    {
        "crop_name": "Sunflower (KBSH 44 Hybrid)",
        "category": "Oilseeds",
        "suitable_seasons": ["Rabi", "Zaid"],
        "suitable_soils": ["Black", "Alluvial", "Loamy"],
        "water_req": "Medium",
        "duration_days": 95,
        "est_cost_per_acre": 13000.0,
        "yield_per_acre": "6 - 10 Quintals",
        "price_per_quintal": 6400.0,
        "advantages": ["Short duration Rabi/Zaid option", "Premium edible oil market", "Bee-friendly for pollination income"],
        "market_demand": "High"
    },
    {
        "crop_name": "Sesame / Til (GT 10)",
        "category": "Oilseeds",
        "suitable_seasons": ["Kharif", "Zaid"],
        "suitable_soils": ["Sandy", "Red", "Loamy"],
        "water_req": "Rainfed / Low",
        "duration_days": 80,
        "est_cost_per_acre": 8000.0,
        "yield_per_acre": "3 - 5 Quintals",
        "price_per_quintal": 15000.0,
        "advantages": ["Premium export price", "Very low water requirement", "Lightweight crop management"],
        "market_demand": "High"
    },
    # ── PULSES ────────────────────────────────────────────────────────────────────
    {
        "crop_name": "Red Gram / Tur (BSMR 736)",
        "category": "Pulses",
        "suitable_seasons": ["Kharif"],
        "suitable_soils": ["Black", "Red", "Loamy"],
        "water_req": "Rainfed / Low",
        "duration_days": 165,
        "est_cost_per_acre": 13500.0,
        "yield_per_acre": "7 - 10 Quintals",
        "price_per_quintal": 7000.0,
        "advantages": ["Drought resistant deep roots", "Very high MSP & market price", "Intercropping with soybean"],
        "market_demand": "Very High"
    },
    {
        "crop_name": "Chickpea / Bengal Gram (Virat Kabuli)",
        "category": "Pulses",
        "suitable_seasons": ["Rabi"],
        "suitable_soils": ["Black", "Sandy", "Loamy"],
        "water_req": "Rainfed / Low",
        "duration_days": 110,
        "est_cost_per_acre": 12000.0,
        "yield_per_acre": "8 - 12 Quintals",
        "price_per_quintal": 5800.0,
        "advantages": ["Zero irrigation after sowing", "Premium Kabuli export market", "Fixes atmospheric nitrogen"],
        "market_demand": "High"
    },
    {
        "crop_name": "Green Gram / Moong (Pusa Vishal)",
        "category": "Pulses",
        "suitable_seasons": ["Kharif", "Zaid"],
        "suitable_soils": ["Loamy", "Sandy", "Alluvial"],
        "water_req": "Rainfed / Low",
        "duration_days": 65,
        "est_cost_per_acre": 9000.0,
        "yield_per_acre": "5 - 7 Quintals",
        "price_per_quintal": 7755.0,
        "advantages": ["Fastest pulse crop (65 days)", "Good Zaid filler crop", "High protein MSP supported"],
        "market_demand": "High"
    },
    {
        "crop_name": "Black Gram / Urad (LBG 752)",
        "category": "Pulses",
        "suitable_seasons": ["Kharif", "Rabi"],
        "suitable_soils": ["Black", "Loamy", "Alluvial"],
        "water_req": "Rainfed / Low",
        "duration_days": 75,
        "est_cost_per_acre": 9500.0,
        "yield_per_acre": "5 - 8 Quintals",
        "price_per_quintal": 6950.0,
        "advantages": ["High demand in dal milling", "Two season option", "Short crop with quick returns"],
        "market_demand": "High"
    },
    {
        "crop_name": "Lentil / Masoor (Pant L 406)",
        "category": "Pulses",
        "suitable_seasons": ["Rabi"],
        "suitable_soils": ["Loamy", "Clay", "Alluvial"],
        "water_req": "Rainfed / Low",
        "duration_days": 120,
        "est_cost_per_acre": 10500.0,
        "yield_per_acre": "6 - 9 Quintals",
        "price_per_quintal": 6000.0,
        "advantages": ["Low-cost Rabi pulse", "Popular in urban retail market", "Cold tolerant"],
        "market_demand": "Medium"
    },
    # ── CASH CROPS ────────────────────────────────────────────────────────────────
    {
        "crop_name": "Bt Cotton (Ajeet 155 BG II)",
        "category": "Cash Crops",
        "suitable_seasons": ["Kharif"],
        "suitable_soils": ["Black", "Deep Alluvial"],
        "water_req": "Medium",
        "duration_days": 160,
        "est_cost_per_acre": 28000.0,
        "yield_per_acre": "13 - 18 Quintals",
        "price_per_quintal": 7200.0,
        "advantages": ["Highest profit cash crop in Vidarbha", "Bollworm resistant BG II", "Textile industry guaranteed offtake"],
        "market_demand": "High"
    },
    {
        "crop_name": "Sugarcane (CoM 0265 / Co 86032)",
        "category": "Cash Crops",
        "suitable_seasons": ["Year-round"],
        "suitable_soils": ["Alluvial", "Loamy", "Black"],
        "water_req": "High",
        "duration_days": 365,
        "est_cost_per_acre": 55000.0,
        "yield_per_acre": "350 - 450 Quintals",
        "price_per_quintal": 340.0,
        "advantages": ["Guaranteed factory purchase (FRP)", "Ratoon crop reduces replanting cost", "Maharashtra sugar belt premium"],
        "market_demand": "Very High"
    },
    {
        "crop_name": "Turmeric (Rajapuri / Selam)",
        "category": "Spices & Cash Crops",
        "suitable_seasons": ["Kharif"],
        "suitable_soils": ["Loamy", "Black", "Alluvial"],
        "water_req": "Medium",
        "duration_days": 270,
        "est_cost_per_acre": 40000.0,
        "yield_per_acre": "60 - 80 Quintals",
        "price_per_quintal": 9000.0,
        "advantages": ["Premium Sangli mandi price", "Medicinal & export demand", "Rhizome gives very high profit"],
        "market_demand": "Very High"
    },
    {
        "crop_name": "Onion (Phule Samarth / Nasik Red)",
        "category": "Vegetables / Cash Crops",
        "suitable_seasons": ["Rabi", "Kharif"],
        "suitable_soils": ["Loamy", "Sandy", "Alluvial"],
        "water_req": "Medium",
        "duration_days": 120,
        "est_cost_per_acre": 30000.0,
        "yield_per_acre": "80 - 120 Quintals",
        "price_per_quintal": 1500.0,
        "advantages": ["Maharashtra is top onion state", "Strong export to Middle East", "Short season high return"],
        "market_demand": "Very High"
    },
    {
        "crop_name": "Pomegranate (Bhagwa / Sinduri)",
        "category": "Horticulture",
        "suitable_seasons": ["Year-round"],
        "suitable_soils": ["Black", "Sandy", "Loamy"],
        "water_req": "Medium",
        "duration_days": 180,
        "est_cost_per_acre": 60000.0,
        "yield_per_acre": "40 - 60 Quintals",
        "price_per_quintal": 8000.0,
        "advantages": ["Premium export quality fruit", "10+ years productive orchard", "Maharashtra Bhagwa globally recognised"],
        "market_demand": "Very High"
    },
    # ── VEGETABLES ────────────────────────────────────────────────────────────────
    {
        "crop_name": "Tomato (Arka Rakshak Hybrid)",
        "category": "Vegetables",
        "suitable_seasons": ["Kharif", "Rabi"],
        "suitable_soils": ["Loamy", "Sandy", "Alluvial"],
        "water_req": "Medium",
        "duration_days": 90,
        "est_cost_per_acre": 28000.0,
        "yield_per_acre": "120 - 180 Quintals",
        "price_per_quintal": 800.0,
        "advantages": ["High yield per acre", "Urban market proximity advantage", "Short season quick cash"],
        "market_demand": "High"
    },
    {
        "crop_name": "Chilli (Pusa Jwala / LCA 306)",
        "category": "Vegetables / Spices",
        "suitable_seasons": ["Kharif", "Rabi"],
        "suitable_soils": ["Black", "Loamy", "Sandy"],
        "water_req": "Medium",
        "duration_days": 150,
        "est_cost_per_acre": 25000.0,
        "yield_per_acre": "20 - 30 Quintals (dry)",
        "price_per_quintal": 12000.0,
        "advantages": ["Very high price for dry chilli", "Guntur & Kolhapur mandi premium", "Spice export demand"],
        "market_demand": "Very High"
    },
    {
        "crop_name": "Soybean + Tur Intercrop",
        "category": "Intercropping System",
        "suitable_seasons": ["Kharif"],
        "suitable_soils": ["Black", "Loamy"],
        "water_req": "Rainfed / Low",
        "duration_days": 165,
        "est_cost_per_acre": 16000.0,
        "yield_per_acre": "8-10 Qt Soybean + 4-5 Qt Tur",
        "price_per_quintal": 5900.0,
        "advantages": ["Risk diversification across two crops", "Maximises black soil productivity", "Recommended by ICAR for Marathwada"],
        "market_demand": "High"
    },
    {
        "crop_name": "Safflower (PBNS 12 / Bhima)",
        "category": "Oilseeds",
        "suitable_seasons": ["Rabi"],
        "suitable_soils": ["Black", "Clay", "Loamy"],
        "water_req": "Rainfed / Low",
        "duration_days": 140,
        "est_cost_per_acre": 10000.0,
        "yield_per_acre": "5 - 8 Quintals",
        "price_per_quintal": 5800.0,
        "advantages": ["Zero irrigation Rabi crop", "Ideal for deep black soil of Marathwada", "Oil + petals both marketable"],
        "market_demand": "Medium"
    },
    {
        "crop_name": "Banana (Grand Naine / G9)",
        "category": "Horticulture",
        "suitable_seasons": ["Year-round"],
        "suitable_soils": ["Alluvial", "Loamy", "Black"],
        "water_req": "High",
        "duration_days": 365,
        "est_cost_per_acre": 70000.0,
        "yield_per_acre": "200 - 280 Quintals",
        "price_per_quintal": 1500.0,
        "advantages": ["Year-round income stream", "Jalgaon district premium variety", "Stem & leaves have additional market"],
        "market_demand": "Very High"
    },
    {
        "crop_name": "Linseed / Flaxseed (Gaurav)",
        "category": "Oilseeds",
        "suitable_seasons": ["Rabi"],
        "suitable_soils": ["Clay", "Black", "Loamy"],
        "water_req": "Rainfed / Low",
        "duration_days": 115,
        "est_cost_per_acre": 8500.0,
        "yield_per_acre": "4 - 6 Quintals",
        "price_per_quintal": 6000.0,
        "advantages": ["Low cost Rabi oilseed", "Omega-3 health food export market", "Ideal for heavy black soils"],
        "market_demand": "Medium"
    },
]


class CropRecommendationService:
    def recommend_crops(self, req: CropRecommendationInput) -> CropRecommendationResponse:
        scored_crops = []

        for crop in CROP_DATABASE:
            score = 50.0  # base

            # Season match — strong weight
            if req.season in crop["suitable_seasons"]:
                score += 25.0
            elif "Year-round" in crop["suitable_seasons"]:
                score += 15.0

            # Soil type match — strong weight
            if req.soil_type in crop["suitable_soils"]:
                score += 20.0

            # Water availability match
            if req.water_availability == crop["water_req"]:
                score += 10.0
            elif req.water_availability == "High" and crop["water_req"] == "Medium":
                score += 5.0  # High water can satisfy medium need too
            elif req.water_availability == "Medium" and crop["water_req"] == "Rainfed / Low":
                score += 3.0

            # Budget feasibility — penalise if cost per acre exceeds budget / farm size
            budget_per_acre = req.budget / max(req.farm_size_acres, 0.5)
            if crop["est_cost_per_acre"] <= budget_per_acre:
                score += 10.0
            elif crop["est_cost_per_acre"] <= budget_per_acre * 1.2:
                score += 4.0   # slightly over budget, partial credit
            else:
                score -= 15.0  # well over budget — penalise hard

            # Financial attractiveness — normalised profit score
            try:
                yield_high = float(crop["yield_per_acre"].split("-")[1].split()[0])
            except Exception:
                yield_high = 10.0
            profit = yield_high * crop["price_per_quintal"] - crop["est_cost_per_acre"]
            # Add up to 10 points based on profit tier
            if profit > 60000:
                score += 10.0
            elif profit > 40000:
                score += 7.0
            elif profit > 20000:
                score += 4.0
            elif profit > 0:
                score += 2.0

            # Market demand bonus
            demand_bonus = {"Very High": 5.0, "High": 3.0, "Medium": 1.0}
            score += demand_bonus.get(crop["market_demand"], 0)

            # Small jitter so equal-scoring crops rotate across different inputs
            # Based on district name hash so results are stable per district but vary across districts
            jitter = (hash(req.district + crop["crop_name"]) % 100) / 200.0  # 0–0.5
            score += jitter

            scored_crops.append((score, crop, profit))

        # Sort by score descending
        scored_crops.sort(key=lambda x: x[0], reverse=True)

        top_crops = []
        for idx, (score, crop, profit) in enumerate(scored_crops[:5]):
            top_crops.append(RecommendedCrop(
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
            top_crops=top_crops,
            generated_at=datetime.utcnow()
        )


crop_service = CropRecommendationService()
