from fastapi import FastAPI
from dotenv import load_dotenv

from models.profile import Profile
from models.finance import Finance
from autotrader_service import AutoTraderService

# Load environment variables from a .env file (API keys, config, etc.)
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Initialize the service that handles car recommendations and TCO calculations
service = AutoTraderService()


def _recommend_with_profile(profile: Profile):
    """
    Generate vehicle recommendations based on the provided user profile.

    Args:
        profile (Profile): User profile containing preferences, finance info, and state.

    Returns:
        list[dict]: A list of recommended vehicles matching the profile.
    """
    return service.recommend_with_profile(profile)


def _build_default_profile(state: str) -> Profile:
    """
    Build a default user profile based only on the given state.

    Args:
        state (str): The U.S. state code (e.g., 'CA', 'TX').

    Returns:
        Profile: A default profile object with broad search parameters.
    """
    return service.build_default_profile(state)


def _vehicle_details_with_tco(vin: str, profile: Profile):
    """
    Fetch vehicle details and compute Total Cost of Ownership (TCO).

    Args:
        vin (str): The Vehicle Identification Number (VIN).
        profile (Profile): The user's profile containing finance and state info.

    Returns:
        dict: Vehicle details including specifications and calculated TCO.
    """
    return service.vehicle_details_with_tco(vin, profile)


@app.post("/recommend")
def recommend_vehicles(profile: Profile):
    """
    Recommend vehicles based on a user-provided profile.

    Args:
        profile (Profile): JSON body containing user profile fields:
            - state (str): User's state
            - finance (Finance): Finance info (budget, loan, etc.)
            - habit, colors, features (optional)

    Returns:
        list[dict]: A ranked list of recommended vehicles with metadata.
    """
    return _recommend_with_profile(profile)


@app.get("/recommend/default")
def recommend_vehicles_default(state: str):
    """
    Recommend vehicles using a default profile.

    The default profile:
    - Only filters by `state`
    - Sets finance fields to very high values (no budget restriction)

    Args:
        state (str): The U.S. state code to filter vehicles.

    Returns:
        list[dict]: A list of recommended vehicles for the given state.
    """
    # Build default profile with state + maximum finance capacity (broad search)
    default_profile = Profile(
        state=state,
        finance=Finance(payment_method="cash", cash_budget=10**9, monthly_capacity=10**9)
    )

    return _recommend_with_profile(default_profile)


@app.get("/vehicle/details/default/{vin}")
def get_vehicle_details_default(vin: str, state: str):
    """
    Get vehicle details and TCO by VIN using a default profile derived from state.

    Args:
        vin (str): The Vehicle Identification Number.
        state (str): The U.S. state code to apply tax/insurance rules.

    Returns:
        dict: Vehicle details enriched with TCO analysis.
    """
    profile = _build_default_profile(state)
    return _vehicle_details_with_tco(vin, profile)


@app.post("/vehicle/details")
def get_vehicle_details(vin: str, profile: Profile):
    """
    Get vehicle details and TCO by VIN using a user-provided profile.

    Args:
        vin (str): The Vehicle Identification Number.
        profile (Profile): JSON body representing user's profile.

    Returns:
        dict: Vehicle details enriched with TCO analysis.
    """
    return _vehicle_details_with_tco(vin, profile)
