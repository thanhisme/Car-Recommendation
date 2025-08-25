from fastapi import FastAPI
from dotenv import load_dotenv

from models.profile import Profile
from autotrader_service import AutoTraderService

# Load environment variables from a .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Initialize the service that handles car recommendations
service = AutoTraderService()

@app.post("/recommend")
def recommend_cars(profile: Profile):
    """
    Endpoint to recommend cars based on user's profile.
    """
    # Perform semantic search to find cars matching user's preferences
    semantic_result = service.semantic_search_from_profile(profile, useMock=False)

    return semantic_result
    
    # Get available finance offers for the user
    finance_result = service.get_finance_info(profile)

    # Filter cars and calculate Total Cost of Ownership (TCO) based on profile, semantic search, and finance info
    filtered_cars = service.filter_cars_by_budget_and_match(profile, semantic_result, finance_result)
    cars_with_tco = service.calculate_tco_for_cars(profile, filtered_cars)

    # Return the recommendation results
    return {
        "summary": "We found cars that match your preferences, budget, and lifestyle.",
        "your_profile": {
            # Show user's location (state + zip if available)
            "location": f"{profile.state}, {getattr(profile, 'zip', '')}",
            "budget": {
                # User's cash budget and monthly capacity for financing
                "cash_budget": profile.finance.cash_budget,
                "monthly_capacity": profile.finance.monthly_capacity,
                "payment_method": profile.finance.payment_method
            },
            # Indicate if user prefers eco-friendly vehicles
            "eco_friendly": getattr(profile, 'eco_friendly', None),
            # Suggested cars from semantic search
            "preferences_from_semantic_search": semantic_result["suggested_cars"]
        },
        "finance_info": {
            # Simple human-readable message about user's payment capacity
            "payment_capacity": f"You can afford cars up to ${profile.finance.cash_budget} in cash "
                                f"or around ${profile.finance.monthly_capacity}/month if financed.",
        },
        # List of recommended cars after filtering and TCO calculation
        "recommended_cars": cars_with_tco,
    }
