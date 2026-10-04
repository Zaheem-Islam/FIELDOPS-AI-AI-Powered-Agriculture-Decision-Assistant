def calculate_irrigation(crop, stage, area, moisture, rainfall, forecast):
    """
    Hackathon demo calculation.
    This is a declared team rule for a controlled scenario, not an agronomic prescription.
    """
    # Demo thresholds: low moisture + limited rainfall => irrigation recommendation.
    if moisture < 250 and rainfall < 10 and forecast < 10:
        liters_per_acre = 1000
        liters = area * liters_per_acre
        return {
            "recommendation": "Recommended",
            "liters": liters,
            "method": "Controlled demo rule: low soil moisture + limited rainfall"
        }

    if moisture >= 350 or rainfall >= 20 or forecast >= 20:
        return {
            "recommendation": "No Immediate Irrigation",
            "liters": 0,
            "method": "Controlled demo rule: adequate moisture/rainfall"
        }

    liters = area * 500
    return {
        "recommendation": "Consider / Reassess",
        "liters": liters,
        "method": "Controlled demo rule: intermediate conditions"
    }
