"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

AUTOGENERATED BY glean_parser v11.0.1 for javascript_server.
Converted to Python manually.
TODO MPP-3642: Add python_server format to glean_parser.
"""

from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4
import json
import logging

GLEAN_EVENT_MOZLOG_TYPE = "glean-server-event"

_logger = logging.getLogger("glean")


class EventsServerEventLogger:
    def __init__(
        self, application_id: str, app_display_version: str, channel: str
    ) -> None:
        """
        Create EventsServerEventLogger instance.

        :param str application_id: The application ID.
        :param str app_display_version: The application display version.
        :param str channel: The channel.
        """
        self._application_id = application_id
        self._app_display_version = app_display_version
        self._channel = channel

    def record(self, user_agent: str, ip_address: str, event: dict[str, Any]) -> None:
        now = datetime.now(timezone.utc)
        timestamp = now.isoformat()
        event["timestamp"] = int(1000.0 * now.timestamp())  # Milliseconds since epoch
        event_payload = {
            "metrics": {},
            "events": [event],
            "ping_info": {
                # seq is required, however doesn't seem to be useful in server context
                "seq": 0,
                "start_time": timestamp,
                "end_time": timestamp,
            },
            # `Unknown` fields below are required in the Glean schema, however they are
            # not useful in server context
            "client_info": {
                "telemetry_sdk_build": "glean_parser v11.0.1",
                "first_run_date": "Unknown",
                "os": "Unknown",
                "os_version": "Unknown",
                "architecture": "Unknown",
                "app_build": "Unknown",
                "app_display_version": self._app_display_version,
                "app_channel": self._channel,
            },
        }
        event_payload_serialized = json.dumps(event_payload)

        # This is the message structure that Decoder expects:
        # https://github.com/mozilla/gcp-ingestion/pull/2400
        ping = {
            "document_namespace": self._application_id,
            "document_type": "events",
            "document_version": "1",
            "document_id": str(uuid4()),
            "user_agent": user_agent,
            "ip_address": ip_address,
            "payload": event_payload_serialized,
        }

        # this is similar to how FxA currently logs with mozlog:
        # https://github.com/mozilla/fxa/blob/4c5c702a7fcbf6f8c6b1f175e9172cdd21471eac/packages/fxa-auth-server/lib/log.js#L289
        _logger.info(GLEAN_EVENT_MOZLOG_TYPE, extra=ping)

    def record_email_generate_mask(
        self,
        user_agent: str,
        ip_address: str,
        mozilla_accounts_id: str,
        is_random_mask: bool,
        created_by_api: bool,
        has_generated_for: bool,
    ) -> None:
        """
        Record and submit a email_generate_mask event:
        An email mask is generated.
        Event is logged using internal mozlog logger.

        :param str user_agent: The user agent.
        :param str ip_address: The IP address. Will be used to decode Geo information
            and scrubbed at ingestion.
        :param str mozilla_accounts_id: Mozilla accounts user ID..
        :param bool is_random_mask: The mask is a random mask, instead of a domain mask.
        :param bool created_by_api: The mask was created via the API, rather than an
            incoming email.
        :param bool has_generated_for: The "generated_for" field was set by the Add-on
            or integration.
        """
        event = {
            "category": "email",
            "name": "generate_mask",
            "extra": {
                "mozilla_accounts_id": mozilla_accounts_id,
                "is_random_mask": is_random_mask,
                "created_by_api": created_by_api,
                "has_generated_for": has_generated_for,
            },
        }
        self.record(user_agent, ip_address, event)


def create_events_server_event_logger(
    application_id: str,
    app_display_version: str,
    channel: str,
) -> EventsServerEventLogger:
    """
    Factory function that creates an instance of Glean Server Event Logger to record
    `events` ping events.
    :param str application_id: The application ID.
    :param str app_display_version: The application display version.
    :param str channel: The channel.
    :return: An instance of EventsServerEventLogger.
    :rtype: EventsServerEventLogger
    """
    return EventsServerEventLogger(application_id, app_display_version, channel)
