"""Shared platform setup helpers.

The five HA entity platforms in this integration all walk the same
``jablotron_instance.entities[<EntityType>]`` map and add any entities
that have not yet been added. This helper encapsulates that pattern so
each platform file shrinks to one call.
"""

from __future__ import annotations

from typing import Callable, Iterable

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import JablotronConfigEntry
from .const import EntityType


def setup_entity_platform(
    hass: HomeAssistant,
    config_entry: JablotronConfigEntry,
    async_add_entities: AddEntitiesCallback,
    entity_types: Iterable[EntityType],
    entity_factory: Callable[["object", "object", EntityType], "object"],
) -> None:
    """Wire up add-on-add-discovery for the given entity types.

    ``entity_factory(jablotron_instance, control, entity_type)`` builds the
    HA entity for one Jablotron control. The first call runs the discovery
    immediately; subsequent dispatcher signals re-run it for newly created
    controls.
    """

    jablotron_instance = config_entry.runtime_data

    @callback
    def add_entities() -> None:
        new_entities = []
        for entity_type in entity_types:
            for control in jablotron_instance.entities[entity_type].values():
                if control.id in jablotron_instance.hass_entities:
                    continue
                new_entities.append(entity_factory(jablotron_instance, control, entity_type))
        if new_entities:
            async_add_entities(new_entities)

    add_entities()

    config_entry.async_on_unload(
        async_dispatcher_connect(hass, jablotron_instance.signal_entities_added(), add_entities)
    )
