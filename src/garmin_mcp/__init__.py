"""
Modular MCP Server for Garmin Connect Data
"""

import json
import os

import requests
from mcp.server.fastmcp import FastMCP

from garth.exc import GarthHTTPError
from garminconnect import Garmin, GarminConnectAuthenticationError


def _to_json_str(data):
    """Convert data to JSON string if it's not already a string"""
    if isinstance(data, str):
        return data
    try:
        return json.dumps(data, indent=2, default=str)
    except (TypeError, ValueError):
        return str(data)

# Import all modules
from garmin_mcp import activity_management
from garmin_mcp import health_wellness
from garmin_mcp import user_profile
from garmin_mcp import devices
from garmin_mcp import gear_management
from garmin_mcp import weight_management
from garmin_mcp import challenges
from garmin_mcp import training
from garmin_mcp import workouts
from garmin_mcp import data_management
from garmin_mcp import womens_health
from garmin_mcp import recommendations

def get_mfa() -> str:
    """Get MFA code non-interactively for container/Kubernetes environments.

    Sources (checked in order):
    - GARMIN_MFA_CODE env var
    - GARMIN_MFA_CODE_FILE pointing to a file containing the code
    - Poll for up to GARMIN_MFA_WAIT_SECONDS for either of the above to appear
    """
    print("\nGarmin Connect MFA required. Awaiting code via env or file...")

    mfa_code = os.environ.get("GARMIN_MFA_CODE")
    if mfa_code:
        return mfa_code.strip()

    mfa_file = os.environ.get("GARMIN_MFA_CODE_FILE")
    if mfa_file and os.path.exists(os.path.expanduser(mfa_file)):
        with open(os.path.expanduser(mfa_file), "r") as f:
            return f.read().strip()

    # Optional polling window to allow sidecar/secret updates
    wait_seconds = int(os.environ.get("GARMIN_MFA_WAIT_SECONDS", "0") or 0)
    if wait_seconds > 0:
        import time

        end_time = time.time() + wait_seconds
        while time.time() < end_time:
            mfa_code = os.environ.get("GARMIN_MFA_CODE")
            if mfa_code:
                return mfa_code.strip()

            mfa_file = os.environ.get("GARMIN_MFA_CODE_FILE")
            if mfa_file and os.path.exists(os.path.expanduser(mfa_file)):
                with open(os.path.expanduser(mfa_file), "r") as f:
                    return f.read().strip()

            time.sleep(1)

    raise RuntimeError(
        "MFA code required but not provided. Set GARMIN_MFA_CODE or GARMIN_MFA_CODE_FILE "
        "(optional: GARMIN_MFA_WAIT_SECONDS to poll)."
    )

# Get credentials from environment
email = os.environ.get("GARMIN_EMAIL")
password = os.environ.get("GARMIN_PASSWORD")
tokenstore = os.getenv("GARMINTOKENS") or "~/.garminconnect"
tokenstore_base64 = os.getenv("GARMINTOKENS_BASE64") or "~/.garminconnect_base64"


def init_api(email, password):
    """Initialize Garmin API with your credentials."""

    try:
        # Using Oauth1 and OAuth2 token files from directory
        print(
            f"Trying to login to Garmin Connect using token data from directory '{tokenstore}'...\n"
        )

        garmin = Garmin()
        garmin.login(tokenstore)

    except (FileNotFoundError, GarthHTTPError, GarminConnectAuthenticationError):
        # Session is expired. You'll need to log in again
        print(
            "Login tokens not present, login with your Garmin Connect credentials to generate them.\n"
            f"They will be stored in '{tokenstore}' for future use.\n"
        )
        try:
            garmin = Garmin(
                email=email, password=password, is_cn=False, prompt_mfa=get_mfa
            )
            garmin.login()
            # Save Oauth1 and Oauth2 token files to directory for next login
            garmin.garth.dump(tokenstore)
            print(
                f"Oauth tokens stored in '{tokenstore}' directory for future use. (first method)\n"
            )
            # Encode Oauth1 and Oauth2 tokens to base64 string and save to file for next login
            token_base64 = garmin.garth.dumps()
            dir_path = os.path.expanduser(tokenstore_base64)
            with open(dir_path, "w") as token_file:
                token_file.write(token_base64)
            print(
                f"Oauth tokens encoded as base64 string and saved to '{dir_path}' file for future use. (second method)\n"
            )
        except (
            FileNotFoundError,
            GarthHTTPError,
            GarminConnectAuthenticationError,
            requests.exceptions.HTTPError,
        ) as err:
            print(err)
            return None

    return garmin


def main():
    """Initialize the MCP server and register all tools"""

    # Initialize Garmin client
    garmin_client = init_api(email, password)
    if not garmin_client:
        print("Failed to initialize Garmin Connect client. Exiting.")
        return

    print("Garmin Connect client initialized successfully.")

    # Configure all modules with the Garmin client
    activity_management.configure(garmin_client)
    health_wellness.configure(garmin_client)
    user_profile.configure(garmin_client)
    devices.configure(garmin_client)
    gear_management.configure(garmin_client)
    weight_management.configure(garmin_client)
    challenges.configure(garmin_client)
    training.configure(garmin_client)
    workouts.configure(garmin_client)
    data_management.configure(garmin_client)
    womens_health.configure(garmin_client)
    recommendations.configure(garmin_client)

    # Create the MCP app
    app = FastMCP("Garmin Connect v1.0")

    # Register tools from all modules
    app = activity_management.register_tools(app)
    app = health_wellness.register_tools(app)
    app = user_profile.register_tools(app)
    app = devices.register_tools(app)
    app = gear_management.register_tools(app)
    app = weight_management.register_tools(app)
    app = challenges.register_tools(app)
    app = training.register_tools(app)
    app = workouts.register_tools(app)
    app = data_management.register_tools(app)
    app = womens_health.register_tools(app)
    app = recommendations.register_tools(app)

    # Add activity listing tool directly to the app
    @app.tool()
    async def list_activities(limit: int = 5) -> str:
        """List recent Garmin activities"""
        try:
            activities = garmin_client.get_activities(0, limit)
            if not activities:
                return "No activities found."
            return _to_json_str(activities)
        except Exception as e:
            return f"Error retrieving activities: {str(e)}"

    # Run the MCP server (Streamable HTTP by default for Railway)
    transport = os.environ.get("GARMIN_MCP_TRANSPORT", "http")
    host = os.environ.get("GARMIN_MCP_HOST", "0.0.0.0")
    port_str = os.environ.get("GARMIN_MCP_PORT", "8000")
    path = os.environ.get("GARMIN_MCP_PATH", "/")
    try:
        port = int(port_str)
    except ValueError:
        port = 8000

    if transport == "stdio":
        app.run()
        return

    print(f"Starting MCP with transport={transport}, host={host}, port={port}, path={path}")

    # --- Patch 1: Disable host validation (TransportSecurityMiddleware) ---
    # The mcp library rejects any Host header that isn't localhost/127.0.0.1,
    # which breaks Railway deployments. We replace TransportSecurityMiddleware
    # with a no-op that always allows requests through.
    try:
        import mcp.server.transport_security as _tst
        import mcp.server.streamable_http as _msh

        class _NoOpSecurity:
            """Pass-through replacement for TransportSecurityMiddleware."""
            def __init__(self, app=None, settings=None):
                self.app = app

            async def __call__(self, scope, receive, send):
                if self.app:
                    return await self.app(scope, receive, send)

            async def validate_request(self, request, is_post=False):
                # Return None = request is valid, proceed normally
                return None

        # Patch the class in both module namespaces.
        # streamable_http.py does `from mcp.server.transport_security import TransportSecurityMiddleware`
        # at import time, so we must patch its local reference too.
        _tst.TransportSecurityMiddleware = _NoOpSecurity
        _msh.TransportSecurityMiddleware = _NoOpSecurity

        # Also patch streamable_http_manager if it holds a reference
        try:
            import mcp.server.streamable_http_manager as _shm
            _shm.TransportSecurityMiddleware = _NoOpSecurity
        except Exception:
            pass

        print("[patch] TransportSecurityMiddleware replaced — host validation disabled")
    except Exception as e:
        import traceback
        print(f"[patch] TransportSecurityMiddleware patch failed: {e}")
        traceback.print_exc()

    # --- Patch 2: Force uvicorn to bind on 0.0.0.0 ---
    # The mcp library calls uvicorn internally and defaults to 127.0.0.1,
    # which makes the server unreachable on Railway. We patch uvicorn.config.Config
    # and uvicorn.server.Server so the host is always overridden to 0.0.0.0.
    try:
        import uvicorn.config
        import uvicorn.server

        _orig_config_init = uvicorn.config.Config.__init__
        def _patched_config_init(self, *args, **kwargs):
            if kwargs.get("host") in (None, "127.0.0.1"):
                kwargs["host"] = "0.0.0.0"
            if not kwargs.get("port") and port:
                kwargs["port"] = port
            return _orig_config_init(self, *args, **kwargs)
        uvicorn.config.Config.__init__ = _patched_config_init

        _orig_server_init = uvicorn.server.Server.__init__
        def _patched_server_init(self, config, *args, **kwargs):
            if hasattr(config, "host") and config.host in (None, "127.0.0.1"):
                config.host = "0.0.0.0"
            return _orig_server_init(self, config, *args, **kwargs)
        uvicorn.server.Server.__init__ = _patched_server_init

        print("[patch] uvicorn patched to bind 0.0.0.0")
    except Exception as e:
        print(f"[patch] uvicorn patch failed: {e}")

    # --- Start the server ---
    try:
        app.run(transport=transport, host=host, port=port)
        return
    except TypeError:
        pass
    # Fallback: rely on uvicorn patch above to pick up host/port
    app.run(transport=transport)


if __name__ == "__main__":
    main()
