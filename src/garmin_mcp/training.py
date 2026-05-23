"""
Training and performance functions for Garmin Connect MCP Server
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
    """Register all training-related tools with the MCP server app"""
    
    @app.tool()
    async def get_progress_summary_between_dates(
        start_date: str, end_date: str, metric: str
    ) -> str:
        """Get progress summary for a metric between dates

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            metric: Metric to get progress for (e.g., "elevationGain", "duration", "distance", "movingDuration")
        """
        try:
            summary = garmin_client.get_progress_summary_between_dates(
                start_date, end_date, metric
            )
            if not summary:
                return f"No progress summary found for {metric} between {start_date} and {end_date}."
            return summary
        except Exception as e:
            return f"Error retrieving progress summary: {str(e)}"
    
    @app.tool()
    async def get_hill_score(start_date: str, end_date: str) -> str:
        """Get hill score data between dates

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
        """
        try:
            hill_score = garmin_client.get_hill_score(start_date, end_date)
            if not hill_score:
                return f"No hill score data found between {start_date} and {end_date}."
            return hill_score
        except Exception as e:
            return f"Error retrieving hill score data: {str(e)}"
    
    @app.tool()
    async def get_endurance_score(start_date: str, end_date: str) -> str:
        """Get endurance score data between dates

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
        """
        try:
            endurance_score = garmin_client.get_endurance_score(start_date, end_date)
            if not endurance_score:
                return f"No endurance score data found between {start_date} and {end_date}."
            return endurance_score
        except Exception as e:
            return f"Error retrieving endurance score data: {str(e)}"
    
    @app.tool()
    async def get_training_effect(activity_id: int) -> str:
        """Get training effect data for a specific activity
        
        Args:
            activity_id: ID of the activity to retrieve training effect for
        """
        try:
            effect = garmin_client.get_training_effect(activity_id)
            if not effect:
                return f"No training effect data found for activity with ID {activity_id}."
            return effect
        except Exception as e:
            return f"Error retrieving training effect data: {str(e)}"
    
    @app.tool()
    async def get_max_metrics(date: str) -> str:
        """Get max metrics data (like VO2 Max and fitness age)
        
        Args:
            date: Date in YYYY-MM-DD format
        """
        try:
            metrics = garmin_client.get_max_metrics(date)
            if not metrics:
                return f"No max metrics data found for {date}."
            return metrics
        except Exception as e:
            return f"Error retrieving max metrics data: {str(e)}"
    
    @app.tool()
    async def get_hrv_data(date: str) -> str:
        """Get Heart Rate Variability (HRV) data
        
        Args:
            date: Date in YYYY-MM-DD format
        """
        try:
            hrv_data = garmin_client.get_hrv_data(date)
            if not hrv_data:
                return f"No HRV data found for {date}."
            return hrv_data
        except Exception as e:
            return f"Error retrieving HRV data: {str(e)}"
    
    @app.tool()
    async def get_fitnessage_data(date: str) -> str:
        """Get fitness age data
        
        Args:
            date: Date in YYYY-MM-DD format
        """
        try:
            fitness_age = garmin_client.get_fitnessage_data(date)
            if not fitness_age:
                return f"No fitness age data found for {date}."
            return fitness_age
        except Exception as e:
            return f"Error retrieving fitness age data: {str(e)}"
    
    @app.tool()
    async def request_reload(date: str) -> str:
        """Request reload of epoch data
        
        Args:
            date: Date in YYYY-MM-DD format
        """
        try:
            result = garmin_client.request_reload(date)
            return result
        except Exception as e:
            return f"Error requesting data reload: {str(e)}"

    @app.tool()
    async def get_cycling_ftp() -> str:
        """Get the latest cycling Functional Threshold Power (FTP) data.

        Returns the most recent cycling FTP estimate available from Garmin.
        """
        try:
            ftp_data = garmin_client.connectapi("/biometric-service/biometric/latestFunctionalThresholdPower/CYCLING")

            if not ftp_data:
                return "No cycling FTP data found"

            # API may return a list or a single object
            if isinstance(ftp_data, list):
                ftp_data = ftp_data[0] if ftp_data else {}

            curated = {
                "sport": ftp_data.get("sport"),
                "functional_threshold_power_watts": ftp_data.get(
                    "functionalThresholdPower"
                ),
                "calendar_date": ftp_data.get("calendarDate"),
                "is_stale": ftp_data.get("isStale"),
                "biometric_source_type": ftp_data.get("biometricSourceType"),
            }

            curated = {k: v for k, v in curated.items() if v is not None}

            return json.dumps(curated, indent=2)
        except Exception as e:
            return f"Error retrieving cycling FTP data: {str(e)}"

    @app.tool()
    async def get_lactate_threshold() -> str:
        """Get the latest lactate threshold data.

        Returns lactate threshold information, which is the exercise intensity at
        which lactate starts to accumulate in the blood. This is a key metric for
        endurance training. Returns the most recent speed/heart-rate threshold and,
        when available, the latest running power-to-weight figures.
        """
        try:
            speed_hr = garmin_client.connectapi("/biometric-service/biometric/latestLactateThreshold")

            power = None
            try:
                today = __import__('datetime').date.today()
                power = garmin_client.connectapi(
                    f"/biometric-service/biometric/powerToWeight/latest/{today}?sport=Running"
                )
            except Exception:
                power = None

            if not speed_hr and not power:
                return "No lactate threshold data found"

            # The latestLactateThreshold endpoint returns a list; take the first entry.
            if isinstance(speed_hr, list):
                speed_hr = speed_hr[0] if speed_hr else {}
            if isinstance(power, list):
                power = power[0] if power else {}

            speed_hr = speed_hr or {}
            power = power or {}

            curated = {
                # Speed and heart rate data
                "lactate_threshold_speed_mps": speed_hr.get("speed"),
                "lactate_threshold_heart_rate_bpm": speed_hr.get("heartRate"),
                "heart_rate_cycling_bpm": speed_hr.get("heartRateCycling"),
                "speed_hr_date": speed_hr.get("calendarDate"),
                # Power data
                "functional_threshold_power_watts": power.get("functionalThresholdPower"),
                "weight_kg": power.get("weight"),
                "power_to_weight": power.get("powerToWeight"),
                "sport": power.get("sport"),
                "power_date": power.get("calendarDate"),
                "is_stale": power.get("isStale"),
            }

            # Remove None values
            curated = {k: v for k, v in curated.items() if v is not None}

            return json.dumps(curated, indent=2)
        except Exception as e:
            return f"Error retrieving lactate threshold data: {str(e)}"

    @app.tool()
    async def get_training_load_trend(start_date: str, end_date: str) -> str:
        """Get the Performance Management Chart (CTL/ATL/TSB) over a date range.

        Returns Chronic Training Load (CTL, 42-day fitness), Acute Training Load (ATL, 7-day fatigue),
        Training Stress Balance (TSB = CTL - ATL, form/freshness), and Acute:Chronic Workload Ratio
        (ACWR) per day. Use this to assess whether the athlete is building fitness, peaking, or
        accumulating too much fatigue.

        Recommended range: 4-8 weeks. Maximum: 90 days.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
        """
        MAX_DAYS = 90
        try:
            start = datetime.date.fromisoformat(start_date)
            end = datetime.date.fromisoformat(end_date)
        except ValueError as e:
            return f"Invalid date format: {e}. Use YYYY-MM-DD."

        days = (end - start).days + 1
        if days > MAX_DAYS:
            return f"Date range too large ({days} days). Maximum is {MAX_DAYS} days."
        if days < 1:
            return "end_date must be on or after start_date."

        trend = []
        current = start
        while current <= end:
            date_str = current.isoformat()
            try:
                data = garmin_client.get_training_status(date_str)
                if data:
                    status_data = (
                        data.get("mostRecentTrainingStatus", {})
                        .get("latestTrainingStatusData", {})
                    )
                    atl_dto = status_data.get("acuteTrainingLoadDTO", {})
                    vo2_data = data.get("mostRecentVO2Max", {}).get("generic", {})
                    entry: Dict[str, Any] = {"date": date_str}
                    atl = atl_dto.get("dailyTrainingLoadAcute")
                    ctl = atl_dto.get("dailyTrainingLoadChronic")
                    acwr = atl_dto.get("dailyAcuteChronicWorkloadRatio")
                    if atl is not None:
                        entry["atl"] = round(atl, 1)
                    if ctl is not None:
                        entry["ctl"] = round(ctl, 1)
                    if atl is not None and ctl is not None:
                        entry["tsb"] = round(ctl - atl, 1)
                    if acwr is not None:
                        entry["acwr"] = round(acwr, 2)
                    acwr_status = atl_dto.get("acwrStatus")
                    if acwr_status:
                        entry["acwr_status"] = acwr_status
                    ts = status_data.get("trainingStatusDTO", {})
                    ts_label = ts.get("trainingStatusCyclingFeedbackPhrase") or ts.get("trainingStatusFeedbackPhrase")
                    if ts_label:
                        entry["training_status"] = ts_label
                    vo2 = vo2_data.get("vo2MaxValue")
                    if vo2 is not None:
                        entry["vo2_max"] = round(vo2, 1)
                    if len(entry) > 1:  # has more than just date
                        trend.append(entry)
            except Exception:
                pass  # skip days with no data
            current += datetime.timedelta(days=1)

        if not trend:
            return f"No training load data found between {start_date} and {end_date}."

        return json.dumps({
            "start_date": start_date,
            "end_date": end_date,
            "days_with_data": len(trend),
            "trend": trend,
        }, indent=2)

    @app.tool()
    async def get_hrv_trend(start_date: str, end_date: str) -> str:
        """Get HRV (Heart Rate Variability) trend over a date range.

        Returns daily HRV values and weekly rolling averages. Single-day HRV is too noisy
        to act on — use this tool to identify baseline shifts that signal accumulated fatigue
        or recovery. A drop of >10ms from the 7-day baseline warrants reducing training load.

        Recommended range: 7-21 days. Maximum: 30 days.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
        """
        MAX_DAYS = 30
        try:
            start = datetime.date.fromisoformat(start_date)
            end = datetime.date.fromisoformat(end_date)
        except ValueError as e:
            return f"Invalid date format: {e}. Use YYYY-MM-DD."

        days = (end - start).days + 1
        if days > MAX_DAYS:
            return f"Date range too large ({days} days). Maximum is {MAX_DAYS} days."
        if days < 1:
            return "end_date must be on or after start_date."

        trend = []
        current = start
        while current <= end:
            date_str = current.isoformat()
            try:
                data = garmin_client.get_hrv_data(date_str)
                if data:
                    hrv_summary = data.get("hrvSummary", {})
                    entry: Dict[str, Any] = {"date": date_str}
                    last_night = hrv_summary.get("lastNightAvg")
                    weekly_avg = hrv_summary.get("weeklyAvg")
                    status = hrv_summary.get("status")
                    feedback = hrv_summary.get("feedbackPhrase")
                    high_hrv = hrv_summary.get("lastNight5MinHigh")
                    if last_night is not None:
                        entry["last_night_avg_hrv_ms"] = round(last_night, 1)
                    if weekly_avg is not None:
                        entry["weekly_avg_hrv_ms"] = round(weekly_avg, 1)
                    if high_hrv is not None:
                        entry["last_night_5min_high_hrv_ms"] = round(high_hrv, 1)
                    if status:
                        entry["status"] = status
                    if feedback:
                        entry["feedback"] = feedback
                    if len(entry) > 1:
                        trend.append(entry)
            except Exception:
                pass
            current += datetime.timedelta(days=1)

        if not trend:
            return f"No HRV data found between {start_date} and {end_date}."

        # Compute 7-day rolling average from the collected data
        hrv_values = [e.get("last_night_avg_hrv_ms") for e in trend if e.get("last_night_avg_hrv_ms") is not None]
        rolling_avg = None
        if hrv_values:
            rolling_avg = round(sum(hrv_values) / len(hrv_values), 1)

        return json.dumps({
            "start_date": start_date,
            "end_date": end_date,
            "days_with_data": len(trend),
            "period_avg_hrv_ms": rolling_avg,
            "trend": trend,
        }, indent=2)

    @app.tool()
    async def get_vo2max_trend(start_date: str, end_date: str) -> str:
        """Get VO2 max trend over a date range.

        Returns daily VO2 max estimates from Garmin's FirstBeat algorithm. Use this to track
        whether training is producing fitness gains over weeks or months. Flat or declining
        VO2 max over 4+ weeks suggests insufficient training stimulus or overreaching.

        Note: VO2 max estimates are smoothed and update gradually — daily changes of <0.5
        are within normal noise. Focus on the 4-6 week trend direction.

        Recommended range: 4-12 weeks. Maximum: 90 days.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
        """
        MAX_DAYS = 90
        try:
            start = datetime.date.fromisoformat(start_date)
            end = datetime.date.fromisoformat(end_date)
        except ValueError as e:
            return f"Invalid date format: {e}. Use YYYY-MM-DD."

        days = (end - start).days + 1
        if days > MAX_DAYS:
            return f"Date range too large ({days} days). Maximum is {MAX_DAYS} days."
        if days < 1:
            return "end_date must be on or after start_date."

        trend = []
        last_vo2 = None
        current = start
        while current <= end:
            date_str = current.isoformat()
            try:
                data = garmin_client.get_training_status(date_str)
                if data:
                    vo2_data = data.get("mostRecentVO2Max", {}).get("generic", {})
                    vo2 = vo2_data.get("vo2MaxValue")
                    if vo2 is not None:
                        vo2_rounded = round(vo2, 1)
                        if vo2_rounded != last_vo2:  # deduplicate unchanged values
                            trend.append({"date": date_str, "vo2_max": vo2_rounded})
                            last_vo2 = vo2_rounded
            except Exception:
                pass
            current += datetime.timedelta(days=1)

        if not trend:
            return f"No VO2 max data found between {start_date} and {end_date}."

        first_vo2 = trend[0]["vo2_max"] if trend else None
        latest_vo2 = trend[-1]["vo2_max"] if trend else None
        change = round(latest_vo2 - first_vo2, 1) if (first_vo2 and latest_vo2) else None

        return json.dumps({
            "start_date": start_date,
            "end_date": end_date,
            "data_points": len(trend),
            "first_vo2_max": first_vo2,
            "latest_vo2_max": latest_vo2,
            "change": change,
            "trend": trend,
        }, indent=2)

    @app.tool()
    async def get_respiration_trend(start_date: str, end_date: str) -> str:
        """Get overnight respiration rate trend over a date range.

        Elevated resting respiration rate (compared to personal baseline) is an early
        warning sign for overreaching, illness, or poor recovery. Use this alongside HRV
        trend for a complete recovery picture.

        Recommended range: 7-21 days. Maximum: 30 days.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
        """
        MAX_DAYS = 30
        try:
            start = datetime.date.fromisoformat(start_date)
            end = datetime.date.fromisoformat(end_date)
        except ValueError as e:
            return f"Invalid date format: {e}. Use YYYY-MM-DD."

        days = (end - start).days + 1
        if days > MAX_DAYS:
            return f"Date range too large ({days} days). Maximum is {MAX_DAYS} days."
        if days < 1:
            return "end_date must be on or after start_date."

        trend = []
        current = start
        while current <= end:
            date_str = current.isoformat()
            try:
                data = garmin_client.get_respiration_data(date_str)
                if data:
                    entry: Dict[str, Any] = {"date": date_str}
                    avg_waking = data.get("avgWakingRespirationValue")
                    avg_sleep = data.get("avgSleepRespirationValue")
                    high_sleep = data.get("highestRespirationValue")
                    low_sleep = data.get("lowestRespirationValue")
                    if avg_waking is not None:
                        entry["avg_waking_breaths_per_min"] = round(avg_waking, 1)
                    if avg_sleep is not None:
                        entry["avg_sleep_breaths_per_min"] = round(avg_sleep, 1)
                    if high_sleep is not None:
                        entry["highest_breaths_per_min"] = round(high_sleep, 1)
                    if low_sleep is not None:
                        entry["lowest_breaths_per_min"] = round(low_sleep, 1)
                    if len(entry) > 1:
                        trend.append(entry)
            except Exception:
                pass
            current += datetime.timedelta(days=1)

        if not trend:
            return f"No respiration data found between {start_date} and {end_date}."

        sleep_values = [e["avg_sleep_breaths_per_min"] for e in trend if "avg_sleep_breaths_per_min" in e]
        avg_sleep_overall = round(sum(sleep_values) / len(sleep_values), 1) if sleep_values else None

        return json.dumps({
            "start_date": start_date,
            "end_date": end_date,
            "days_with_data": len(trend),
            "period_avg_sleep_breaths_per_min": avg_sleep_overall,
            "trend": trend,
        }, indent=2)

    return app