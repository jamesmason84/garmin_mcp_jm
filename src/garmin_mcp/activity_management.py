"""
Activity Management functions for Garmin Connect MCP Server
"""
import datetime
import json
from typing import Any, Dict, List, Optional, Union

# The garmin_client will be set by the main file
garmin_client = None


def _to_json_str(data):
    """Convert data to JSON string if it's not already a string"""
    if isinstance(data, str):
        return data
    try:
        return json.dumps(data, indent=2, default=str)
    except (TypeError, ValueError):
        return str(data)


def configure(client):
    """Configure the module with the Garmin client instance"""
    global garmin_client
    garmin_client = client


def register_tools(app):
    """Register all activity management tools with the MCP server app"""
    
    @app.tool()
    async def get_activities_by_date(start_date: str, end_date: str, activity_type: str = "") -> str:
        """Get activities data between specified dates, optionally filtered by activity type
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            activity_type: Optional activity type filter (e.g., cycling, running, swimming)
        """
        try:
            activities = garmin_client.get_activities_by_date(start_date, end_date, activity_type)
            if not activities:
                return f"No activities found between {start_date} and {end_date}" + \
                       (f" for activity type '{activity_type}'" if activity_type else "")
            
            return _to_json_str(activities)
        except Exception as e:
            return f"Error retrieving activities by date: {str(e)}"

    @app.tool()
    async def get_activities_fordate(date: str) -> str:
        """Get activities for a specific date
        
        Args:
            date: Date in YYYY-MM-DD format
        """
        try:
            activities = garmin_client.get_activities_fordate(date)
            if not activities:
                return f"No activities found for {date}"
            
            return _to_json_str(activities)
        except Exception as e:
            return f"Error retrieving activities for date: {str(e)}"

    @app.tool()
    async def get_activity(activity_id: int) -> str:
        """Get basic activity information
        
        Args:
            activity_id: ID of the activity to retrieve
        """
        try:
            activity = garmin_client.get_activity(activity_id)
            if not activity:
                return f"No activity found with ID {activity_id}"
            
            return _to_json_str(activity)
        except Exception as e:
            return f"Error retrieving activity: {str(e)}"

    @app.tool()
    async def get_activity_splits(activity_id: int) -> str:
        """Get splits for an activity
        
        Args:
            activity_id: ID of the activity to retrieve splits for
        """
        try:
            splits = garmin_client.get_activity_splits(activity_id)
            if not splits:
                return f"No splits found for activity with ID {activity_id}"
            
            return _to_json_str(splits)
        except Exception as e:
            return f"Error retrieving activity splits: {str(e)}"

    @app.tool()
    async def get_activity_typed_splits(activity_id: int) -> str:
        """Get typed splits for an activity
        
        Args:
            activity_id: ID of the activity to retrieve typed splits for
        """
        try:
            typed_splits = garmin_client.get_activity_typed_splits(activity_id)
            if not typed_splits:
                return f"No typed splits found for activity with ID {activity_id}"
            
            return _to_json_str(typed_splits)
        except Exception as e:
            return f"Error retrieving activity typed splits: {str(e)}"

    @app.tool()
    async def get_activity_split_summaries(activity_id: int) -> str:
        """Get split summaries for an activity
        
        Args:
            activity_id: ID of the activity to retrieve split summaries for
        """
        try:
            split_summaries = garmin_client.get_activity_split_summaries(activity_id)
            if not split_summaries:
                return f"No split summaries found for activity with ID {activity_id}"
            
            return _to_json_str(split_summaries)
        except Exception as e:
            return f"Error retrieving activity split summaries: {str(e)}"

    @app.tool()
    async def get_activity_weather(activity_id: int) -> str:
        """Get weather data for an activity
        
        Args:
            activity_id: ID of the activity to retrieve weather data for
        """
        try:
            weather = garmin_client.get_activity_weather(activity_id)
            if not weather:
                return f"No weather data found for activity with ID {activity_id}"
            
            return _to_json_str(weather)
        except Exception as e:
            return f"Error retrieving activity weather data: {str(e)}"

    @app.tool()
    async def get_activity_hr_in_timezones(activity_id: int) -> str:
        """Get heart rate data in different time zones for an activity
        
        Args:
            activity_id: ID of the activity to retrieve heart rate time zone data for
        """
        try:
            hr_zones = garmin_client.get_activity_hr_in_timezones(activity_id)
            if not hr_zones:
                return f"No heart rate time zone data found for activity with ID {activity_id}"
            
            return _to_json_str(hr_zones)
        except Exception as e:
            return f"Error retrieving activity heart rate time zone data: {str(e)}"

    @app.tool()
    async def get_activity_gear(activity_id: int) -> str:
        """Get gear data used for an activity
        
        Args:
            activity_id: ID of the activity to retrieve gear data for
        """
        try:
            gear = garmin_client.get_activity_gear(activity_id)
            if not gear:
                return f"No gear data found for activity with ID {activity_id}"
            
            return _to_json_str(gear)
        except Exception as e:
            return f"Error retrieving activity gear data: {str(e)}"

    @app.tool()
    async def get_activity_exercise_sets(activity_id: int) -> str:
        """Get exercise sets for strength training activities
        
        Args:
            activity_id: ID of the activity to retrieve exercise sets for
        """
        try:
            exercise_sets = garmin_client.get_activity_exercise_sets(activity_id)
            if not exercise_sets:
                return f"No exercise sets found for activity with ID {activity_id}"
            
            return _to_json_str(exercise_sets)
        except Exception as e:
            return f"Error retrieving activity exercise sets: {str(e)}"

    @app.tool()
    async def set_activity_name(activity_id: int, activity_name: str) -> str:
        """Set or update the name of an activity.

        Args:
            activity_id: ID of the activity to update
            activity_name: New activity name
        """
        try:
            activity_name = activity_name.strip()
            if not activity_name:
                return "Activity name cannot be empty"

            garmin_client.set_activity_name(activity_id, activity_name)

            return json.dumps(
                {
                    "success": True,
                    "activity_id": activity_id,
                    "activity_name": activity_name,
                    "message": "Activity name successfully updated",
                },
                indent=2,
            )
        except Exception as e:
            return f"Error updating activity name: {str(e)}"

    @app.tool()
    async def get_activity_power_in_timezones(activity_id: int) -> str:
        """Get power distribution across training zones for an activity.

        Returns time spent in each power zone with watt thresholds and duration.
        Requires a power meter. Zones are based on the athlete's FTP configured in Garmin Connect.

        Args:
            activity_id: ID of the activity to retrieve power zone data for
        """
        try:
            power_zones = garmin_client.connectapi(f"/activity-service/activity/{activity_id}/powerTimeInZones")
            if not power_zones:
                return f"No power zone data found for activity {activity_id}. Ensure the activity was recorded with a power meter."

            return json.dumps(power_zones, indent=2)
        except Exception as e:
            return f"Error retrieving activity power zone data: {str(e)}"

    @app.tool()
    async def count_activities() -> str:
        """Get total count of activities in the user's Garmin account

        Returns the total number of activities recorded.
        """
        try:
            count = (garmin_client.connectapi("/activitylist-service/activities/count") or {}).get("totalCount")
            if count is None:
                return "Unable to retrieve activity count"

            return json.dumps({
                "total_activities": count,
                "note": "Use get_activities() with pagination to retrieve activity details"
            }, indent=2)
        except Exception as e:
            return f"Error counting activities: {str(e)}"

    @app.tool()
    async def get_activities(start: int = 0, limit: int = 20) -> str:
        """Get activities with pagination support

        Retrieves a paginated list of activities. Use this for browsing through
        large activity lists more efficiently than get_activities_by_date.

        Args:
            start: Starting index (default 0, activities are ordered newest first)
            limit: Maximum number of activities to return (default 20, max 100)
        """
        try:
            # Cap limit at 100 for safety and performance
            limit = min(max(1, limit), 100)

            activities = garmin_client.get_activities(start, limit)
            if not activities:
                return f"No activities found at index {start}"

            # Curate the activity list
            curated = {
                "start": start,
                "limit": limit,
                "count": len(activities),
                "has_more": len(activities) == limit,
                "next_start": start + limit if len(activities) == limit else None,
                "activities": []
            }

            for a in activities:
                activity = {
                    "id": a.get('activityId'),
                    "name": a.get('activityName'),
                    "type": a.get('activityType', {}).get('typeKey'),
                    "start_time": a.get('startTimeLocal'),
                    "distance_meters": a.get('distance'),
                    "duration_seconds": a.get('duration'),
                    "moving_duration_seconds": a.get('movingDuration'),
                    "calories": a.get('calories'),
                    "avg_hr_bpm": a.get('averageHR'),
                    "max_hr_bpm": a.get('maxHR'),
                    "steps": a.get('steps'),
                    "elevation_gain_meters": a.get('elevationGain'),
                    "elevation_loss_meters": a.get('elevationLoss'),
                    "owner_display_name": a.get('ownerDisplayName'),
                }
                # Remove None values
                activity = {k: v for k, v in activity.items() if v is not None}
                curated["activities"].append(activity)

            return json.dumps(curated, indent=2)
        except Exception as e:
            return f"Error retrieving activities: {str(e)}"

    @app.tool()
    async def get_activity_types() -> str:
        """Get all available activity types

        Returns a list of all activity types supported by Garmin Connect,
        useful for filtering activities by type.
        """
        try:
            activity_types = garmin_client.get_activity_types()
            if not activity_types:
                return "No activity types found"

            # Curate the activity types list
            curated = {
                "count": len(activity_types),
                "activity_types": []
            }

            for at in activity_types:
                activity_type = {
                    "type_id": at.get('typeId'),
                    "type_key": at.get('typeKey'),
                    "display_name": at.get('displayName'),
                    "parent_type_id": at.get('parentTypeId'),
                    "is_hidden": at.get('isHidden'),
                }
                # Remove None values
                activity_type = {k: v for k, v in activity_type.items() if v is not None}
                curated["activity_types"].append(activity_type)

            return json.dumps(curated, indent=2)
        except Exception as e:
            return f"Error retrieving activity types: {str(e)}"

    return app
