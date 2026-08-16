from typing import Any, Dict, List


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def _get_value(obj: Any, key: str, default=None):
    """
    Safely get a value from either an object or dictionary.
    """

    if isinstance(obj, dict):
        return obj.get(key, default)

    return getattr(
        obj,
        key,
        default
    )


def _component_key(component: Any) -> str:
    """
    Get a stable component identifier.
    """

    component_id = _get_value(
        component,
        "id",
        None
    )

    if component_id:
        return str(component_id)

    return str(
        _get_value(
            component,
            "name",
            "unknown"
        )
    )


def _component_name(component: Any) -> str:
    """
    Get component display name.
    """

    return str(
        _get_value(
            component,
            "name",
            _component_key(component)
        )
    )


def _relationship_key(
    relationship: Any
):
    """
    Convert a relationship into a comparable tuple.
    """

    source = str(
        _get_value(
            relationship,
            "source",
            ""
        )
    )

    target = str(
        _get_value(
            relationship,
            "target",
            ""
        )
    )

    relationship_type = str(
        _get_value(
            relationship,
            "type",
            "depends_on"
        )
    )

    return (
        source,
        target,
        relationship_type
    )


# ============================================================
# COMPONENT DIFF
# ============================================================

def compare_components(
    old_components: List[Any],
    new_components: List[Any]
) -> Dict[str, Any]:
    """
    Compare components between two architecture snapshots.
    """

    old_map = {
        _component_key(component): component
        for component in old_components
    }

    new_map = {
        _component_key(component): component
        for component in new_components
    }

    old_ids = set(
        old_map.keys()
    )

    new_ids = set(
        new_map.keys()
    )

    added_ids = new_ids - old_ids
    removed_ids = old_ids - new_ids

    common_ids = old_ids & new_ids

    added_components = [
        _component_name(
            new_map[component_id]
        )
        for component_id in sorted(
            added_ids
        )
    ]

    removed_components = [
        _component_name(
            old_map[component_id]
        )
        for component_id in sorted(
            removed_ids
        )
    ]

    changed_layers = []

    for component_id in sorted(
        common_ids
    ):

        old_component = old_map[
            component_id
        ]

        new_component = new_map[
            component_id
        ]

        old_layer = _get_value(
            old_component,
            "layer",
            "unknown"
        )

        new_layer = _get_value(
            new_component,
            "layer",
            "unknown"
        )

        if old_layer != new_layer:

            changed_layers.append(
                {
                    "component":
                        _component_name(
                            new_component
                        ),

                    "component_id":
                        component_id,

                    "old_layer":
                        old_layer,

                    "new_layer":
                        new_layer
                }
            )

    return {
        "added_components":
            added_components,

        "removed_components":
            removed_components,

        "changed_layers":
            changed_layers
    }


# ============================================================
# RELATIONSHIP DIFF
# ============================================================

def compare_relationships(
    old_relationships: List[Any],
    new_relationships: List[Any]
) -> Dict[str, Any]:
    """
    Compare architecture relationships between snapshots.
    """

    old_map = {
        _relationship_key(
            relationship
        ): relationship

        for relationship
        in old_relationships
    }

    new_map = {
        _relationship_key(
            relationship
        ): relationship

        for relationship
        in new_relationships
    }

    old_keys = set(
        old_map.keys()
    )

    new_keys = set(
        new_map.keys()
    )

    added_keys = (
        new_keys - old_keys
    )

    removed_keys = (
        old_keys - new_keys
    )

    added_relationships = [
        {
            "source":
                key[0],

            "target":
                key[1],

            "type":
                key[2]
        }

        for key in sorted(
            added_keys
        )
    ]

    removed_relationships = [
        {
            "source":
                key[0],

            "target":
                key[1],

            "type":
                key[2]
        }

        for key in sorted(
            removed_keys
        )
    ]

    return {
        "added_relationships":
            added_relationships,

        "removed_relationships":
            removed_relationships
    }


# ============================================================
# METRIC DIFF
# ============================================================

def compare_metrics(
    old_metrics: Dict[str, Any],
    new_metrics: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Compare architecture metrics between snapshots.
    """

    old_metrics = (
        old_metrics
        or {}
    )

    new_metrics = (
        new_metrics
        or {}
    )

    changed_metrics = []

    all_keys = (
        set(old_metrics.keys())
        |
        set(new_metrics.keys())
    )

    for key in sorted(
        all_keys
    ):

        old_value = old_metrics.get(
            key
        )

        new_value = new_metrics.get(
            key
        )

        if isinstance(
            old_value,
            dict
        ) or isinstance(
            new_value,
            dict
        ):

            if old_value != new_value:

                changed_metrics.append(
                    {
                        "metric":
                            key,

                        "old_value":
                            old_value,

                        "new_value":
                            new_value
                    }
                )

            continue

        if old_value != new_value:

            changed_metrics.append(
                {
                    "metric":
                        key,

                    "old_value":
                        old_value,

                    "new_value":
                        new_value
                }
            )

    return {
        "changed_metrics":
            changed_metrics
    }


# ============================================================
# ARCHITECTURE CHANGE SCORE
# ============================================================

def calculate_change_score(
    summary: Dict[str, int]
) -> Dict[str, Any]:
    """
    Calculate an architecture change score from 0 to 100.

    The score represents the magnitude of architectural change.

    Weighting:

        Components      -> 30 points
        Relationships   -> 30 points
        Layer changes   -> 20 points
        Metrics          -> 20 points
    """

    components_changed = (
        summary.get(
            "components_added",
            0
        )
        +
        summary.get(
            "components_removed",
            0
        )
    )

    relationships_changed = (
        summary.get(
            "relationships_added",
            0
        )
        +
        summary.get(
            "relationships_removed",
            0
        )
    )

    layers_changed = summary.get(
        "layers_changed",
        0
    )

    metrics_changed = summary.get(
        "metrics_changed",
        0
    )

    # --------------------------------------------------------
    # Normalize each category.
    #
    # One or more changes in a category contributes toward
    # that category's maximum weight.
    # --------------------------------------------------------

    component_score = min(
        components_changed * 10,
        30
    )

    relationship_score = min(
        relationships_changed * 10,
        30
    )

    layer_score = min(
        layers_changed * 10,
        20
    )

    metric_score = min(
        metrics_changed * 5,
        20
    )

    total_score = (
        component_score
        +
        relationship_score
        +
        layer_score
        +
        metric_score
    )

    total_score = min(
        total_score,
        100
    )

    # --------------------------------------------------------
    # Change classification
    # --------------------------------------------------------

    if total_score == 0:

        change_level = "No Change"

    elif total_score <= 20:

        change_level = "Minimal"

    elif total_score <= 50:

        change_level = "Moderate"

    elif total_score <= 75:

        change_level = "Significant"

    else:

        change_level = "Major"

    return {
        "score": total_score,

        "level": change_level,

        "breakdown": {
            "components": component_score,
            "relationships": relationship_score,
            "layers": layer_score,
            "metrics": metric_score
        }
    }


# ============================================================
# COMPLETE ARCHITECTURE DIFF
# ============================================================

def compare_architectures(
    old_snapshot: Any,
    new_snapshot: Any
) -> Dict[str, Any]:
    """
    Compare two ArchitectureSnapshot objects.

    This is the main Architecture Time Machine diff engine.

    Returns:

        added components
        removed components
        added relationships
        removed relationships
        changed layers
        changed metrics
        architecture change score
        architecture change level
        score breakdown
    """

    old_components = _get_value(
        old_snapshot,
        "components",
        []
    )

    new_components = _get_value(
        new_snapshot,
        "components",
        []
    )

    old_relationships = _get_value(
        old_snapshot,
        "relationships",
        []
    )

    new_relationships = _get_value(
        new_snapshot,
        "relationships",
        []
    )

    old_metrics = _get_value(
        old_snapshot,
        "metrics",
        {}
    )

    new_metrics = _get_value(
        new_snapshot,
        "metrics",
        {}
    )

    component_diff = compare_components(
        old_components,
        new_components
    )

    relationship_diff = compare_relationships(
        old_relationships,
        new_relationships
    )

    metric_diff = compare_metrics(
        old_metrics,
        new_metrics
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    summary = {

        "components_added":
            len(
                component_diff[
                    "added_components"
                ]
            ),

        "components_removed":
            len(
                component_diff[
                    "removed_components"
                ]
            ),

        "relationships_added":
            len(
                relationship_diff[
                    "added_relationships"
                ]
            ),

        "relationships_removed":
            len(
                relationship_diff[
                    "removed_relationships"
                ]
            ),

        "layers_changed":
            len(
                component_diff[
                    "changed_layers"
                ]
            ),

        "metrics_changed":
            len(
                metric_diff[
                    "changed_metrics"
                ]
            )
    }

    # --------------------------------------------------------
    # Architecture Change Score
    # --------------------------------------------------------

    change_analysis = calculate_change_score(
        summary
    )

    # --------------------------------------------------------
    # Overall architecture status
    # --------------------------------------------------------

    architecture_changed = any(
        value > 0
        for value in summary.values()
    )

    return {

        "old_commit":
            _get_value(
                old_snapshot,
                "commit_hash",
                "unknown"
            ),

        "new_commit":
            _get_value(
                new_snapshot,
                "commit_hash",
                "unknown"
            ),

        "added_components":
            component_diff[
                "added_components"
            ],

        "removed_components":
            component_diff[
                "removed_components"
            ],

        "added_relationships":
            relationship_diff[
                "added_relationships"
            ],

        "removed_relationships":
            relationship_diff[
                "removed_relationships"
            ],

        "changed_layers":
            component_diff[
                "changed_layers"
            ],

        "changed_metrics":
            metric_diff[
                "changed_metrics"
            ],

        "summary":
            summary,

        "architecture_changed":
            architecture_changed,

        # ----------------------------------------------------
        # NEW: ARCHITECTURE CHANGE SCORE
        # ----------------------------------------------------

        "change_score":
            change_analysis[
                "score"
            ],

        "change_level":
            change_analysis[
                "level"
            ],

        "change_score_breakdown":
            change_analysis[
                "breakdown"
            ]
    }