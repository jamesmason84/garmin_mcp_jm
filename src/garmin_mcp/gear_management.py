"""
Gear management functions for Garmin Connect MCP Server
"""
import json
import datetime
from typing import Any, Dict, List, Optional, Union

# The garmin_client will be set by the main file
garmin_client = None


def configure(client):
    """Configure the module with the Garmin client instance"""
    global garmin_client
    garmin_client = client


def register_tools(app):
    """Register all gear management tools with the MCP server app"""
    
    @app.tool()
    async def get_gear(user_profile_id: str) -> str:
        """Get all gear registered with the user account
        
        Args:
            user_profile_id: User profile ID (can be obtained from get_device_last_used)
        """
        try:
            gear = garmin_client.get_gear(user_profile_id)
            if not gear:
                return "No gear found."
            return gear
        except Exception as e:
            return f"Error retrieving gear: {str(e)}"

    @app.tool()
    async def get_gear_defaults(user_profile_id: str) -> str:
        """Get default gear settings
        
        Args:
            user_profile_id: User profile ID (can be obtained from get_device_last_used)
        """
        try:
            defaults = garmin_client.get_gear_defaults(user_profile_id)
            if not defaults:
                return "No gear defaults found."
            return defaults
        except Exception as e:
            return f"Error retrieving gear defaults: {str(e)}"
    
    @app.tool()
    async def get_gear_stats(gear_uuid: str) -> str:
        """Get statistics for specific gear
        
        Args:
            gear_uuid: UUID of the gear item
        """
        try:
            stats = garmin_client.get_gear_stats(gear_uuid)
            if not stats:
                return f"No stats found for gear with UUID {gear_uuid}."
            return stats
        except Exception as e:
            return f"Error retrieving gear stats: {str(e)}"

    @app.tool()
    async def add_gear_to_activity(gear_uuid: str, activity_id: int) -> str:
        """Associate a piece of gear with an activity.

        Args:
            gear_uuid: UUID of the gear item to link
            activity_id: ID of the activity to associate the gear with
        """
        try:
            resp = garmin_client.garth.put(
                "connectapi",
                f"/gear-service/gear/link/{gear_uuid}/activity/{activity_id}",
            )
            return json.dumps(resp.json() if hasattr(resp, 'json') else resp, indent=2)
        except Exception as e:
            return f"Error adding gear to activity: {str(e)}"

    @app.tool()
    async def remove_gear_from_activity(gear_uuid: str, activity_id: int) -> str:
        """Remove a piece of gear from an activity.

        Args:
            gear_uuid: UUID of the gear item to unlink
            activity_id: ID of the activity to remove the gear from
        """
        try:
            resp = garmin_client.garth.put(
                "connectapi",
                f"/gear-service/gear/unlink/{gear_uuid}/activity/{activity_id}",
            )
            return json.dumps(resp.json() if hasattr(resp, 'json') else resp, indent=2)
        except Exception as e:
            return f"Error removing gear from activity: {str(e)}"

    return app